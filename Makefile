.PHONY: help all preview build_pkgs \
	submodules submodules-pull \
	requirements \
	quarto-exts \
	site serve \
	components components-shinylive components-static \
	clean clean-extensions clean-venv distclean

.DEFAULT_GOAL := help

VENV = venv
PYBIN = $(VENV)/bin


## Build everything
all: deps quartodoc components-static site

# Any targets that depend on $(VENV) or $(PYBIN) will cause the venv to be
# created. To use the ven, python scripts should run with the prefix $(PYBIN),
# as in `$(PYBIN)/pip`.
$(VENV):
	python3 -m venv $(VENV)

$(PYBIN): $(VENV)


define PRINT_HELP_PYSCRIPT
import re, sys

prev_line_help = None
for line in sys.stdin:
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

help:
	@python3 -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

## Update git submodules to commits referenced in this repository
submodules:
	git submodule init
	git submodule update --depth=20

## Pull latest commits in git submodules
submodules-pull:
	git submodule update --recursive --remote

## Update Quarto extensions
quarto-exts:
	quarto add --no-prompt quarto-ext/shinylive
	quarto add --no-prompt shafayetShafee/line-highlight

## Install build dependencies
deps: $(PYBIN)
	$(PYBIN)/pip install pip --upgrade
	$(PYBIN)/pip install -r requirements.txt
	. $(PYBIN)/activate && cd py-shiny && make install-deps
	. $(PYBIN)/activate && cd py-shiny/docs && make deps

## Build qmd files for Shiny API docs
quartodoc: $(PYBIN)
	. $(PYBIN)/activate && cd py-shiny/docs && make quartodoc
	# Copy all generated files except index.qmd
	rsync -av --exclude="index.qmd" py-shiny/docs/api/ ./api
	cp -R py-shiny/docs/_inv py-shiny/docs/objects.json ./
	# Copy over index.qmd, but rename it to _api_index.qmd
	cp py-shiny/docs/api/express/index.qmd ./api/express/_api_index.qmd
	cp py-shiny/docs/api/core/index.qmd ./api/core/_api_index.qmd
	cp py-shiny/docs/api/testing/index.qmd ./api/testing/_api_index.qmd

## Build website
site: $(PYBIN)
	. $(PYBIN)/activate && quarto render

## Build website and serve
serve: $(PYBIN)
	. $(PYBIN)/activate && quarto preview

## Remove Quarto website build files
clean:
	rm -rf _build
	rm -rf components/static
	cd py-shiny/docs && make clean

## Remove Quarto extensions
clean-exts:
	rm -rf _extensions

## Remove venv files
clean-venv:
	rm -rf $(VENV)

## Remove all build files (Quarto website, quarto extensions, venv)
distclean: clean clean-extensions clean-venv

components-static:
	rm -rf components/static
	. $(PYBIN)/activate && python components/make-static-previews.py

components-shinylive-links:
	. $(PYBIN)/activate && python components/update-shinylive-links.py

## Build component static previews and update shinylive links
components: components-shinylive-links components-static
