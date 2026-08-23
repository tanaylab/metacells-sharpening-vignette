# Installing

The vignette runs Python code which invokes Julia code. Eight packages make that work — three Python, five Julia — and
no package index carries a working version of any of them. `pip install dafpy` fetches 0.1.1, whose query syntax
differs from the 0.3.0 the rest expects; the General registry's `DataAxesFormats` is 0.1.2, which `Metacells` will not
resolve against; and the remaining six are on neither index at all. All eight are therefore installed from their
repositories, which is why this is a document of its own rather than a cell in the notebook.

Until they are released, all eight are taken from the head of their repository, so what you get is what is current
rather than what was current when this was written. Release day replaces that with ordinary versions from PyPI and the
General registry, and shortens this document considerably.

Only those eight are installed, plus `juliacall`, which lets Python invoke Julia. Nothing else is chosen for you:
whatever you want to work with alongside them is yours to add. That matters most for the `metacells` package, which
computes the metacells this pipeline sharpens — it holds `numpy` below 2 and `pandas` below 3, and imposing that on
everyone who installs the vignette would be rude.

When the packages are released this document will get considerably shorter.

## Which of these to use

To *read* the vignette, install nothing: the released HTML and PDF are linked from the `README`. You install this to
run the pipeline on your own data.

| | [Current env](#current-env) | [Conda](#conda) | [Docker](#docker) |
|---|---|---|---|
| uses the Python, Julia and Jupyter you already have | ✔ | | |
| isolated from your setup — packages, C++ runtime, interpreter versions | | ✔ | ✔ |
| isolated from the rest of the operating system | | | ✔ |
| your other tools remain usable | ✔ | unless they are Python or Julia ones, or manually added | only if added to the image |
| your data files are reachable | ✔ | ✔ | only if mounted into the container, or downloaded into it |
| gives you a Julia, rather than needing one | | ✔ | ✔ |
| needs privileges you may not have on a shared machine | | | ✔ |
| how much work it is to set up | most | least | in between |
| what it can disturb | your Python and Julia setup | nothing | nothing |
| is guaranteed to work | no — it can conflict with what you already have | almost — the environment is solved afresh, so a dependency can change under it | yes — the image is fixed |

**[Current env](#current-env)** installs into the Python and the Julia you already use. It is the most direct — your
Jupyter already sees the result, and your existing tools are all still there — and the most work: you have to have a
Julia 1.12 for it to install into, which is a prerequisite the other two hand you, and you have to put a handful of
environment variables in whatever your shell reads when it starts, which the other two carry for you. It is also the
only one which
can damage anything: the Julia packages go into your default Julia environment and are resolved together with whatever
is already in it, and they ask for versions the registry does not have. Choose it when your Python and Julia setups are
ones you do not mind changing.

**[Conda](#conda)** builds a separate environment with its own Python and Julia, so nothing of yours is touched and the
versions are the ones this was tested with. It is the least work, being one file to create an environment from and one
script to run, with no Julia to install first. The isolation is real in both directions: your shell tools and R remain
usable, but your other Python environment's packages and your existing Julia packages are not, unless you add them here
too. Choose it when you want the vignette to work without negotiating with the rest of your machine.

**[Docker](#docker)** goes further and isolates the operating system as well, so it runs identically wherever it runs.
The cost is that nothing of yours is inside it: your data has to be mounted, your tools are absent unless added to the
image, and you need a container runtime you are permitted to use, which on a shared cluster you often are not. Choose
it to run the vignette rather than to work alongside it.

The Docker image is built from the same environment file and the same script as the conda environment, so the two hold
the same thing and the vignette behaves the same in either.

These are three points on a spectrum rather than the only possibilities. A Python virtual environment, a Julia depot of
its own through `JULIA_DEPOT_PATH`, a Julia project through `--project`, and the private environment `juliacall` builds
for itself all work, and can be combined to isolate the two languages to whatever degree you want, independently. None
of that is described here: these three are the combinations which are tested, and the rest is left to those who know
they want it.

## Current env

### Before you start

* **Julia 1.12**, which `Metacells.jl` requires. If you do not have it,
  [juliaup](https://github.com/JuliaLang/juliaup) is the simplest way:

  ```
  curl -fsSL https://install.julialang.org | sh
  juliaup add 1.12
  juliaup default 1.12
  julia --version
  ```

* **Python 3.10 or later**, the one your Jupyter runs.

* **git**, because none of the packages is installed from a package index.

### 1. Install everything

Installing does not need the vignette, only this one file:

```
curl -fsSLO https://raw.githubusercontent.com/tanaylab/metacells-sharpening-vignette/main/metacells-sharpening-setup-environment.sh
chmod +x metacells-sharpening-setup-environment.sh
./metacells-sharpening-setup-environment.sh
```

Run it with the `python3` of the Jupyter you use first in your path. That is what makes the notebook see the result
without anything further: a notebook runs in a kernel, and the kernel is the Python that Jupyter itself runs in.

It installs `dafpy` (the data layer), `somegraphspy` (the graphs) and `metacellspy` (the computations), each from the
head of its repository, along with `juliacall`, which lets Python invoke Julia. That upgrades whatever they depend on
in that environment. Running the script again is how you move to a newer head.

It then adds the Julia packages to your default Julia environment. They are added by URL rather than by name: four are not in the General
registry at all, and the fifth, `DataAxesFormats`, is there only at 0.1.2, which `Metacells` will not accept. Adding
them by name fails, and this is also why they can conflict with what your default environment already holds.

Finally it compiles them and checks that they load, so that a conflict shows up now rather than in a notebook cell.

Then it prints the environment variables to set. They are not optional: `juliacall` picks a Julia of its own unless it
is told which one to use, so without them the notebook installs a second Julia and runs against that instead of against
what you just installed. See [The environment variables](#the-environment-variables) for what each of them does.

Nothing else is installed. `pip install` whatever else you want to work with — but note that the `metacells` package,
which computes the metacells this pipeline sharpens, holds `numpy` below 2 and `pandas` below 3, so installing it
constrains everything else in that environment.

### 2. Set what it printed

The script prints the lines to add for the sh, csh and fish families, and does not add them for you. Which file your
shell reads when it starts depends on the shell and on whether it is a login shell, and the syntax differs between
them, so anything that guesses is silently wrong for somebody.

The list is longer on some machines than on others. On a distribution whose C++ runtime is older than the one Julia
needs — RHEL 8 and its relatives — Python cannot load Julia until the loader is pointed at the runtime Julia ships
beside itself, and `LD_LIBRARY_PATH` is printed along with the rest. The script finds this out by trying rather than by
guessing from the distribution. The conda and Docker installs never need it, because they bring their own C++ runtime.

### 3. Check that it worked

In a shell which has the variables, which is a new one unless you set them by hand as well:

```
python -c '
import metacellspy as mc
print("metacellspy:", mc.__version__)
print("regularization:", mc.GENE_FRACTION_REGULARIZATION_FOR_CELLS)
'
```

The second line is read from Julia at import, so printing it means both halves are talking to each other.

### 4. Run the vignette

*Now* you need the vignette itself, which is where the notebook is:

```
git clone https://github.com/tanaylab/metacells-sharpening-vignette
cd metacells-sharpening-vignette
```

Start Jupyter as you always do, open the notebook, and run it. Its first cell checks that it can reach Julia and says
so plainly if it cannot.

You can equally point the notebook at your own data instead, in which case you need nothing from the repository at
all — what you installed above is the whole pipeline.

### Setting what it printed

The script prints the lines to add for the sh, csh and fish families, and does not add them for you. Which file your
shell reads when it starts depends on the shell and on whether it is a login shell, and the syntax differs between
them, so anything that guesses is silently wrong for somebody.

The list is longer on some machines than on others. On a distribution whose C++ runtime is older than the one Julia
needs — RHEL 8 and its relatives — Python cannot load Julia until the loader is pointed at the runtime Julia ships
beside itself, and `LD_LIBRARY_PATH` is printed along with the rest. The script finds this out by trying rather than by
guessing from the distribution. The conda and Docker installs never need it, because they bring their own C++ runtime.

## The environment variables

These are what the two languages are steered by. The conda install sets all of them for you; installing into your
current environment leaves the first four to you, which is what the setup script prints at the end.

They have to be in the environment before Python reaches Julia, which is the moment `metacellspy` — or `dafpy`, or
`somegraphspy`, or `juliacall` itself — is first imported. Setting them in a notebook cell is too late if an earlier
cell already imported any of those.

| | what to set it to | what it does |
|---|---|---|
| `PYTHON_JULIACALL_EXE` | `@default` | which `julia` binary to run; `@default` is the one in your path |
| `PYTHON_JULIACALL_PROJECT` | `@default` | which Julia environment to use; `@default` is that Julia's own default environment, which is where the setup script put the packages |
| `PYTHON_JULIACALL_THREADS` | `auto` | how many threads Julia gets, `auto` being all of them; unset means one |
| `PYTHON_JULIACALL_HANDLE_SIGNALS` | `yes` | must be `yes` whenever Julia has more than one thread, or Julia and Python fight over signals and the process dies with a segfault rather than an error |
| `JULIA_DEPOT_PATH` | leave alone | where Julia keeps its packages, `~/.julia` unless you say otherwise |
| `LD_LIBRARY_PATH` | leave alone | where the loader looks for the C++ runtime |
| `METACELLS_GMARA_CACHE` | leave alone | where the gene lists fetched from Gmara are cached, `$HOME/.cache/gmara` unless you say otherwise |
| `METACELLS_GMARA_TIMEOUT` | leave alone | seconds to wait for a lock file in that cache, when several processes use it at once, `10` unless you say otherwise; not positive waits forever |

The first two are the ones that matter. `juliacall` has `juliapkg` install a Julia of its own unless it is pointed at
one, and it has no way of saying "the one I already have": `PYTHON_JULIACALL_EXE` must name an executable and
`PYTHON_JULIACALL_PROJECT` a directory that exists. `@default` is our addition, and means exactly that — expanded by
`dafpy`, and by `somegraphspy` and `metacellspy` which are built on it, before `juliacall` sees it.

They are independent, so you can give one of them a path of your own and leave the other as `@default`. Set neither,
and everything the setup script installed is ignored in favour of a second Julia you did not ask for. Import
`juliacall` before any of our packages and it rejects `@default` as a path which does not exist, naming the variable —
which is the point of using a value it refuses rather than a variable it would silently ignore.

The other two are left exactly as you set them. Julia runs on one thread if you do not ask for more, and asking for
more without also handling the signals is what makes it crash, so the two go together.

The rest are yours. `JULIA_DEPOT_PATH` is set by the setup script only when installing into the conda environment, so
that the Julia packages live inside it rather than in your `~/.julia`. `LD_LIBRARY_PATH` only if the setup script tells
you to, and the Gmara pair only if the defaults do not suit you.

## Conda

TODO — the files exist and are described here, but this has not yet been run end to end.

You need `conda`, and nothing else: Python and Julia both come from the environment.

Installing does not need the vignette, only these two files:

```
BASE=https://raw.githubusercontent.com/tanaylab/metacells-sharpening-vignette/main
curl -fsSLO $BASE/metacells-sharpening-conda-environment.yml
curl -fsSLO $BASE/metacells-sharpening-setup-environment.sh
chmod +x metacells-sharpening-setup-environment.sh

conda env create -f metacells-sharpening-conda-environment.yml
conda activate metacells-sharpening
./metacells-sharpening-setup-environment.sh
```

The environment file holds only what `pip` cannot install — Python 3.12 and Julia 1.12.6. Everything else is left to
the same script the other install uses, so that one resolver owns the whole Python dependency graph; naming a Python
package in both places is how a conda environment breaks.

The environment file is also what isolates the environment, which `conda` does not do by itself. `PYTHONPATH` is yours,
and it and your `~/.local` site directory are both searched before anything installed here, so the file empties the
first and sets `PYTHONNOUSERSITE`. Without that a source checkout on your `PYTHONPATH` is enough to make `pip` consider
that package installed and skip it, leaving an environment which looks complete and is not.

The script installs into the environment the conda `julia` package made for it, which it names after the conda
environment and keeps in a depot inside it. That is what makes the Julia packages part of the environment — removing
the environment removes them too — and it is what `PYTHON_JULIACALL_PROJECT=@default` resolves to. The cost is that
they are downloaded and compiled again rather than shared with your `~/.julia`.

Nothing is left for you to set afterwards: the environment file carries every variable, and the conda `julia` package
carries the Julia ones, which is the difference from installing into your current environment. The one exception is the
rare machine which needs `LD_LIBRARY_PATH`; there the script stores it and tells you to activate the environment once
more, since the shell you ran it from activated before that value existed.

The environment is solved when it is created, and until the packages are released both halves track the head of their
repositories, so two people installing far enough apart can get different versions of everything but Python and Julia
themselves. That is deliberate while the packages are still moving. Reproducing a published result rather than merely
running the pipeline wants the opposite — a `conda-lock` file for the conda half and a committed `Manifest.toml` for
the Julia one — which is what release day brings.

If you want this isolation but cannot use `conda`, a Python virtual environment gets you most of it: create it, install
into it as in [Current env](#current-env), and set `JULIA_DEPOT_PATH` yourself so that the Julia packages do not land
in your default environment. `PYTHON_JULIACALL_PROJECT=@default` then follows the depot you chose, so the variables to
set are the same ones.

## Docker

TODO — the `Dockerfile` is written and is described here, but it has not been built. Nobody has run `docker build` on
it yet.

You need a container runtime and permission to use it, which on a shared machine you often do not have.

```
git clone https://github.com/tanaylab/metacells-sharpening-vignette
cd metacells-sharpening-vignette
docker build -t metacells-sharpening .
```

Unlike the other two, this one wants the repository, because a `Dockerfile` is a file rather than something you can
pipe. `.dockerignore` then narrows what the build can see to the two files it copies, so nothing else in the repository
can drift into the image without being asked for.

The image *is* the [Conda](#conda) install: the same environment file, the same setup script, run at build time. The
claim that the two hold the same thing is therefore true by construction rather than a promise kept by hand. What it
costs is a long first build — every Julia package is compiled inside the image — in exchange for never compiling
anything again, on any machine that can run it.

The base image is pinned by digest rather than by tag, since the point of this way of installing is that the image is
the one that was tested and a tag is repointed at will. It is the digest of the multi-architecture manifest, not of one
image, so this still builds on arm64.

The notebook is deliberately *not* in the image. The image is the environment; what you run in it is yours to mount:

```
docker run --rm -p 8888:8888 -v "$PWD:/work" -w /work metacells-sharpening
```

That publishes Jupyter on port 8888 and puts the current directory — the vignette, or your own data — at `/work`.
`ENTRYPOINT` is `conda run` in the environment, so anything else you ask for arrives with the environment already set
up:

```
docker run --rm -v "$PWD:/work" -w /work metacells-sharpening python -c 'import metacellspy; print(metacellspy.__version__)'
```

Two things are still open: whether the image ships the example data or downloads it on first run, and whether it is
published to a registry or built locally as above. Publishing costs somewhere to publish it and someone to keep it
current; building locally costs each reader that first build.
