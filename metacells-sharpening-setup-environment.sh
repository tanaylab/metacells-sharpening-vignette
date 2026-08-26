#!/bin/bash

# Install everything the vignette needs, into either the conda environment or whatever Python and
# Julia you already use, and say what has to be in the environment for the notebook to find it.
#
# Running it again is harmless, and is what to do to move to a newer version of any of the packages.
#
# It installs into the conda environment when that environment is active, and into your own Python
# and Julia otherwise. Both halves go into whatever is active: `pip` into that Python, and the Julia
# packages into that Julia's default environment. In the conda environment that environment is one
# `conda` made for it, and in yours it is yours, and may already list packages of your own - which is
# why installing into your own is the way that can conflict with something.

set -e -u -o pipefail

EXPECTED_VERSION="0.1.0"


# The vignette's own Python packages. None is on PyPI at a version which works: `pip install dafpy`
# fetches 0.1.1, whose query syntax differs from the 0.3.0 the rest of the stack expects. Until they
# are released they are taken from the head of each repository, which is where the version the
# vignette is written against lives.
#
# As a tarball of the branch rather than as `git+https://`, which `pip` implements by running `git`.
# Installing this therefore needs no `git`, which is worth more than the repository `pip` would have
# recorded as the source: Julia's own `Pkg` uses the `LibGit2` it bundles, so nothing else here needs
# one either.
PYTHON_PACKAGES=(
    "dafpy @ https://github.com/tanaylab/dafpy/archive/refs/heads/main.tar.gz"
    "somegraphspy @ https://github.com/tanaylab/somegraphspy/archive/refs/heads/main.tar.gz"
    "metacellspy @ https://github.com/tanaylab/metacellspy/archive/refs/heads/main.tar.gz"
)

IN_CONDA_ENVIRONMENT=false
if [ -n "${METACELLS_SHARPENING_VIGNETTE:-}" ]; then
    IN_CONDA_ENVIRONMENT=true

    # Whatever you called it when you created it, which is not necessarily what the documentation
    # calls it, and is what any command printed below has to name.
    CURRENT_CONDA_ENV="$(conda info --json |
        python3 -c 'import json, sys; print(json.load(sys.stdin)["active_prefix_name"])')"

    if [ "$METACELLS_SHARPENING_VIGNETTE" != "$EXPECTED_VERSION" ]; then
        echo "The active environment is version $METACELLS_SHARPENING_VIGNETTE," >&2
        echo "and this expects $EXPECTED_VERSION. Recreate it:" >&2
        echo "    conda env remove -n $CURRENT_CONDA_ENV" >&2
        echo "    conda env create -f metacells-sharpening-conda-environment.yml" >&2
        exit 1
    fi
fi

if ! command -v julia > /dev/null; then
    echo "There is no julia in the path. See INSTALL.md for installing Julia 1.12." >&2
    exit 1
fi

if $IN_CONDA_ENVIRONMENT; then
    echo "Installing into the conda environment at $CONDA_PREFIX."
else
    echo "Installing into $(command -v python3) and $(command -v julia)."
    echo "This adds the Julia packages to your default Julia environment, alongside whatever else is"
    echo "in it. Use the conda environment instead if you would rather it were left alone."
fi

echo
echo "Installing the Python packages:"
# Twice, because their version numbers do not change between commits: `pip` resolves the repository
# to its head, sees the version it already has, and keeps the old files. Only `--force-reinstall`
# replaces them, and `--no-deps` keeps that from dragging everything else through a reinstall as
# well - which is why the first command is still needed, to install those dependencies.
pip install "${PYTHON_PACKAGES[@]}"
pip install --force-reinstall --no-deps "${PYTHON_PACKAGES[@]}"

# Jupyter is only installed in the conda environment: the point of installing into your own is that
# you already have one.
if $IN_CONDA_ENVIRONMENT; then
    pip install jupyterlab
fi

