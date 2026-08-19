# Installing

The vignette runs Python code which invokes Julia code, and neither package index carries a working version of this
stack. `pip install dafpy` fetches 0.1.1, whose query syntax differs from the 0.3.0 the rest of the stack expects; the
General registry's `DataAxesFormats` is 0.1.2, which `Metacells` will not resolve against; and five of the eight
packages are on neither index at all. Everything is therefore installed from its repository, pinned to a known
revision. Getting the two languages to cooperate is the rest of the work, which is why this is a document of its own
rather than a cell in the notebook.

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
| includes additional useful packages | | ✔ | ✔ |
| needs privileges you may not have on a shared machine | | | ✔ |
| how much work it is to set up | most | least | in between |
| what it can disturb | your Python and Julia setup | nothing | nothing |
| is guaranteed to work | no — it can conflict with what you already have | almost — the environment is solved afresh, so a dependency can change under it | yes — the image is fixed |

**[Current env](#current-env)** installs the packages into the Python and the Julia you already use. It is the most
direct — your Jupyter already sees the result, and your existing tools are all still there — and also the most work,
since you assemble it yourself rather than being handed an environment to create. It is the only one which can damage
anything. The Julia packages are added to your default Julia environment, and they
demand versions the registry does not have, so they can conflict with whatever else lives there. Choose it when your
Python and Julia setups are ones you do not mind changing.

**[Conda](#conda)** builds a separate environment with its own Python, Julia and C++ runtime, so nothing of yours is
touched and the versions are the ones this was tested with. It is the least work, being an environment file to create
and a script to run once, and the isolation is real
in both directions: your shell tools and R remain usable, but your other Python environment's packages and your
existing Julia packages are not, unless you add them here too. Choose it when you want the vignette to work without
negotiating with the rest of your machine.

**[Docker](#docker)** goes further and isolates the operating system as well, so it runs identically wherever it runs.
The cost is that nothing of yours is inside it: your data has to be mounted, your tools are absent unless added to the
image, and you need a container runtime you are permitted to use, which on a shared cluster you often are not. Choose
it to run the vignette rather than to work alongside it.

The conda environment and the Docker image contain the same packages, so the vignette behaves the same in either.

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

### 1. Get the vignette

```
git clone https://github.com/tanaylab/metacells-sharpening-vignette
cd metacells-sharpening-vignette
```

### 2. Install the Python packages

```
pip install -r requirements.txt
```

This installs `dafpy` (the data layer), `somegraphspy` (the graphs), `metacellspy` (the computations) and `juliacall`
(which lets Python invoke Julia), each pinned to a specific commit.

Use the `pip` of the Python your Jupyter runs. That is what makes the notebook see these packages without any further
work: a notebook runs in a kernel, and the kernel is the Python that Jupyter itself runs in.

This upgrades whatever these packages depend on, `numpy` and `pandas` among them, in that environment.

### 3. Install the Julia packages

```
julia -e '
using Pkg
for url in [
    "https://github.com/tanaylab/TanayLabUtilities.jl",
    "https://github.com/tanaylab/DataAxesFormats.jl",
    "https://github.com/tanaylab/Slanter.jl",
    "https://github.com/tanaylab/SomeGraphs.jl",
    "https://github.com/tanaylab/Metacells.jl",
]
    Pkg.add(; url = url)
end
Pkg.add("PythonCall")
'
```

These go into your default Julia environment, which is what `juliacall` uses unless told otherwise, so nothing else
has to be configured.

They have to be added by URL rather than by name. Four of them are not in the General registry at all, and the fifth,
`DataAxesFormats`, is there only at 0.1.2, which `Metacells` will not accept. Adding them by name fails, and this is
also why they can conflict with what your default environment already holds.

### 4. Check that it worked

```
python -c '
import metacellspy as mc
print("metacellspy:", mc.__version__)
print("regularization:", mc.GENE_FRACTION_REGULARIZATION_FOR_CELLS)
'
```

The second line is read from Julia at import, so printing it means both halves are talking to each other.

### 5. Run the notebook

Start Jupyter as you always do, open the notebook, and run it. Its first cell checks that it can reach Julia and says
so plainly if it cannot.

### If importing fails with `GLIBCXX_... not found`

Your C++ runtime is older than the one Julia needs, which happens on RHEL 8 and its relatives. Julia ships a suitable
one next to itself, so point the loader at it before starting Jupyter:

```
export LD_LIBRARY_PATH="$(julia -e 'print(Sys.BINDIR)')/../lib/julia"
```

The conda and Docker installs do not have this problem, because they bring their own C++ runtime.

## Conda

TODO.

This will be two files. An `environment.yml` holding Python, Julia 1.12.6 — the version `Manifest.toml` was built with
— a C++ runtime, `jupyterlab`, and the additional packages listed under [Docker](#docker), so that the environment is
somewhere you can work rather than only run the vignette. And a `setup.sh`, run once inside the activated environment,
doing the two things `conda` cannot: writing the activation script which points `JULIA_DEPOT_PATH` inside the
environment prefix, and installing the Julia packages, which are not `conda` packages and so need `Pkg`.

Pointing the depot into the prefix is what makes this isolated: the *default* Julia environment then is the one inside
this environment, so nothing needs to be told which project to use, and removing the environment removes the Julia
packages along with everything else. The cost is that they are downloaded and precompiled again rather than shared
with your `~/.julia`, which is disk and a slow first run.

After that one script, activating and deactivating is free — the variables are recomputed on each activation.

The environment is solved when it is created, so two people creating it far enough apart can get different versions of
whatever is not pinned. A lock file, from `conda-lock` or `conda list --explicit`, would close that, at the cost of
having to regenerate it deliberately; worth it if the vignette is to reproduce a published result rather than only to
run.

If you want this isolation but cannot use `conda`, a Python virtual environment gets you most of it: create it, install
into it as in [Current env](#current-env), and set `JULIA_DEPOT_PATH` yourself so that the Julia packages do not land
in your default environment.

## Docker

TODO.

This will be an image with the whole stack resolved and precompiled, and a `docker run` line which mounts your data and
publishes the notebook, so that running the vignette needs nothing installed but Docker itself.

The base image has to be pinned by digest rather than by tag, since the point of this option is that the image is the
one that was tested, and a tag is repointed at will.

Beyond the vignette's own dependencies it will carry the packages that make it a usable place to work — `jupyterlab`,
`metacells`, `numpy`, `pandas`, `scipy` and the plotting libraries — and the [Conda](#conda) environment will carry the
same list, so that the vignette behaves identically in either.

Two things have to be decided: whether the image ships the example data or downloads it on first run, and whether it is
published to a registry or built locally from a `Dockerfile` in this repository. Building locally costs each reader a
long first build; publishing costs somewhere to publish it and someone to keep it current.
