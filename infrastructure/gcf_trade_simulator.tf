data "archive_file" "trade_simulator_source" {
    type        = "zip"
    source_dir  = "../src/trade_simulator/trade_simulator"
    output_path = "/tmp/trade_simulator.zip"
}

resource "google_storage_bucket_object" "trade_simulator_archive" {
  content_type = "application/zip"
  bucket = google_storage_bucket.artifacts.name
  source = data.archive_file.trade_simulator_source.output_path

  name   = "trade-simulator-${data.archive_file.trade_simulator_source.output_md5}.zip"
}

resource "google_cloudfunctions_function" "trade-simulator" {
  name        = "trade-simulator"
  description = "Sends a simulation report to Discord"
  runtime     = "python39"

  
  source_archive_bucket = google_storage_bucket.artifacts.name
  source_archive_object = google_storage_bucket_object.trade_simulator_archive.name

  timeout               = 540
  available_memory_mb   = 2048
  max_instances         = 1

  entry_point           = "main"

  event_trigger {
    event_type = "google.pubsub.topic.publish"
    resource   = google_pubsub_topic.simulation_report.id
    failure_policy {
      retry = false
    }
  }

  environment_variables = {
    PRICES_MINUTELY = "${google_bigquery_dataset.stocks.dataset_id}.prices_minutely_resampled"
    TRADES_TABLE    = "${google_bigquery_dataset.stocks.dataset_id}.${google_bigquery_table.simulated_trades.table_id}"
    PROJECT_ID      = var.project_id
    CHANNEL_ID      = var.trading_channel_id
  }

  secret_environment_variables {
    key     = "WEBHOOK"
    secret  = var.secret_trading_webhook
    version = "latest"
  }

  secret_environment_variables {
    key = "AUTH_TOKEN"
    secret = var.bot_auth_token
    version = "latest"
  }
}
