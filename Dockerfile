# The vignette's environment, as an image.
#
# Build it from the directory holding this file:
#     docker build -t metacells-sharpening .
#
# It is the conda install, run at build time, so the image and the conda environment hold the same
# thing by construction rather than by anyone keeping two descriptions of it in step. See `INSTALL.md`.

# `miniforge3` rather than `micromamba`, because the setup script talks to `conda` itself. Pinned by
# digest rather than by tag, since the point of this way of installing is that the image is fixed.
# This is tag 26.3.2-3, and it is the digest of the multi-architecture manifest rather than of one
# image, so this still builds on arm64.
FROM condaforge/miniforge3@sha256:532f6ee7a858b009dc895f8313eb6ed875f05a455ec57d832aa6b4c66e2799b9

# Activating a conda environment inside a `RUN` needs a shell that can source the activation script.
SHELL ["/bin/bash", "-c"]

WORKDIR /opt/metacells-sharpening
COPY metacells-sharpening-conda-environment.yml metacells-sharpening-setup-environment.sh ./

# One layer, so that the half-built state - an environment with neither the Python nor the Julia
# packages in it - never becomes a layer of its own.
RUN conda env create --file metacells-sharpening-conda-environment.yml \
 && source /opt/conda/etc/profile.d/conda.sh \
 && conda activate metacells-sharpening \
 && ./metacells-sharpening-setup-environment.sh \
 && conda clean --all --yes

# `conda run` applies both the environment file's variables and the conda `julia` package's own
# activation script, so whatever you run arrives with the environment already set up.
# `--no-capture-output` because Jupyter's output is worth having as it is produced.
ENTRYPOINT ["conda", "run", "--no-capture-output", "--name", "metacells-sharpening"]

# The notebook is not in the image - this is the environment to run it in. Mount the vignette, or
# your own data, wherever you want it.
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root"]
