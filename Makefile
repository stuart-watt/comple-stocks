###########################
## Environment variables ##
###########################
include .env

export ALIAS = stocks 		# must match name field in environment.yaml

export TF_VAR_project_name = $(PROJECT_NAME)
export TF_VAR_project_id = $(PROJECT_ID)
export TF_VAR_region = $(PROJECT_REGION)
export TF_VAR_secret_webhook = $(SECRET_WEBHOOK)
export GOOGLE_APPLICATION_CREDENTIALS ?= $(HOME)/$(CREDENTIALS)

#############
## Install ##
#############

mamba:
	mamba env update -n $(ALIAS) --file environment.yml --prune \
		|| \
	mamba env create --file environment.yml

#############
## Testing ##
#############

tests:
	pytest src/messenger/
	pytest src/stock_scraper/


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
