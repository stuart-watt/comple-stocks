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
