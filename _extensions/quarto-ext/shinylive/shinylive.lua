-- Notes:
-- * 2023/10/04 - Barret:
--   Always use `callShinyLive()` to call a shinylive extension.
--   `callPythonShinyLive()` and `callRShinyLive()` should not be used directly.
--   Instead, always use `callShinyLive()`.
-- * 2023/10/04 - Barret:
--   I could not get `error(msg)` to quit the current function execution and
--   bubble up the stack and stop. Instead, I am using `assert(false, msg)` to
--   achieve the desired behavior. Multi-line error messages should start with a
--   `\n` to keep the message in the same readable area.


-- `table` to organize flags to have code only run once.
local hasDoneSetup = { base = false, r = false, python = false, python_version = false }
-- `table` to store `{ version, assets_version }` for each language's extension.
-- If both `r` and `python` are used in the same document, then the
-- `assets_version` for each language must be the same.
local versions = { r = nil, python = nil }
-- Global variable for the codeblock-to-json.js script file location
local codeblockScript = nil
-- Global hash table to store app specific dependencies to avoid calling
-- `quarto.doc.attach_to_dependency()` multiple times for the same dependency.
local appSpecificDeps = {}

-- Display error message and throw error w/ short message
-- @param msg: string Error message to be displayed
-- @param short_msg: string Error message to be thrown
function throw_quarto_error(err_msg, ...)
  n = select("#", ...)
  if n > 0 then
    -- Display any meta information about the error
    -- Add blank lines after msg for line separation for better readability
    quarto.log.error(...)
  else
    quarto.log.error(err_msg .. "\n\n")
  end
  -- Add blank lines after short_msg for line separation for better readability
  -- Use assert(false, msg) to quit the current function execution and
  -- bubble up the stack and stop. Barret: I could not get this to work with `error(msg)`.
  assert(false, err_msg .. "\n")
end

-- ===== Shinylive subprocess result cache (py-shiny-site patch) ===============
-- Memoizes subprocess results to disk so they are shared across documents
-- within a `quarto render` of the site. Without this, every document pays
-- several seconds of identical subprocess startup cost (version check, info,
-- base-htmldeps, language-resources), which dominates full-site render time.
-- Maintained as scripts/patches/shinylive-cache.patch; `make quarto-extensions`
-- re-applies it after re-downloading the extension.
-- The cache is strictly an optimization: on any cache failure, the real
-- subprocess is run.

local pipeCacheState = nil -- nil = uninitialized, false = disabled, table = ready

local function initPipeCache()
  if pipeCacheState ~= nil then
    return pipeCacheState
  end
  local ok, result = pcall(function()
    local projDir = quarto.project.directory or os.getenv("QUARTO_PROJECT_DIR")
    if projDir == nil then
      return false
    end
    projDir = tostring(projDir)
    local dir = projDir .. "/.quarto/shinylive-cache"
    pandoc.system.make_directory(dir, true)
    -- Include requirements.txt in every cache key: bumping the pinned
    -- shinylive version invalidates the whole cache. Include the quarto
    -- version too: the codeblock-to-json call runs through the quarto CLI,
    -- so its output can change when quarto is upgraded.
    local keySuffix = "quarto-" .. tostring(quarto.version)
    local reqFile = io.open(projDir .. "/requirements.txt", "r")
    if reqFile then
      keySuffix = keySuffix .. "\1" .. pandoc.utils.sha1(reqFile:read("*a"))
      reqFile:close()
    end
    return { dir = dir, keySuffix = keySuffix }
  end)
  if ok and result then
    pipeCacheState = result
  else
    pipeCacheState = false
  end
  return pipeCacheState
end

local function pipeCacheKey(cache, command, args, input)
  return pandoc.utils.sha1(
    command .. "\1" .. table.concat(args, "\1") .. "\1" .. input .. "\1" .. cache.keySuffix
  )
end

local function pipeCacheRead(cache, key)
  local f = io.open(cache.dir .. "/" .. key, "rb")
  if f == nil then
    return nil
  end
  local contents = f:read("*a")
  f:close()
  return contents
