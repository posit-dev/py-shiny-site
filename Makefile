.DEFAULT_GOAL := help

VENV ?= .venv
PYBIN ?= $(VENV)/bin
PYTHON_VERSION ?= 3.12
PIP3 ?= pip3

QUARTO_VERSION ?= 1.7.23
QUARTO_PATH ?= ~/.local/share/qvm/versions/v${QUARTO_VERSION}/bin/quarto

SHINYLIVE_VERSION ?= 0.8.5

# Any targets that depend on $(VENV) or $(PYBIN) will cause the venv to be
# created using uv (much faster than standard venv). To use the venv, python
# scripts should run with the prefix $(PYBIN), as in `$(PYBIN)/python`.
$(VENV):
	$(MAKE) install-uv
	uv venv --python $(PYTHON_VERSION)

$(PYBIN): $(VENV)


## Build assets and render site
.PHONY: all
all: quartodoc components site

## Build assets and render site using develop branch shinylive
.PHONY: all-dev
all-dev: deps-dev quartodoc components site

## Build website
.PHONY: site
site: $(PYBIN) install-quarto
	. $(PYBIN)/activate && ${QUARTO_PATH} render

## Build website and serve
.PHONY: serve
serve: $(PYBIN) install-quarto
	. $(PYBIN)/activate && ${QUARTO_PATH} preview

## Build website and serve using develop branch shinylive
.PHONY: serve-dev
serve-dev: deps-dev install-quarto
	. $(PYBIN)/activate && ${QUARTO_PATH} preview


## Install uv if not already installed
.PHONY: install-uv
install-uv:
	@if command -v uv > /dev/null 2>&1; then \
		exit 0; \
	else \
		echo "🔵 Installing uv from pip..."; \
		curl -LsSf https://astral.sh/uv/install.sh | sh; \
		echo "✓ uv installed successfully"; \
	fi


.PHONY: install-quarto
install-quarto:
	# In CI environments, assume quarto is pre-installed
	@if [ "$(CI)" = "true" ]; then \
		echo "🔍 CI environment detected, checking for quarto..."; \
		if command -v quarto > /dev/null 2>&1; then \
			echo "✓ quarto is available"; \
		else \
			echo "❌ Error: quarto is not available in CI environment" >&2; \
			exit 1; \
		fi; \
	else \
		echo "🔵 Installing quarto"; \
		if ! command -v qvm > /dev/null 2>&1; then \
			if command -v brew > /dev/null 2>&1; then \
				echo "🔹 Installing qvm via Homebrew"; \
				brew install dpastoor/tap/qvm; \
			else \
				echo "❌ Error: qvm is not installed. Please visit https://github.com/dpastoor/qvm/releases/ to install it." >&2; \
				exit 1; \
			fi; \
		fi; \
		qvm install v${QUARTO_VERSION}; \
		echo "🔹 Updating .vscode/settings.json"; \
		awk -v path="${QUARTO_PATH}" '/"quarto.path":/ {gsub(/"quarto.path": ".*"/, "\"quarto.path\": \"" path "\"")} 1' .vscode/settings.json > .vscode/settings.json.tmp && mv .vscode/settings.json.tmp .vscode/settings.json; \
		echo "🔹 Updating .github/workflows/deploy-docs.yml"; \
		awk -v ver="${QUARTO_VERSION}" '/QUARTO_VERSION:/ {gsub(/QUARTO_VERSION: .*/, "QUARTO_VERSION: " ver)} 1' .github/workflows/deploy-docs.yml > .github/workflows/deploy-docs.yml.tmp && mv .github/workflows/deploy-docs.yml.tmp .github/workflows/deploy-docs.yml; \
	fi

$(QUARTO_PATH): install-quarto

## Update git submodules to commits referenced in this repository
.PHONY: submodules
submodules:
	git submodule init
	git submodule update --depth=0

