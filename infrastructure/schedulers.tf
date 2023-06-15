###############
## Ingestion ##
###############

resource "google_cloud_scheduler_job" "hourly" {
  name     = "stocks-hourly"
  schedule = "0 0 * * 1-5"
  region   = var.region

  pubsub_target {
    topic_name = google_pubsub_topic.ingestor.id
    data = base64encode(jsonencode({"method": "ingest-hourly"}))
  }
}


resource "google_cloud_scheduler_job" "minutely" {
  name     = "stocks-minutely"
  schedule = "30 3,6 23 * * 1-5" # runs at 11:30 and 2:30 AWST
  region   = var.region

  pubsub_target {
    topic_name = google_pubsub_topic.ingestor.id
    data = base64encode(jsonencode({"method": "ingest-minutely"}))
  }
}

###############
## Reporting ##
###############

resource "google_cloud_scheduler_job" "stock_report" {
  name     = "stock_report"
  schedule = "0 8 * * 1-5" # 4 pm AWST
  region   = var.region

  pubsub_target {
    topic_name = google_pubsub_topic.stock_notification.id
    data = base64encode(jsonencode({"method": "daily-report"}))
  }
}

resource "google_cloud_scheduler_job" "price_check" {
  name     = "price_check"
  schedule = "*/10,40 0-5 * * 1-5"
  region   = var.region

  pubsub_target {
    topic_name = google_pubsub_topic.stock_notification.id
    data = base64encode(jsonencode({"method": "price-check"}))
  }
}