end

-- Some subprocess results embed absolute paths to files elsewhere on disk,
-- and running the subprocess is what creates those files: notably
-- `extension base-htmldeps` downloads the shinylive web assets to the user
-- cache dir as a side effect. Only serve a hit whose referenced files all
-- still exist; otherwise re-run the subprocess so it can re-create them.
-- (Matches POSIX absolute paths in "source"/"path" JSON fields; on Windows
-- nothing matches, so hits are served unvalidated — same as no check.)
local function pipeCacheHitUsable(hit)
  for _, field in ipairs({ "source", "path" }) do
    for path in hit:gmatch('"' .. field .. '":%s*"(/[^"]+)"') do
      local f = io.open(path, "r")
      if f == nil then
        return false
      end
      f:close()
    end
  end
  return true
end

local function pipeCacheWrite(cache, key, value)
  -- Write to a temp file then rename: atomic on POSIX, so a concurrent
  -- render (e.g. quarto preview) can never observe a partial entry.
  local path = cache.dir .. "/" .. key
  local tmpPath = path .. ".tmp" .. tostring(math.random(1000000000))
  local f = io.open(tmpPath, "wb")
  if f == nil then
    return
  end
  f:write(value)
  f:close()
  os.rename(tmpPath, path)
end

-- Drop-in replacement for `pandoc.pipe()` that memoizes successful results
-- to disk. Failed subprocess calls are never cached (pandoc.pipe raises, so
-- the error propagates to the caller exactly as before).
local pipeMemo = {} -- in-process memo: repeat calls skip hashing and disk I/O

local function cachedPipe(command, args, input)
  local cache = initPipeCache()
  if cache == false then
    return pandoc.pipe(command, args, input)
  end

  local keyOk, key = pcall(pipeCacheKey, cache, command, args, input)
  if not keyOk then
    return pandoc.pipe(command, args, input)
  end

  if pipeMemo[key] ~= nil then
    return pipeMemo[key]
  end

  local hitOk, hit = pcall(pipeCacheRead, cache, key)
  if hitOk and hit ~= nil then
    local usableOk, usable = pcall(pipeCacheHitUsable, hit)
    if usableOk and usable then
      pipeMemo[key] = hit
      return hit
    end
  end

  local res = pandoc.pipe(command, args, input)
  pipeMemo[key] = res
  pcall(pipeCacheWrite, cache, key, res)
  return res
end
-- ===== End shinylive subprocess result cache =================================

-- Python specific method to call py-shinylive
-- @param args: list of string arguments to pass to py-shinylive
-- @param input: string to pipe into to py-shinylive
function callPythonShinylive(args, input)
  -- Try calling `pandoc.pipe('shinylive', ...)` and if it fails, print a message
  -- about installing shinylive python package.
  local res
  local status, err = pcall(
    function()
      res = cachedPipe("shinylive", args, input)
    end
  )

  if not status then
    throw_quarto_error(
      "Error running 'shinylive' command. Perhaps you need to install / update the 'shinylive' Python package?",
      "Error running 'shinylive' command. Perhaps you need to install / update the 'shinylive' Python package?\n",
      "Error:\n",
      err
    )
  end

  return res
end

-- R specific method to call {r-shinylive}
-- @param args: list of string arguments to pass to r-shinylive
-- @param input: string to pipe into to r-shinylive
function callRShinylive(args, input)
  args = { "-e",
    "shinylive:::quarto_ext()",
    table.unpack(args) }

  -- Try calling `pandoc.pipe('Rscript', ...)` and if it fails, print a message
  -- about installing shinylive R package.
  local res
  local status, err = pcall(
    function()
      res = cachedPipe("Rscript", args, input)
    end
  )

  if not status then
    throw_quarto_error(
      "Error running 'Rscript' command. Perhaps you need to install / update the 'shinylive' R package?",
      "Error running 'Rscript' command. Perhaps you need to install / update the 'shinylive' R package?\n",
      "Error:\n",
      err
    )
  end

  return res
