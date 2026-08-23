# Installing

The vignette runs Python code which invokes Julia code. Eight packages make that work — three Python, five Julia — and
no package index carries a working version of any of them, so all eight are installed from the head of their repository.
That is why installing is a document of its own rather than a cell in the notebook.

Only those eight are installed, plus `juliacall`, which lets Python invoke Julia. Anything else you want to work with is
yours to add — in particular the `metacells` package, which computes the metacells this pipeline sharpens, and which
holds `numpy` below 2 and `pandas` below 3.

## Which of these to use

To *read* the vignette, install nothing: the published HTML and PDF are linked from the `README`. You install this to
run the pipeline on your own data.

| | [Current env](#current-env) | [Conda](#conda) |
|---|---|---|
| uses the Python, Julia and Jupyter you already have | ✔ | |
| isolated from your setup — packages, C++ runtime, interpreter versions | | ✔ |
| your other tools remain usable | ✔ | unless they are Python or Julia ones, or manually added |
| your data files are reachable | ✔ | ✔ |
| gives you a Julia, rather than needing one | | ✔ |
| how much work it is to set up | most | least |
| what it can disturb | your Python and Julia setup | nothing |
| is guaranteed to work | no — it can conflict with what you already have | almost — the environment is solved afresh, so a dependency can change under it |

**[Current env](#current-env)** installs into the Python and Julia you already use. Your Jupyter sees the result at once
and your existing tools are untouched — but you need a Julia 1.12 to install into, you set a few environment variables
yourself, and the Julia packages are resolved against whatever your default Julia environment already holds, which is
the one way any of this can break something of yours.

**[Conda](#conda)** builds a separate environment with its own Python and Julia. Nothing of yours is touched, nothing is
left for you to set afterwards, and the versions are the ones this was tested with. The cost is that your other Python
and Julia packages are not visible inside it unless you add them there too.

## Conda

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

### Using it

That is the whole of the setup. From then on, activating the environment is all there is to it:

```
conda activate metacells-sharpening
```

There is nothing to add to your shell startup and nothing to set by hand — the environment carries every variable the
vignette needs, so start Jupyter with it active and the notebook finds everything. Deactivating puts back whatever those
variables held before, so none of it escapes into the rest of your work.

There is one case where you do have something to do, and the setup script says so when it applies: on a machine whose
C++ runtime is older than Julia's, it ends by telling you to run `conda activate metacells-sharpening` once more. Do
that once and you are done — every later activation carries everything, as above.

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

### Installing

Installing does not need the vignette, only this one file:

```
curl -fsSLO https://raw.githubusercontent.com/tanaylab/metacells-sharpening-vignette/main/metacells-sharpening-setup-environment.sh
chmod +x metacells-sharpening-setup-environment.sh
./metacells-sharpening-setup-environment.sh
```

Run it with the `python3` of the Jupyter you use first in your path: a notebook runs in a kernel, and the kernel is the
Python that Jupyter itself runs in.

It installs `dafpy` (the data layer), `somegraphspy` (the graphs) and `metacellspy` (the computations), adds the five
Julia packages to your default Julia environment, compiles them, and checks that Python can reach Julia — so a conflict
surfaces now rather than in a notebook cell. Running it again is how you move to a newer head of each repository.

It then prints the environment variables to set. They are not optional: without them `juliacall` installs a second Julia
of its own and runs against that instead of against what you just installed. See [The environment
variables](#the-environment-variables) for what each does.

## The environment variables

These four steer `juliacall`. The conda environment carries them, so there they are nothing you have to think about;
installing into your current environment leaves them to you, which is what the setup script prints at the end.

They have to be set before Python reaches Julia, which is the moment `metacellspy` — or `dafpy`, or `somegraphspy`, or
`juliacall` itself — is first imported. Setting them in a notebook cell is too late if an earlier cell imported any of
those.

| | what to set it to | what it does |
|---|---|---|
| `PYTHON_JULIACALL_EXE` | `@default` | which `julia` to run; `@default` is the one in your path |
| `PYTHON_JULIACALL_PROJECT` | `@default` | which Julia environment to use; `@default` is that Julia's own, which is where the setup script put the packages |
| `PYTHON_JULIACALL_THREADS` | `auto` | how many threads Julia gets, `auto` being all of them; unset means one |
| `PYTHON_JULIACALL_HANDLE_SIGNALS` | `yes` | required whenever Julia has more than one thread, or Julia and Python fight over signals and the process dies with a segfault rather than an error |

The first two are the ones that matter. `juliacall` installs a Julia of its own unless it is pointed at one, and has no
way of saying "the one I already have": it wants a path that exists. `@default` is our addition and means exactly that,
expanded by `dafpy` — and by `somegraphspy` and `metacellspy`, which are built on it — before `juliacall` sees it. Set
neither, and everything the setup script installed is ignored in favour of a second Julia you did not ask for.

On a distribution whose C++ runtime is older than the one Julia needs — RHEL 8 and its relatives — `LD_LIBRARY_PATH`
also needs to be set, pointing at the runtime Julia ships beside itself. The script finds that out by trying rather than
by guessing. The conda install never needs it, bringing its own C++ runtime.

The script prints the environment variables you need to set, in the format of the sh, csh and fish families, but does
not add setting them for you anywhere: which file your shell reads when it starts depends on the shell and on whether it
is a login shell, so anything that guesses is silently wrong for somebody. The usual ones are:

| shell | file |
|---|---|
| `bash` | `~/.bashrc`, or `~/.bash_profile` for a login shell — on macOS the terminal starts login shells |
| `zsh` | `~/.zshrc`, or `~/.zprofile` for a login shell |
| `csh`, `tcsh` | `~/.cshrc`, which `tcsh` reads as `~/.tcshrc` when that exists |
| `fish` | `~/.config/fish/config.fish` |

Other environment variables that may be of interest: `JULIA_DEBUG` controls which debug messages, if any, are emitted
while running. The code sets up values you can include in this to emit specific things, such as intermediate results
and/or progress bars for loops; see the documentation of the relevant packages, especially `Metacells.jl`, for details.
`METACELLS_GMARA_CACHE`, where the gene lists fetched from Gmara are cached, `$HOME/.cache/gmara` otherwise, and
`METACELLS_GMARA_TIMEOUT`, how many seconds to wait for that cache's lock when several processes share it, `10`
otherwise, and forever if it is not positive.

## Check that it worked

Either way — with the conda environment active, or in a shell which has the variables:

```
python -c '
import metacellspy as mc
print("metacellspy:", mc.__version__)
print("regularization:", mc.GENE_FRACTION_REGULARIZATION_FOR_CELLS)
'
```

The second line is read from Julia at import, so printing it means both halves are talking to each other.