# Which Julia packages are needed is not written down here. Each of the three Python packages ships a
# `juliapkg.json` saying what it imports, and `juliapkg` - which arrives with `juliacall` - merges
# them. Reading that is what keeps this from being a second, and eventually wrong, copy of the same
# list: when one of the three starts using another Julia package, this installs it without being
# told. It has to run after the `pip` install above, since those are the files it reads.
#
# `juliapkg` cannot install them itself. It manages a Julia environment of its own, and
# `PYTHON_JULIACALL_PROJECT=@default` deliberately takes that job away from it, so what it knows has
# to be handed to `Pkg`.
#
# `juliacall` declares itself the same way, which is where `PythonCall` - what it talks to Julia
# through - comes from, so nothing here names that either.
#
# Each package is named as `name` when it is in the General registry, and as `name=url` when it is
# not - which is the four of ours that are not registered, plus `DataAxesFormats`, which is there
# only at a version `Metacells` will not accept.
JULIA_PACKAGES=($(python3 -c '
import contextlib
import sys

import juliapkg.deps

# `juliapkg` says which files it read by printing, so its chatter has to go somewhere other than the
# list being collected here.
with contextlib.redirect_stdout(sys.stderr):
    _, specifications = juliapkg.deps.find_requirements()

for specification in sorted(specifications, key = lambda specification: specification.name):
    print(specification.name if specification.url is None else f"{specification.name}={specification.url}")
'))

# The conda `julia` package names an environment after the conda environment, and points the depot
# inside it, which is what makes the Julia packages part of it: removing the conda environment
# removes them too. Either way this is the environment that Julia uses by itself, which is what
# `PYTHON_JULIACALL_PROJECT=@default` resolves to.
echo
echo "Adding the Julia packages to $(julia -e 'print(dirname(Base.active_project()))'):"
julia -e '
using Pkg

# A package you are developing is left as it is. `Pkg.add` would replace your working copy with a
# clone of the repository, without saying so, and your working copy is the whole point of having
# devved it - and, if you are developing these, what you want the vignette to run against.
developed = Set(info.name for (_, info) in Pkg.dependencies() if info.is_tracking_path)

specifications = Pkg.PackageSpec[]
for specification in ARGS
    name_and_url = split(specification, "="; limit = 2)
    name = String(name_and_url[1])
    if name in developed
        println("    keeping the version of ", name, " you are developing")
    elseif length(name_and_url) == 1
        push!(specifications, Pkg.PackageSpec(; name))
    else
        push!(specifications, Pkg.PackageSpec(; url = String(name_and_url[2])))
    end
end

# All of them in one call, so that `Pkg` resolves them together: added one at a time, a package would
# have to come after everything it depends on, and nothing here knows that order.
Pkg.add(specifications)
' "${JULIA_PACKAGES[@]}"

# Installing is not the same as compiling. Whatever is not compiled here is compiled by the first
# `import metacellspy`, in the middle of using the notebook.
echo
echo "Compiling:"
julia -e 'using Pkg; Pkg.precompile(); Pkg.status()'

# A different test from compiling: this is where a conflict with what was already installed shows up.
echo
echo "Checking that Julia loads the packages:"
julia -e 'using Metacells; using SomeGraphs; println("Metacells ", pkgversion(Metacells))'

# The test that matters, since this is how the notebook reaches Julia. On a distribution whose C++
# runtime predates the one Julia needs - RHEL 8 and its relatives - this is where it fails, and the
# fix is to let the loader find the one Julia ships. Rather than deciding in advance whether that is
# needed, it is tried only when the plain attempt has failed.
echo
echo "Checking that Python reaches Julia:"
JULIA_LIBRARIES="$(cd "$(julia -e 'print(Sys.BINDIR)')/../lib/julia" && pwd)"

# The same variables the conda environment file holds, so that the check below tests what was just
# installed. In the conda environment they are set already and this changes nothing; otherwise they
# are set only here, which is why they are printed at the end for you to set as well.
export PYTHON_JULIACALL_EXE="@default"
export PYTHON_JULIACALL_PROJECT="@default"
export PYTHON_JULIACALL_THREADS="auto"
export PYTHON_JULIACALL_HANDLE_SIGNALS="yes"

if python3 -c 'import metacellspy' 2> /tmp/metacells-sharpening-check.$$; then
    NEEDS_LIBRARY_PATH=false
elif LD_LIBRARY_PATH="$JULIA_LIBRARIES${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}" \
        python3 -c 'import metacellspy' 2> /dev/null; then
    NEEDS_LIBRARY_PATH=true
else
    echo "Python cannot reach Julia:" >&2
    cat /tmp/metacells-sharpening-check.$$ >&2
    rm -f /tmp/metacells-sharpening-check.$$
    exit 1
fi
rm -f /tmp/metacells-sharpening-check.$$
echo "    ok"

echo
echo "Done."

if $IN_CONDA_ENVIRONMENT; then
    # The environment file holds every variable this needs, and the conda `julia` package holds the
    # Julia ones, so activating the environment is all there is to it. `conda` saves what a variable
    # held before activation and puts it back on deactivation, so none of that escapes.
    #
    # The library path is the exception, since only trying it can say whether it is needed, and it
    # is the one thing here which has to keep whatever it already held.
    if $NEEDS_LIBRARY_PATH; then
        conda env config vars set \
            LD_LIBRARY_PATH="$JULIA_LIBRARIES${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}" > /dev/null
        echo "Activate the environment once more, so that the library path it now holds is set:"
        echo "    conda activate $CURRENT_CONDA_ENV"
    else
        echo "Start Jupyter with $CURRENT_CONDA_ENV active and it will find all of this."
    fi
    exit 0
fi

# Printed rather than written into a startup file. Which file a shell reads depends on the shell and
# on whether it is a login shell, and the syntax differs between them - `setenv` in the csh family,
# `set -gx` in fish - so anything which guesses is wrong for somebody, silently. You know your shell;
# this only has to tell you what to put in it.

# Print how to set the variables whose value is simply given, in the syntax of one shell: how it
# spells "set this in the environment", and what it puts between the name and the value. The library
# path is not among them - it keeps what it already held, which every shell spells its own way.
print_variables() {
    set_variable="$1"
    assign="$2"
    echo "    $set_variable PYTHON_JULIACALL_EXE$assign@default"
    echo "    $set_variable PYTHON_JULIACALL_PROJECT$assign@default"
    echo "    $set_variable PYTHON_JULIACALL_THREADS${assign}auto"
    echo "    $set_variable PYTHON_JULIACALL_HANDLE_SIGNALS${assign}yes"
}

echo
echo "Set these in whatever your shell reads when it starts, so that they hold whenever you start"
echo "Jupyter. Without them the notebook does not use what was just installed: \`juliacall\` installs"
echo "a second Julia, of its own, and uses that instead."
if $NEEDS_LIBRARY_PATH; then
    echo
    echo "The library path is among them because this machine's C++ runtime is older than the one"
    echo "Julia needs, so Python can only reach Julia when the loader is pointed at the one Julia"
    echo "ships. That is how it worked here."
fi

echo
echo "In the sh family, which is bash, zsh and ksh:"
echo
print_variables export =
if $NEEDS_LIBRARY_PATH; then
    echo "    export LD_LIBRARY_PATH=\"$JULIA_LIBRARIES\${LD_LIBRARY_PATH:+:\$LD_LIBRARY_PATH}\""
fi

echo
echo "In the csh family, which is csh and tcsh, where naming an unset variable is an error:"
echo
print_variables setenv " "
if $NEEDS_LIBRARY_PATH; then
    echo "    if (\$?LD_LIBRARY_PATH) then"
    echo "        setenv LD_LIBRARY_PATH $JULIA_LIBRARIES:\$LD_LIBRARY_PATH"
    echo "    else"
    echo "        setenv LD_LIBRARY_PATH $JULIA_LIBRARIES"
    echo "    endif"
fi

echo
echo "In fish:"
echo
print_variables "set -gx" " "
if $NEEDS_LIBRARY_PATH; then
    echo "    set -gx LD_LIBRARY_PATH $JULIA_LIBRARIES \$LD_LIBRARY_PATH"
fi

echo
echo "Run this script again if you upgrade Julia, since what it printed describes the Julia you"
echo "have now."
