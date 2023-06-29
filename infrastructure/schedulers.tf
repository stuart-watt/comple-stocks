###############
## Ingestion ##
###############

resource "google_cloud_scheduler_job" "listed_companies" {
  name        = "stocks-listed"
  schedule    = "0 0 * * 1-5"
  region      = var.region
  description = "Starts a job to ingest the listed companies on the ASX."

  pubsub_target {
    topic_name = google_pubsub_topic.ingestor.id
    data = base64encode(jsonencode({"method": "listed_companies", "interval": "1h"}))
  }
}

resource "google_cloud_scheduler_job" "hourly" {
  name        = "stocks-hourly"
  schedule    = "0 0 * * 1-5"
  region      = var.region
  description = "Starts a job to ingest the stock prices with hourly granularity."

  pubsub_target {
    topic_name = google_pubsub_topic.ingestor.id
    data = base64encode(jsonencode({"method": "stock", "interval": "1h"}))
  }
}

resource "google_cloud_scheduler_job" "index-hourly" {
  name        = "index-hourly"
  schedule    = "50 23 * * 1-5"
  region      = var.region
  description = "Starts a job to ingest the ASX indices with hourly granularity."

  pubsub_target {
    topic_name = google_pubsub_topic.ingestor.id
    data = base64encode(jsonencode({"method": "index", "interval": "1h"}))
  }
}


resource "google_cloud_scheduler_job" "minutely" {
  name        = "stocks-minutely"
  schedule    = "0 0-7 * * 1-5" # runs every hour between market hours
  region      = var.region
  description = "Starts a job to ingest the stock prices with minutely granularity."

  pubsub_target {
    topic_name = google_pubsub_topic.ingestor.id
    data = base64encode(jsonencode({"method": "stock", "interval": "1m"}))
  }
}

###############
## Reporting ##
###############

resource "google_cloud_scheduler_job" "stock_report" {
  name        = "stock_report"
  schedule    = "0 8 * * 1-5" # 4 pm AWST
  region      = var.region
  description = "Starts a job to send a stock report to Discord."

  pubsub_target {
    topic_name = google_pubsub_topic.stock_notification.id
    data = base64encode(jsonencode({"method": "daily-report"}))
  }
}

resource "google_cloud_scheduler_job" "price_check" {
  name     = "price_check"
  schedule = "30 0-5 * * 1-5"
  region   = var.region
  description = "Starts a job to send a stock alert to discord."

  pubsub_target {
    topic_name = google_pubsub_topic.stock_notification.id
    data = base64encode(jsonencode({"method": "price-check"}))
  }
}

###############
## Simulator ##
###############

resource "google_cloud_scheduler_job" "simulation_report" {
  name        = "trading_simulation_report"
  schedule    = "0 8 * * 1-5" # 4 pm AWST
  region      = var.region
  description = "Starts a job to send a trading simulation report to Discord."

  pubsub_target {
    topic_name = google_pubsub_topic.simulation_report.id
    data = base64encode(jsonencode({"method": "report"}))
  }
}

resource "google_cloud_scheduler_job" "simulation_scrape" {
  name        = "trading_simulation_scraper"
  schedule    = "30 0-6 * * *"
  region      = var.region
  description = "Starts a job to scrape Discord messages and save to BigQuery."

  pubsub_target {
    topic_name = google_pubsub_topic.simulation_report.id
    data = base64encode(jsonencode({"method": "scrape-trades"}))
  }
}