end

-- Returns decoded object
-- @param language: "python" or "r"
-- @param args, input: see `callPythonShinylive` and `callRShinylive`
function callShinylive(language, args, input, parseJson)
  if input == nil then
    input = ""
  end
  if parseJson == nil then
    parseJson = true
  end

  local res
  -- print("Calling " .. language .. " shinylive with args: ", args)
  if language == "python" then
    res = callPythonShinylive(args, input)
  elseif language == "r" then
    res = callRShinylive(args, input)
  else
    throw_quarto_error("internal - Unknown language: " .. language)
  end

  if not parseJson then
    return res
  end

  -- Remove any unwanted output before the first curly brace or square bracket.
  -- print("res: " .. string.sub(res, 1, math.min(string.len(res), 100)) .. "...")
  local curly_start = string.find(res, "{", 0, true)
  local brace_start = string.find(res, "[", 0, true)
  local min_start
  if curly_start == nil then
    min_start = brace_start
  elseif brace_start == nil then
    min_start = curly_start
  else
    min_start = math.min(curly_start, brace_start)
  end
  if min_start == nil then
    local res_str = res
    if string.len(res) > 100 then
      res_str = string.sub(res, 1, 100) .. "... [truncated]"
    end
    throw_quarto_error(
      "Could not find start curly brace or start brace in " ..
      language .. " shinylive response. Is JSON being returned from the " .. language .. " `shinylive` package?",
      "Could not find start curly brace or start brace in " .. language .. " shinylive response.\n",
      "JSON string being parsed:\n",
      res_str
    )
  end
  if min_start > 1 then
    res = string.sub(res, min_start)
  end


  -- Decode JSON object
  local result
  local status, err = pcall(
    function()
      result = quarto.json.decode(res)
    end
  )
  if not status then
    throw_quarto_error(
      "Error decoding JSON response from `shinylive` " .. language .. " package.",
      "Error decoding JSON response from `shinylive` " .. language .. " package.\n",
      "JSON string being parsed:\n",
      res,
      "Error:\n",
      err
    )
  end
  return result
end

function parseVersion(versionTxt)
  local versionParts = {}
  for part in string.gmatch(versionTxt, "%d+") do
    table.insert(versionParts, tonumber(part))
  end
  local ret = {
    major = nil,
    minor = nil,
    patch = nil,
    extra = nil,
    length = #versionParts,
    str = versionTxt
  }

  if ret.length >= 1 then
    ret.major = versionParts[1]
    if ret.length >= 2 then
      ret.minor = versionParts[2]
      if ret.length >= 3 then
        ret.patch = versionParts[3]
        if ret.length >= 4 then
          ret.extra = versionParts[4]
        end
      end
    end
  end

  return ret
end

-- If verA > verB, return 1
-- If verA == verB, return 0
-- If verA < verB, return -1
function compareVersions(verA, verB)
  if verA.major == nil or verB.major == nil then
    throw_quarto_error("Trying to compare an invalid version: " .. verA.str .. " or " .. verB.str)
  end

  for index, key in ipairs({ "major", "minor", "patch", "extra" }) do
    local partDiff = compareVersionPart(verA[key], verB[key])
    if partDiff ~= 0 then
      return partDiff
    end
  end

  -- Equal!
  return 0
end

function compareVersionPart(aPart, bPart)
  if aPart == nil and bPart == nil then
    return 0
  end
  if aPart == nil then
    return -1
  end
  if bPart == nil then
    return 1
  end
  if aPart > bPart then
    return 1
  elseif aPart < bPart then
    return -1
  end

  -- Equal!
  return 0
end

