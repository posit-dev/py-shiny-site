.DEFAULT_GOAL := help

VENV ?= .venv
PYBIN ?= $(VENV)/bin
PYTHON_VERSION ?= 3.12
PIP3 ?= pip3

QUARTO_VERSION ?= 1.7.23
QUARTO_PATH ?= ~/.local/share/qvm/versions/v${QUARTO_VERSION}/bin/quarto

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

## Build website
.PHONY: site
site: $(PYBIN) install-quarto
	. $(PYBIN)/activate && ${QUARTO_PATH} render

## Build website and serve
.PHONY: serve
serve: $(PYBIN) install-quarto
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


# Install build dependencies
deps: $(PYBIN)
	uv pip install -r requirements.txt
	. $(PYBIN)/activate && cd py-shiny && make ci-install-docs


## Build qmd files for Shiny API docs
quartodoc: $(PYBIN) deps install-quarto quarto-extensions
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

## Remove all build files (Quarto website, quarto extensions, venv)
.PHONY: distclean
distclean: clean clean-extensions clean-venv





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
