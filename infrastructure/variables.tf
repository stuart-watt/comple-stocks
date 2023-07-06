variable "project_name" {
  type        = string
  description = "The project name."
}

variable "project_id" {
  type        = string
  description = "The GCP project ID to deploy into."
}

variable "region" {
  type        = string
  description = "The preferred GCP availability zone."
  default     = "us-central1"
}

variable "secret_stocks_webhook" {
  type        = string
  description = "The webhook for the stock notifications."
}

variable "secret_trading_webhook" {
  type        = string
  description = "The webhook for the trading simulation notifications."
}

variable "trading_channel_id" {
  type        = string
  description = "The ID for the simualted trading Discord channel."
}

variable "guild_id" {
  type        = string
  description = "The ID for the Discord server."
}

variable "bot_auth_token" {
  type        = string
  description = "The Authorisation token for the Discord bot."
}