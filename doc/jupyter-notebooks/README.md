# OpenAssetIO Jupyter Notebook Examples

## Getting started

### Installing Conda

#### Ubuntu (or other .deb system)

```sh
curl https://repo.anaconda.com/pkgs/misc/gpgkeys/anaconda.asc | gpg --dearmor > conda.gpg
sudo install -o root -g root -m 644 conda.gpg /usr/share/keyrings/conda-archive-keyring.gpg
gpg --keyring /usr/share/keyrings/conda-archive-keyring.gpg --no-default-keyring --fingerprint 34161F5BF5EB1D4BFBBB8F0A8AEB4F8B29D82806
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/conda-archive-keyring.gpg] https://repo.anaconda.com/pkgs/misc/debrepo/conda stable main" | sudo tee /etc/apt/sources.list.d/conda.list
sudo apt update
sudo apt install conda

# Next line needed in any new terminal
source /opt/conda/etc/profile.d/conda.sh
```

##### Optional Conda config
```sh
# To make conda available whenever a new terminal is opened
conda init
# The above will auto-activate a "base" environment, to stop this
conda config --set auto_activate_base false
# `mamba` is worth having in the base environment
conda install -n base mamba -c conda-forge
# To avoid having to explicitly specify `-c conda-forge` everywhere
conda config --prepend channels conda-forge
```

### Conda Jupyter Notebook environment

```sh
# `mamba` assumed to be installed as above. Can replace with `conda`,
# but it is very slow at dependency resolution.
# Note: conda-jupyter.txt is found alongside this README.
mamba create --name jupyter --file conda-jupyter.txt --yes
conda activate jupyter
```

### Install OpenAssetIO and dependencies to the Conda environment

```sh
# In case its not already active
conda activate jupyter

# Easy ones first
pip install openassetio-manager-bal
# TODO(DF): Must override TraitGen jsonschema version for Jupyter
#  compatibility. Then PyYAML wants to downgrade and fails to build.
#  So just install without deps - in practice, compatible ones are
#  already in the environment.
pip install openassetio-traitgen --no-deps

# Build and install OpenAssetIO to the Conda environment.

cd ${OPENASSETIO_REPO_DIR}
OPENASSETIO_CONAN_SKIP_CPYTHON=1 conan install -if conan-jupyter resources/build
CMAKE_PREFIX_PATH=conan-jupyter cmake -S . -B build-jupyter -DOPENASSETIO_GLIBCXX_USE_CXX11_ABI=ON
cmake --build build-jupyter --parallel
cmake --install build-jupyter --prefix ${CONDA_PREFIX}

# Build and install OpenAssetIO-MediaCreation to the Conda environment.

# Note: can't use `pip` because we need the # C++ trait view classes.
cd ${OPENASSETIO_MEDIACREATION_REPO_DIR}
cmake -S . -B build-jupyter -DOPENASSETIO_MEDIACREATION_GENERATE_PYTHON=ON
cmake --build build-jupyter --parallel
cmake --install build-jupyter --prefix ${CONDA_PREFIX}
```

### Start JupyterLab

```sh
cd ${OPENASSETIO_REPO_DIR}/doc/jupyter-notebooks
jupyter-lab
```

Then open up a `.ipynb` file and have some fun!

> **Note**
>
> Cling is temperamental. Before attempting to debug something, try
> restarting the kernel and running the Notebook from scratch. In
> JupyterLab see the "fast-forward" `>>` button.

### Execute headless

A big advantage of Notebooks is that they can be executed on the
command-line to validate they are correct; and rendered out to static
formats for use as documentation.

Converting a notebook to another format also executes it, e.g.

```
jupyter nbconvert --to html --execute versioning.ipynb
```

TODO(DF): There is also `jupyter run` - but I get wierd errors as if the
notebook file is malformed.
