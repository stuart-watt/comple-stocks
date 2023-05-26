data "archive_file" "messenger_source" {
    type        = "zip"
    source_dir  = "../src/messenger"
    output_path = "/tmp/messenger.zip"
}

resource "google_storage_bucket_object" "messenger_archive" {
  content_type = "application/zip"
  bucket = google_storage_bucket.artifacts.name
  source = data.archive_file.messenger_source.output_path

  name   = "messenger-${data.archive_file.messenger_source.output_md5}.zip"
}

resource "google_cloudfunctions_function" "discord_messenger" {
  name        = "discord-messenger"
  description = "Sends a message to Discord"
  runtime     = "python39"

  
  source_archive_bucket = google_storage_bucket.artifacts.name
  source_archive_object = google_storage_bucket_object.messenger_archive.name

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
    WEBHOOK = data.google_secret_manager_secret_version_access.webhook.secret_data
  }
}
