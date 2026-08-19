#!/bin/bash

# Install the Julia packages the vignette needs into your default Julia environment.
#
# They are added by their repository URL rather than by name because four of them are not in the
# General registry, and the fifth, `DataAxesFormats`, is there only at a version `Metacells` will not
# accept. Adding them by name fails.
#
# This is the one part of installing which changes something outside the vignette: these packages are
# resolved against whatever else your default Julia environment already holds, and they ask for
# versions the registry does not have, so they can conflict with it. The conda and docker installs
# keep their Julia packages to themselves; see `INSTALL.md`.

set -e -u -o pipefail

REPOSITORIES=(
    https://github.com/tanaylab/TanayLabUtilities.jl
    https://github.com/tanaylab/DataAxesFormats.jl
    https://github.com/tanaylab/Metacells.jl
    https://github.com/tanaylab/Slanter.jl
    https://github.com/tanaylab/SomeGraphs.jl
)

if ! command -v julia > /dev/null; then
    echo "There is no julia in the path. See INSTALL.md for installing Julia 1.12." >&2
    exit 1
fi

echo "Adding the Julia packages to your default Julia environment:"
julia -e '
using Pkg
for url in ARGS
    Pkg.add(; url = url)
end
# `juliacall` needs this to talk to Julia at all, and adds it itself if it is missing; adding it here
# means everything is installed in one go.
Pkg.add("PythonCall")

# `Pkg.add` precompiles by default, but not when `JULIA_PKG_PRECOMPILE_AUTO` says otherwise, and this
# is where the waiting belongs: whatever is not compiled here is compiled by the first `import
# metacellspy`, which is in the middle of using the notebook.
Pkg.precompile()

Pkg.status()
' "${REPOSITORIES[@]}"

echo
echo "Checking that the packages load:"
julia -e 'using Metacells; using SomeGraphs; println("Metacells ", pkgversion(Metacells))'
