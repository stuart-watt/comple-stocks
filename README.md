# stock-prompter
A service which sends notification and trading prompts to discord based on ASX stock prices.

# Installation

*This repo assumes you are running on a linux machine. I use WSL with an Ubuntu distro.*

### First steps

1. Clone the repo

2. Install make

run `sudo apt-get install build-essential` in the terminal. This will install build-essential and allow you to run commands defined in the Makefile.

3. Install miniconda into your home directory (follow: https://kontext.tech/article/1064/install-miniconda-and-anaconda-on-wsl-2-or-linux)

This code will operate out of a conda environment. First download Miniconda to your home directory:

`wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh`

*you may require wget to follow the installation on a linux machine. Run `sudo apt-get install wget` to install it if needed*


Then install and run through the prompts:

`sh Miniconda3-latest-Linux-x86_64.sh`

Finally restart your terminal to excecute changes (or run `source ~/.bashrc`)

Install mamba (`conda install -c conda-forge mamba`)

4. Create a `.env` file.

The Makefile assumes this file exists.
This file can be used to store sensitive environment variables that is ignored by git.
(For example, the name of the GCP project ID)

5. Create the conda environment

Run `conda init`
Run `make mamba` (This repo uses mamba to solve environment as it is quicker)

6. Activate the conda environment

`conda activate stocks`

### Deployment

This repo will also use terraform for infrastructure provisioning. You will need to install it.

1. Follow the manual insallation at
https://learn.hashicorp.com/tutorials/terraform/install-cli


2. Add your GCP project ID and region into the `.env` file

`PROJECT_ID=<your project name>`
`PROJECT_REGION=<your project region>`

3. Import GCP credentials

You will need GCP credentials in your Ubuntu distro.

Create a folder in your home directory called `.gcp` and 
save you GCP credentials in a file called `gcp_credentials.json`

4. Deploy terraform

run `make terraform`