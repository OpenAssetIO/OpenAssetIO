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
# Alternatively, to make conda available all the time
# conda init
# The above will auto-activate a "base" environment, to stop this
# conda config --set auto_activate_base false
# `mamba` is worth having in the base environment
# conda install -n base mamba -c conda-forge
```

### Conda Jupyter Notebook environment

```sh
conda create -n jupyter --yes
conda activate jupyter

# mamba is a rewrite of conda in C++ and is orders of magnitude quicker.
# here we install to the current environment, but may be a good idea to
# have installed to the base environment.
conda install mamba -c conda-forge --yes
# Minimum version of gcc installed that also works with xeus-cling
mamba install xeus-cling jupyterlab gcc==10.4.0 gxx==10.4.0 tox git cmake ninja conan=1.59.0 -c conda-forge --yes
```

### Start JupyterLab

Assuming the current working directory is the same as this README
```sh
jupyter-lab
```

Then open up a `.ipynb` file and have some fun!

> **Note**
>
> Cling is temperamental. Before attempting to debug something, try
> restarting the kernel and running the Notebook from scratch. In
> JupyterLab see the "fast-forward" `>>` button.
