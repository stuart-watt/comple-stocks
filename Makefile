###########################
## Environment variables ##
###########################
include .env

export ALIAS = stocks 		# must match name field in environment.yaml

export PROJECT_ID = $(GCP_PROJECT_ID)
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
	pytest src/trade_simulator/


################
## Formatting ##
################

format:
	black .

###############
## Terraform ##
###############

export TF_VAR_project_name = $(PROJECT_NAME)
export TF_VAR_project_id = $(GCP_PROJECT_ID)
export TF_VAR_region = $(PROJECT_REGION)
export TF_VAR_secret_stocks_webhook = $(SECRET_STOCKS_WEBHOOK)
export TF_VAR_secret_trading_webhook = $(SECRET_TRADING_WEBHOOK)
export TF_VAR_trading_channel_id = $(TRADING_CHANNEL_ID)
export TF_VAR_guild_id = $(GUILD_ID)
export TF_VAR_bot_auth_token = $(BOT_AUTH_TOKEN)

terraform:
	cd infrastructure && terraform init && terraform apply -auto-approve

#########
## DBT ##
#########

dbt:
	cd src/warehouse && dbt seed && dbt run