function ensurePyshinyliveVersion(language)
  -- Quit early if not python
  if language ~= "python" then
    return
  end
  -- Quit early if already completed check
  if hasDoneSetup.python_version then
    return
  end
  hasDoneSetup.python_version = true

  -- Verify that min python shinylive version is met
  pyShinyliveVersion = callShinylive(language, { "--version" }, "", false)
  -- Remove trailing whitespace
  pyShinyliveVersion = pyShinyliveVersion:gsub("%s+$", "")
  -- Parse version into table
  parsedVersion = parseVersion(pyShinyliveVersion)

  -- Verify that the version is at least 0.1.0
  if
      (parsedVersion.length < 3) or
      -- Major and minor values are 0. Ex: 0.0.18
      (parsedVersion.major == 0 and parsedVersion.minor == 0)
  then
    assert(false,
      "\nThe shinylive Python package must be at least version v0.1.0 to be used in a Quarto document." ..
      "\n\nInstalled Python Shinylive package version: " .. pyShinyliveVersion ..
      "\n\nPlease upgrade the Python Shinylive package by running:" ..
      "\n\tpip install --upgrade shinylive" ..
      "\n\n(If you are using a virtual environment, please activate it before running the command above.)"
    )
  end
end

-- Do one-time setup for language agnostic html dependencies.
-- This should only be called once per document
-- @param language: "python" or "r"
function ensureBaseSetup(language)
  -- Quit early if already done
  if hasDoneSetup.base then
    return
  end
  hasDoneSetup.base = true

  -- Find the path to codeblock-to-json.ts and save it for later use.
  local infoObj = callShinylive(language, { "extension", "info" })
  -- Store the path to codeblock-to-json.ts for later use
  codeblockScript = infoObj.scripts['codeblock-to-json']
  -- Store the version info for later use
  versions[language] = { version = infoObj.version, assets_version = infoObj.assets_version }

  -- Add language-agnostic dependencies
  local baseDeps = getShinyliveBaseDeps(language)
  for idx, dep in ipairs(baseDeps) do
    quarto.doc.add_html_dependency(dep)
  end

  -- Add ext css dependency
  quarto.doc.add_html_dependency(
    {
      name = "shinylive-quarto-css",
      stylesheets = { "resources/css/shinylive-quarto.css" }
    }
  )
end

-- Do one-time setup for language specific html dependencies.
-- This should only be called once per document
-- @param language: "python" or "r"
function ensureLanguageSetup(language)
  -- Min version check must be done first
  ensurePyshinyliveVersion(language)

  -- Make sure the base setup is done before the langage setup
  ensureBaseSetup(language)

  if hasDoneSetup[language] then
    return
  end
  hasDoneSetup[language] = true

  -- Only get the asset version value if it hasn't been retrieved yet.
  if versions[language] == nil then
    local infoObj = callShinylive(language, { "extension", "info" })
    versions[language] = { version = infoObj.version, assets_version = infoObj.assets_version }
  end
  -- Verify that the r-shinylive and py-shinylive supported assets versions match
  if
      (versions.r and versions.python) and
      ---@diagnostic disable-next-line: undefined-field
      versions.r.assets_version ~= versions.python.assets_version
  then
    local parsedRAssetsVersion = parseVersion(versions.r.assets_version)
    local parsedPythonAssetsVersion = parseVersion(versions.python.assets_version)

    local verDiff = compareVersions(parsedRAssetsVersion, parsedPythonAssetsVersion)
    local verDiffStr = ""
    if verDiff == 1 then
      -- R shinylive supports higher version of assets. Upgrade python shinylive
      verDiffStr =
          "The currently installed python shinylive package supports a lower assets version, " ..
          "therefore we recommend updating your python shinylive package to the latest version."
    elseif verDiff == -1 then
      -- Python shinylive supports higher version of assets. Upgrade R shinylive
      verDiffStr =
          "The currently installed R shinylive package supports a lower assets version, " ..
          "therefore we recommend updating your R shinylive package to the latest version."
    end

    throw_quarto_error(
      "The shinylive R and Python packages must support the same Shinylive Assets version to be used in the same Quarto document.",
      "The shinylive R and Python packages must support the same Shinylive Assets version to be used in the same Quarto document.\n",
      "\n",
      "Python shinylive package version: ",
      ---@diagnostic disable-next-line: undefined-field
      versions.python.version .. " ; Supported assets version: " .. versions.python.assets_version .. "\n",
      "R shinylive package version:       " ..
      ---@diagnostic disable-next-line: undefined-field
      versions.r.version .. " ; Supported assets version: " .. versions.r.assets_version .. "\n",
      "\n",
      verDiffStr .. "\n",
      "\n",
      "To update your R Shinylive package, run:\n",
      "\tR -e \"install.packages('shinylive')\"\n",
      "\n",
      "To update your Python Shinylive package, run:\n",
      "\tpip install --upgrade shinylive\n",
      "(If you are using a virtual environment, please activate it before running the command above.)\n",
      "\n"
    )
  end

  -- Add language-specific dependencies
  local langResources = callShinylive(language, { "extension", "language-resources" })
  for idx, resourceDep in ipairs(langResources) do
    -- No need to check for uniqueness.
    -- Each resource is only be added once and should already be unique.
    quarto.doc.attach_to_dependency("shinylive", resourceDep)
  end
