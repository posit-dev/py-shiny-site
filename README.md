This repository contains the sources for the Shiny for Python web site.

## Setup and build


**Prerequisites:** Make sure you have the following installed. (Note that if you have Nix installed on your system, you do not need to install these manually because Nix can provide them automatically.)

- Quarto 1.3.x
- Python
- R

Clone this repository:

```bash
git clone https://github.com/posit-dev/py-shiny-site.git
cd py-shiny-site
```

**Optional:** If you are using Nix, you can get a working development environment with all of the prerequisites by simply running `nix develop`. This will enter a shell with correct versions of the dependencies already installed.

```bash
# Optional, if you have Nix installed
nix develop
```

Set up git submodules:

```bash
make submodules
```

Build everything (see Notes below for information on individual steps, which can be run separately):

```bash
make all
```

Serve the website and watch for changes to the .qmd files:

```bash
make serve
```

Running `make` by itself will print out the available `make` targets:

```
$ make
all                    Build everything
submodules             Update git submodules to commits referenced in this repository
submodules-pull        Pull latest commits in git submodules
quarto-exts            Update Quarto extensions
deps                   Install build dependencies
quartodoc              Build qmd files for Shiny API docs
site                   Build website
serve                  Build website and serve
clean                  Remove Quarto website build files
clean-exts             Remove Quarto extensions
clean-venv             Remove venv files
distclean              Remove all build files (Quarto website, quarto extensions, venv)
```


## Notes

### Details of `make all`

The `make all` command runs the following steps. If you are iterating on the site, it will be more efficient to run these steps individually as needed.

Install Python packages needed for building the site:

```bash
make deps
```

Build qmd files for Shiny API docs. These will go in api/.

```bash
make quartodoc
```

Build the site:

```bash
make site
```

### Virtualenv

When running `make`, all of the Python scripts and commands run in a virtualenv. If you want to run commands at the terminal in the same virtualenv, you will need to do the following:

Set up virtualenv (this only needs to be done once, and is done automatically by `make all`):

```bash
make venv
```

After the virtualenv is created, activate it with:

```bash
source venv/bin/activate
```

This will make the virtualenv available when you run commands at the terminal.

Deactivate the virtualenv with:

```bash
deactivate
```

### Pulling changes

To pull the latest changes:

```bash
git pull
```

Update submodules. For example, if the upstream pyshiny-site points to a new commit in shinylive, this will update the local shinylive to that commit.

```bash
make submodules
```

Install dependencies and build the site:

```bash
make all
```

In some cases, you may need to run `make clean`, to make sure everything is rebuilt properly.


## Updating Quarto extensions

This site is built using a number of Quarto extensions. The extensions are checked into the repository so they do not need to be installed separately. However, if you want to update the extensions to the latest version, you can do so by running:

```bash
make quarto-exts
```

Then commit the changes to the repository.


## Manually deploying the site

Normally, any commits on the `main` branch will automatically be built and deployed on the `gh-pages` branch using GitHub Actions. (Note: the reason that the site is built to the `docs/` directory is because that's what GitHub Pages uses.)

If you want to manually deploy the site, follow the build instructions above on the `main` branch (or another branch -- but typically not `gh-pages`), then run:

```bash
git checkout -B gh-pages
git add docs
git push -f
```


## Notes

By default, the submodules will have a specific commit checked out in detached HEAD mode; they will not have a branch checked out. If you want to do develop on the submodules, you may need to check out a branch like `main`. Note that when you do have a branch checked out in a submodule, you need to be careful to make sure it doesn't get out of sync with the commit that the parent project wants the submodule to be on.
