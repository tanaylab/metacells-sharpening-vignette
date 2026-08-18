# Installing

The vignette runs Python code which invokes Julia code. Getting the two to cooperate is most of the work here, which is
why this is a document of its own rather than a cell in the notebook.

Setting it up takes three steps: the Python packages, the Julia packages, and telling Python which Julia to use. The
last one is the part that goes wrong silently, so read it even if the first two went smoothly.

## Before you start

* **Julia 1.12.** `Metacells.jl` requires it. The simplest way to get it is
  [juliaup](https://github.com/JuliaLang/juliaup):

  ```
  curl -fsSL https://install.julialang.org | sh
  juliaup add 1.12
  juliaup default 1.12
  julia --version
  ```

* **Python 3.10 or later**, with `venv`.

* **git**, because none of the packages is installed from a package index. See "Why everything comes from git" below.

## 1. Get the vignette

```
git clone https://github.com/tanaylab/metacells-sharpening-vignette
cd metacells-sharpening-vignette
```

Every command below is run from that directory.

## 2. Install the Python packages

```
python3 -m venv venv
venv/bin/pip install -r requirements.txt
```

This installs `dafpy` (the data layer), `somegraphspy` (the graphs), `metacellspy` (the computations) and `juliacall`
(which lets Python invoke Julia), each pinned to a specific commit.

If you use `conda` instead of `venv`, create an environment with Python 3.10 or later and `pip install -r
requirements.txt` into it; nothing below depends on which of the two you used.

## 3. Install the Julia packages

```
julia --project=. -e 'using Pkg; Pkg.instantiate()'
```

This reads `Manifest.toml`, which pins every Julia package to an exact revision, and installs them into `.` as a
project of its own. It downloads and precompiles a fair amount, so the first run takes a while.

Nothing is installed into your default Julia environment, so this cannot disturb any other Julia work you do.

## 4. Tell Python which Julia to use

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

## 5. Check that it worked

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

## Running the notebook

```
venv/bin/jupyter lab
```

The notebook's first cell sets the variables from step 4 and verifies them, so it works whichever way you started
Jupyter.

## If you insist on separate environments

You do not have to share one environment. Leave all four variables unset and `juliacall` reverts to its own behaviour:
it creates a private Julia environment and installs into it what the `juliapkg.json` of each Python package asks for,
which is the same set of packages from the same repositories.

This costs you the ability to inspect what the notebook is running. `julia --project=.` will no longer show you what
Python sees, and the versions are resolved independently of `Manifest.toml`, so they can differ from the ones the
vignette was verified against. Prefer the shared environment unless you have a reason not to.

## Why everything comes from git

Neither package index carries a working version of this stack:

| package | index | what is needed |
|---|---|---|
| `dafpy` | PyPI has 0.1.1 | 0.3.0 — 0.1.1 has a different query syntax |
| `somegraphspy`, `metacellspy` | not on PyPI | — |
| `DataAxesFormats.jl` | General has 0.1.2 | 0.3.0 — `Metacells` will not resolve against 0.1.2 |
| `Metacells.jl`, `TanayLabUtilities.jl`, `SomeGraphs.jl`, `Slanter.jl` | not registered | — |

Installing from a package index would therefore either fail outright or, worse, quietly give you a combination which
does not work. `requirements.txt` and `Manifest.toml` between them pin every package to an exact revision, so what you
get is what the vignette was verified against.

When these packages are released this document will get considerably shorter.

## When it goes wrong

| symptom | cause |
|---|---|
| `GLIBCXX_3.4.26 not found` | `LD_LIBRARY_PATH` is not pointing at Julia's own `lib/julia` |
| `Unable to load dependent library ... libjulia-internal` | as above, or `PYTHON_JULIACALL_EXE` is the `juliaup` launcher rather than the real binary |
| the active project is under `~/.julia` | `PYTHON_JULIACALL_USE_DEFAULT_ENVIRONMENT` is not `no` |
| `Unsatisfiable requirements detected for package DataAxesFormats` | the Julia packages were added by name instead of by `Pkg.instantiate()` reading `Manifest.toml` |
| `ModuleNotFoundError: No module named 'metacellspy'` | the wrong Python — use `venv/bin/python`, not `python3` |
| Python finds a package you did not install | `PYTHONPATH` is set and is leaking packages into the environment |
