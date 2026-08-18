# Installing

The vignette runs Python code which invokes Julia code, and neither package index carries a working version of this
stack. `pip install dafpy` fetches 0.1.1, whose query syntax differs from the 0.3.0 the rest of the stack expects; the
General registry's `DataAxesFormats` is 0.1.2, which `Metacells` will not resolve against; and five of the eight
packages are on neither index at all. Everything is therefore installed from its repository, pinned to a known
revision. Getting the two languages to cooperate is most of the remaining work, which is why this is a document of its
own rather than a cell in the notebook.

When the packages are released this document will get considerably shorter.

## Which of these to use

| | [Local](#local-install) | [Conda](#conda-install) | [Docker](#docker) |
|---|---|---|---|
| you want to read the vignette | ✔ | ✔ | ✔ |
| you want to run it on your own data | ✔ | ✔ | ✔ |
| you want to modify or debug the code | ✔ | ✔ | |
| you already manage your environments with `conda` | | ✔ | |
| you would rather install nothing at all | | | ✔ |
| number of steps | most | fewer | fewest |

**[Local install](#local-install)** puts Julia and a Python virtual environment on your machine directly. It has the
most steps and the most ways to go wrong, and in exchange it is the most transparent: you can read and change every
part of the stack, and a Julia REPL shows you exactly what the notebook is running. Choose it if you intend to work on
the code rather than only read the result. This is the option the vignette is developed against.

**[Conda install](#conda-install)** does the same thing with one environment manager for both languages, which is
easier if that is how you already work, and self-contained if you would rather the vignette did not touch anything
outside its environment.

**[Docker](#docker)** gives you an image with the whole stack already resolved. It is the most reliable way to run the
vignette and the least convenient way to change it, so choose it if you want to see the vignette work rather than to
work on it.

## Local install

Three steps: the Python packages, the Julia packages, and telling Python which Julia to use. The last one is the part
that goes wrong silently, so read it even if the first two went smoothly.

### Before you start

* **Julia 1.12.** `Metacells.jl` requires it. The simplest way to get it is
  [juliaup](https://github.com/JuliaLang/juliaup):

  ```
  curl -fsSL https://install.julialang.org | sh
  juliaup add 1.12
  juliaup default 1.12
  julia --version
  ```

* **Python 3.10 or later**, with `venv`.

* **git**, because none of the packages is installed from a package index.

### 1. Get the vignette

```
git clone https://github.com/tanaylab/metacells-sharpening-vignette
cd metacells-sharpening-vignette
```

Every command below is run from that directory.

### 2. Install the Python packages

```
python3 -m venv venv
venv/bin/pip install -r requirements.txt
```

This installs `dafpy` (the data layer), `somegraphspy` (the graphs), `metacellspy` (the computations) and `juliacall`
(which lets Python invoke Julia), each pinned to a specific commit.

### 3. Install the Julia packages

```
julia --project=. -e 'using Pkg; Pkg.instantiate()'
```

This reads `Manifest.toml`, which pins every Julia package to an exact revision, and installs them into `.` as a
project of its own. It downloads and precompiles a fair amount, so the first run takes a while.

Nothing is installed into your default Julia environment, so this cannot disturb any other Julia work you do.

### 4. Tell Python which Julia to use

By default `juliacall` builds a private Julia environment of its own, which Python can see and you cannot. That is a
poor place to be when something misbehaves, so the vignette instead points Python at the same project you just
instantiated. Then `julia --project=.` gives you a REPL holding exactly what the notebook holds, which is how you debug
it.

Four environment variables do this. The notebook sets them in its first cell, before importing anything, and then
checks that they took effect; you only need them yourself if you are running Python outside the notebook:

```
export PYTHON_JULIACALL_USE_DEFAULT_ENVIRONMENT=no
export PYTHON_JULIACALL_EXE="$(julia -e 'print(Sys.BINDIR)')/julia"
export PYTHON_JULIACALL_PROJECT="$PWD"
export LD_LIBRARY_PATH="$(julia -e 'print(Sys.BINDIR)')/../lib/julia"
```

Each of them is there for a reason which is not obvious:

* `PYTHON_JULIACALL_USE_DEFAULT_ENVIRONMENT=no` is **required**. Without it, importing `dafpy` activates your default
  Julia environment and discards whatever project you asked for, without saying anything.

* `PYTHON_JULIACALL_EXE` must be the real Julia binary. `which julia` gives you `juliaup`'s launcher, and `juliacall`
  works out where Julia's system image lives from the path of the executable it is given, so the launcher's directory
  sends it looking in the wrong place. `Sys.BINDIR` is Julia telling you where it actually is.

* `PYTHON_JULIACALL_EXE` and `PYTHON_JULIACALL_PROJECT` are honoured **only when both are set**. Setting one alone does
  nothing.

* `LD_LIBRARY_PATH` is needed on distributions whose C++ runtime is older than Julia's, which includes RHEL 8 and its
  relatives. Julia ships a suitable `libstdc++` next to itself, and this is what lets Python's dynamic loader find it.
  Without it, importing fails with `GLIBCXX_... not found`. It does no harm where it is not needed.

### 5. Check that it worked

```
venv/bin/python -c '
import metacellspy as mc
from metacellspy.julia_import import jl
print("Julia project:", jl.Base.active_project())
print("metacellspy  :", mc.__version__)
'
```

The project it prints must be the `Project.toml` in this directory. If it is one under `~/.julia`, then step 4 did not
take effect, and the notebook will not be running what you think it is.

To confirm both languages really do share one environment:

```
julia --project=. -e 'using Metacells; println(pkgversion(Metacells))'
```

### 6. Run the notebook

```
venv/bin/jupyter lab
```

The notebook's first cell sets the variables from step 4 and verifies them, so it works whichever way you started
Jupyter.

### If you insist on separate environments

You do not have to share one environment. Leave all four variables unset and `juliacall` reverts to its own behaviour:
it creates a private Julia environment and installs into it what the `juliapkg.json` of each Python package asks for,
which is the same set of packages from the same repositories.

This costs you the ability to inspect what the notebook is running. `julia --project=.` will no longer show you what
Python sees, and the versions are resolved independently of `Manifest.toml`, so they can differ from the ones the
vignette was verified against. Prefer the shared environment unless you have a reason not to.

### When it goes wrong

| symptom | cause |
|---|---|
| `GLIBCXX_3.4.26 not found` | `LD_LIBRARY_PATH` is not pointing at Julia's own `lib/julia` |
| `Unable to load dependent library ... libjulia-internal` | as above, or `PYTHON_JULIACALL_EXE` is the `juliaup` launcher rather than the real binary |
| the active project is under `~/.julia` | `PYTHON_JULIACALL_USE_DEFAULT_ENVIRONMENT` is not `no` |
| `Unsatisfiable requirements detected for package DataAxesFormats` | the Julia packages were added by name instead of by `Pkg.instantiate()` reading `Manifest.toml` |
| `ModuleNotFoundError: No module named 'metacellspy'` | the wrong Python — use `venv/bin/python`, not `python3` |
| Python finds a package you did not install | `PYTHONPATH` is set and is leaking packages into the environment |

## Conda install

TODO.

This will be an `environment.yml` holding both Python and Julia, with the Julia depot inside the environment prefix so
that the whole thing is self-contained and removing the environment removes everything it installed. The open question
is whether `conda-forge` carries the Julia 1.12 which `Metacells.jl` requires; if it does not, Julia comes from
`juliaup` as in the local install and only the Python side is managed by `conda`.

Until this is written, follow the [local install](#local-install) and use a `conda` environment with Python 3.10 or
later in place of the virtual environment in step 2. Everything else is the same.

## Docker

TODO.

This will be an image with the whole stack resolved and precompiled, so that running the vignette needs nothing
installed but Docker itself, and a `docker run` line which mounts your data and publishes the notebook.

Two things have to be decided: whether the image ships the example data or downloads it on first run, and whether it is
published to a registry or built locally from a `Dockerfile` in this repository.
