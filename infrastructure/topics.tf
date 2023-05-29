resource "google_pubsub_topic" "hourly" {
  name = "hourly"
}

resource "google_cloud_scheduler_job" "hourly" {
  name     = "hourly"
  schedule = "0 * * * *"
  region   = var.region

  pubsub_target {
    topic_name = google_pubsub_topic.hourly.id
    attributes = {
      "frequency" = "hourly"
    }
  }
}

resource "google_pubsub_topic" "stock_report" {
  name = "stock_report"
}

resource "google_cloud_scheduler_job" "stock_report" {
  name     = "stock_report"
  schedule = "0 7 * * *" # 3 pm AWST
  region   = var.region

  pubsub_target {
    topic_name = google_pubsub_topic.stock_report.id
    attributes = {
      "frequency" = "daily"
    }
  }
}
