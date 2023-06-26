data "archive_file" "messenger_source" {
    type        = "zip"
    source_dir  = "../src/messenger/messenger"
    output_path = "/tmp/messenger.zip"
}

resource "google_storage_bucket_object" "messenger_archive" {
  content_type = "application/zip"
  bucket = google_storage_bucket.artifacts.name
  source = data.archive_file.messenger_source.output_path

  name   = "messenger-${data.archive_file.messenger_source.output_md5}.zip"
}

resource "google_cloudfunctions_function" "stock-reporter" {
  name        = "stock-reporter"
  description = "Sends a stock report to Discord"
  runtime     = "python39"

  
  source_archive_bucket = google_storage_bucket.artifacts.name
  source_archive_object = google_storage_bucket_object.messenger_archive.name

  timeout               = 540
  available_memory_mb   = 2048
  max_instances         = 1

  entry_point           = "main"

  event_trigger {
    event_type = "google.pubsub.topic.publish"
    resource   = google_pubsub_topic.stock_notification.id
    failure_policy {
      retry = false
    }
  }

  environment_variables = {
    PRICES_MINUTELY = "${google_bigquery_dataset.stocks.dataset_id}.prices_minutely_resampled"
    PROJECT_ID      = var.project_id
  }

  secret_environment_variables {
    key     = "WEBHOOK"
    secret  = var.secret_stocks_webhook
    version = "latest"
  }
}
