###########################
## Environment variables ##
###########################
include .env

export ALIAS = stocks 		# must match name field in environment.yaml

export TF_VAR_project_id = $(PROJECT_ID)
export TF_VAR_region = $(PROJECT_REGION)

export GOOGLE_APPLICATION_CREDENTIALS ?= $(HOME)/.gcp/gcp_credentials.json

#############
## Install ##
#############

mamba:
	mamba env update -n $(ALIAS) --file environment.yaml --prune \
		|| \
	mamba env create --file environment.yaml

#############
## Testing ##
#############


################
## Formatting ##
################

format:
	black .

################
## Deployment ##
################

terraform:
	cd infrastructure && terraform init && terraform apply -auto-approve

