data "archive_file" "discord_poll_source" {
    type        = "zip"
    source_dir  = "../src/discord_poll/discord_poll"
    output_path = "/tmp/discord_poll.zip"
}

resource "google_storage_bucket_object" "discord_poll_archive" {
  content_type = "application/zip"
  bucket = google_storage_bucket.artifacts.name
  source = data.archive_file.discord_poll_source.output_path

  name   = "discord-poll-${data.archive_file.discord_poll_source.output_md5}.zip"
}

resource "google_cloudfunctions_function" "discord-poll" {
  name        = "discord-poll"
  description = "Polls discord for messages and commands"
  runtime     = "python39"

  
  source_archive_bucket = google_storage_bucket.artifacts.name
  source_archive_object = google_storage_bucket_object.discord_poll_archive.name

  timeout               = 60
  available_memory_mb   = 128
  max_instances         = 1

  entry_point           = "main"

  event_trigger {
    event_type = "google.pubsub.topic.publish"
    resource   = google_pubsub_topic.discord_poll.id
    failure_policy {
      retry = false
    }
  }

  environment_variables = {
    PROJECT_ID = var.project_id
    CHANNEL_ID = var.trading_channel_id
    TOPIC      = google_pubsub_topic.trade_simulator.id
  }

  secret_environment_variables {
    key = "AUTH_TOKEN"
    secret = var.bot_auth_token
    version = "latest"
  }
}
