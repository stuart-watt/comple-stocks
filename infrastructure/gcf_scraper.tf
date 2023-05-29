data "archive_file" "scraper_source" {
    type        = "zip"
    source_dir  = "../src/stock_scraper"
    output_path = "/tmp/scraper.zip"
}

resource "google_storage_bucket_object" "scraper_archive" {
  content_type = "application/zip"
  bucket = google_storage_bucket.artifacts.name
  source = data.archive_file.scraper_source.output_path

  name   = "scraper-${data.archive_file.scraper_source.output_md5}.zip"
}

resource "google_cloudfunctions_function" "stock_scraper" {
  name        = "stock-scraper"
  description = "Scrapes all ASX stock prices from Yahoo finance"
  runtime     = "python39"

  
  source_archive_bucket = google_storage_bucket.artifacts.name
  source_archive_object = google_storage_bucket_object.scraper_archive.name

  timeout               = 540
  available_memory_mb   = 1024
  max_instances         = 1

  entry_point           = "main"

  event_trigger {
    event_type = "google.pubsub.topic.publish"
    resource   = google_pubsub_topic.hourly.id
    failure_policy {
      retry = false
    }
  }

  environment_variables = {
    LISTED_COMPANIES_URL = "https://asx.api.markitdigital.com/asx-research/1.0/companies/directory/file",
    COMPANIES_TABLE      = "${google_bigquery_dataset.stocks.dataset_id}.${google_bigquery_table.listed_companies.table_id}"
    PRICES_TABLE         = "${google_bigquery_dataset.stocks.dataset_id}.${google_bigquery_table.prices.table_id}"
    START_DATE           = "2023-01-01"
    INTERVAL             = "1h"
    PROJECT_ID           = var.project_id
  }
}
