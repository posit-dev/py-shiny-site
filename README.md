This repository contains the sources for the Shiny for Python web site.

## Setup and build

Install Quarto. Because Quarto is under rapid development, it's best to install by cloning the Quarto git repository and running a setup script; after that, just doing `git pull` will make the latest version available, without needing to run an installer each time. [Instructions here](https://github.com/quarto-dev/quarto-cli#development-version).

Clone this repository:

```bash
git clone https://github.com/rstudio/pyshiny-site.git
cd pyshiny-site
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
all                    Build assets and render site
site                   Build website
serve                  Build website and serve
install-uv             Install uv if not already installed
submodules             Update git submodules to commits referenced in this repository
submodules-pull        Pull latest commits in git submodules
quarto-extensions      Update Quarto extensions
quartodoc              Build qmd files for Shiny API docs
components             Build component static previews and update shinylive links
clean                  Remove Quarto website build files
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

To update shinylive links in `components/` and build static versions of the components in the gallery, run:

```bash
make components
```

### Virtualenv

When running `make`, all of the Python scripts and commands run in a virtualenv. If you want to run commands at the terminal in the same virtualenv, you will need to do the following:

Set up virtualenv (this only needs to be done once, and is done automatically by `make all` and `make install-uv`):

```bash
make install-uv
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

Install dependencies, build the assets, and finally build the site:

```bash
make all
```

In some cases, you may need to run `make clean`, to make sure everything is rebuilt properly.


## Updating Quarto extensions

This site is built using a number of Quarto extensions. The extensions are checked into the repository so they do not need to be installed separately. However, if you want to update the extensions to the latest version, you can do so by running:

```bash
make clean-extensions quarto-extensions
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