## Pull latest commits in git submodules
.PHONY: submodules-pull
submodules-pull:
	git submodule update --recursive --remote


_extensions/quarto-ext/shinylive: install-quarto
	${QUARTO_PATH} add --no-prompt quarto-ext/shinylive
_extensions/shafayetShafee/line-highlight: install-quarto
	${QUARTO_PATH} add --no-prompt shafayetShafee/line-highlight
_extensions/machow/quartodoc: install-quarto
	${QUARTO_PATH} add --no-prompt machow/quartodoc

## Update Quarto extensions
.PHONY: quarto-extensions
quarto-extensions: _extensions/quarto-ext/shinylive _extensions/shafayetShafee/line-highlight _extensions/machow/quartodoc


# Install build dependencies (using PyPI shinylive)
deps: $(PYBIN)
	uv pip install -r requirements.txt
	. $(PYBIN)/activate && cd py-shiny && make ci-install-docs

# Install build dependencies with develop branch shinylive
deps-dev: $(PYBIN)
	uv pip install -r requirements.txt
	. $(PYBIN)/activate && cd py-shiny && make ci-install-docs
	$(MAKE) build-shinylive


## Build qmd files for Shiny API docs
quartodoc: $(PYBIN) deps install-quarto
	. $(PYBIN)/activate && cd py-shiny/docs && make quartodoc
	# Copy all generated files except index.qmd
	rsync -av --exclude="index.qmd" py-shiny/docs/api/ ./api
	cp -R py-shiny/docs/_inv py-shiny/docs/objects.json ./
	# Copy over index.qmd, but rename it to _api_index.qmd
	cp py-shiny/docs/api/express/index.qmd ./api/express/_api_index.qmd
	cp py-shiny/docs/api/core/index.qmd ./api/core/_api_index.qmd
	cp py-shiny/docs/api/testing/index.qmd ./api/testing/_api_index.qmd


## Build component static previews and update shinylive links
.PHONY: components
components: components-shinylive-links components-static

.PHONY: components-static
components-static: $(PYBIN) deps
	rm -rf components/static
	. $(PYBIN)/activate && python components/make-static-previews.py

.PHONY: components-shinylive-links
components-shinylive-links: $(PYBIN) deps
	. $(PYBIN)/activate && python components/update-shinylive-links.py


SHINYLIVE_DIR ?= _shinylive-source

## Clone shinylive repository (for building from source)
.PHONY: clone-shinylive
clone-shinylive:
	@if [ ! -d "$(SHINYLIVE_DIR)" ]; then \
		echo "🔵 Cloning shinylive repository..."; \
		git clone https://github.com/posit-dev/shinylive.git $(SHINYLIVE_DIR); \
	else \
		echo "✓ shinylive directory already exists"; \
	fi

