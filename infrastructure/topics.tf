###############
## Ingestion ##
###############

resource "google_pubsub_topic" "ingestor" {
  name = "stock-ingestion"
}

resource "google_cloud_scheduler_job" "hourly" {
  name     = "stocks-hourly"
  schedule = "0 0 * * *"
  region   = var.region

  pubsub_target {
    topic_name = google_pubsub_topic.ingestor.id
    data = base64encode(jsonencode({"method": "ingest-hourly"}))
  }
}

resource "google_cloud_scheduler_job" "minutely" {
  name     = "stocks-minutely"
  schedule = "0,30 0-6,23 * * *" # every 30 mins between 10am-4:30pm AEST (accounting for daylight savings)
  region   = var.region

  pubsub_target {
    topic_name = google_pubsub_topic.ingestor.id
    data = base64encode(jsonencode({"method": "ingest-minutely"}))
  }
}

###############
## Reporting ##
###############

resource "google_pubsub_topic" "stock_report" {
  name = "stock_report"
}

resource "google_cloud_scheduler_job" "stock_report" {
  name     = "stock_report"
  schedule = "0 8 * * 1-5" # 4 pm AWST
  region   = var.region

  pubsub_target {
    topic_name = google_pubsub_topic.stock_report.id
    attributes = {
      "frequency" = "daily"
    }
  }
}