end

function getShinyliveBaseDeps(language)
  -- Relative path from the current page to the root of the site. This is needed
  -- to find out where shinylive-sw.js is, relative to the current page.
  if quarto.project.offset == nil then
    throw_quarto_error("The `shinylive` extension must be used in a Quarto project directory (with a _quarto.yml file).")
  end
  local deps = callShinylive(
    language,
    { "extension", "base-htmldeps", "--sw-dir", quarto.project.offset },
    ""
  )
  return deps
end

-- Legacy quarto cli location
quarto_cli_path = "quarto"
if quarto.config ~= nil and quarto.config.cli_path ~= nil then
  -- * 2024/05/03 - Christophe:
  --   `quarto run` needs to be called using the same quarto CLI that called the extension.
  --   This is done by using `quarto.config.cli_path()` from Quarto 1.5 Lua API.
  --   https://github.com/quarto-dev/quarto-cli/pull/9576
  quarto_cli_path = quarto.config.cli_path()
end

return {
  {
    CodeBlock = function(el)
      if not el.attr then
        -- Not a shinylive codeblock, return
        return
      end

      local language
      if el.attr.classes:includes("{shinylive-r}") then
        language = "r"
      elseif el.attr.classes:includes("{shinylive-python}") then
        language = "python"
      else
        -- Not a shinylive codeblock, return
        return
      end
      -- Setup language and language-agnostic dependencies
      ensureLanguageSetup(language)

      -- Convert code block to JSON string in the same format as app.json.
      local parsedCodeblockJson = cachedPipe(
        quarto_cli_path,
        { "run", codeblockScript, language },
        el.text
      )

      -- This contains "files" and "quartoArgs" keys.
      local parsedCodeblock = quarto.json.decode(parsedCodeblockJson)

      -- Find Python package dependencies for the current app.
      local appDeps = callShinylive(
        language,
        { "extension", "app-resources" },
        -- Send as piped input to the shinylive command
        quarto.json.encode(parsedCodeblock["files"])
      )

      -- Add app specific dependencies
      for idx, dep in ipairs(appDeps) do
        if not appSpecificDeps[dep.name] then
          appSpecificDeps[dep.name] = true
          quarto.doc.attach_to_dependency("shinylive", dep)
        end
      end

      if el.attr.classes:includes("{shinylive-python}") then
        el.attributes.engine = "python"
        el.attr.classes = pandoc.List()
        el.attr.classes:insert("shinylive-python")
      elseif el.attr.classes:includes("{shinylive-r}") then
        el.attributes.engine = "r"
        el.attr.classes = pandoc.List()
        el.attr.classes:insert("shinylive-r")
      end
      
      el.text = 
        "#| '!! shinylive warning !!': |\n"..
        "#|   shinylive does not work in self-contained HTML documents.\n" .. 
        "#|   Please set `embed-resources: false` in your metadata.\n" ..
        el.text
      
      return el
    end
  }
}