## Build shinylive from the develop branch for previewing unreleased features
# Note, the develop branch's submodules MUST be up-to-date for this to work correctly.
.PHONY: build-shinylive
build-shinylive: $(PYBIN) clean-shinylive clone-shinylive
	@echo "🔵 Checking out develop branch..."
	cd $(SHINYLIVE_DIR) && git checkout develop && git pull origin develop
	@echo "🔵 Updating submodules..."
	cd $(SHINYLIVE_DIR) && git submodule init
	cd $(SHINYLIVE_DIR) && git submodule update --recursive --remote
	cd $(SHINYLIVE_DIR)/packages/py-shiny && git fetch --tags || true
	@echo "🔵 Building shinylive assets from source..."
	cd $(SHINYLIVE_DIR) && npm install
	cd $(SHINYLIVE_DIR) && make all
	cd $(SHINYLIVE_DIR) && make dist
	@echo "🔵 Installing locally-built shinylive assets..."
	@ASSETS_VERSION=$$(cd $(SHINYLIVE_DIR) && node -p "require('./package.json').version"); \
	ASSETS_DIR=$$(. $(PYBIN)/activate && python -c "import appdirs; print(appdirs.user_cache_dir('shinylive'))"); \
	SHINYLIVE_ABS=$$(cd $(SHINYLIVE_DIR) && pwd); \
	if [ -z "$$ASSETS_VERSION" ] || [ -z "$$ASSETS_DIR" ] || [ -z "$$SHINYLIVE_ABS" ]; then \
		echo "❌ Error: Failed to determine version or paths"; \
		exit 1; \
	fi; \
	echo "🔹 Extracting assets version $${ASSETS_VERSION}"; \
	cd "$$SHINYLIVE_ABS" && tar -xzf dist/shinylive-$${ASSETS_VERSION}.tar.gz; \
	if [ ! -d "$$SHINYLIVE_ABS/shinylive-$${ASSETS_VERSION}" ]; then \
		echo "❌ Error: Extraction failed - directory not found"; \
		exit 1; \
	fi; \
	echo "🔹 Installing to $${ASSETS_DIR}/shinylive-$${ASSETS_VERSION}"; \
	mkdir -p "$${ASSETS_DIR}"; \
	rm -rf "$${ASSETS_DIR}/shinylive-$${ASSETS_VERSION}"; \
	mv "$$SHINYLIVE_ABS/shinylive-$${ASSETS_VERSION}" "$${ASSETS_DIR}/"; \
	if [ ! -d "$${ASSETS_DIR}/shinylive-$${ASSETS_VERSION}/shinylive" ]; then \
		echo "❌ Error: Assets installation failed - directory structure incomplete"; \
		exit 1; \
	fi; \
	echo "✓ Shinylive assets version $${ASSETS_VERSION} installed successfully"; \
	echo "  Assets location: $${ASSETS_DIR}/shinylive-$${ASSETS_VERSION}"

## Update shinylive source and rebuild
.PHONY: update-shinylive
update-shinylive: clone-shinylive
	@echo "🔵 Updating shinylive repository..."
	cd $(SHINYLIVE_DIR) && git pull
	$(MAKE) build-shinylive

## Clean shinylive build artifacts and cached assets
.PHONY: clean-shinylive
clean-shinylive:
	rm -rf $(SHINYLIVE_DIR)
	@if [ -n "$(PYBIN)" ] && [ -f "$(PYBIN)/python" ]; then \
		ASSETS_DIR=$$(. $(PYBIN)/activate && shinylive assets info 2>/dev/null | grep -A1 "Local cached" | tail -1 | tr -d ' '); \
		if [ -n "$$ASSETS_DIR" ] && [ -d "$$ASSETS_DIR" ]; then \
			echo "🔹 Removing all cached shinylive assets from $$ASSETS_DIR"; \
			rm -rf "$$ASSETS_DIR"/shinylive-*; \
		fi; \
	fi


## Remove Quarto website build files
.PHONY: clean
clean:
	rm -rf _build
	rm -rf components/static
	cd py-shiny/docs && make clean

.PHONY: clean-extensions
clean-extensions:
	rm -rf _extensions

.PHONY: clean-venv
clean-venv:
	rm -rf $(VENV)

## Remove all build files (Quarto website, quarto extensions, venv, shinylive)
.PHONY: distclean
distclean: clean clean-extensions clean-venv clean-shinylive





define PRINT_HELP_PYSCRIPT
import re, sys

prev_line_help = None
for line in sys.stdin:
	if line.strip().startswith(".PHONY"):
		continue
	if prev_line_help is None:
		match = re.match(r"^## (.*)", line)
		if match:
			prev_line_help = match.groups()[0]
		else:
			prev_line_help = None
	else:
		match = re.match(r'^([a-zA-Z_-]+)', line)
		if match:
			target = match.groups()[0]
			print("%-22s %s" % (target, prev_line_help))

		target = None
		prev_line_help = None

endef
export PRINT_HELP_PYSCRIPT

.PHONY: help
help:
	@python3 -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)
