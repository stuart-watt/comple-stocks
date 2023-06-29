resource "google_bigquery_table" "prices_hourly" {
  dataset_id = google_bigquery_dataset.stocks.dataset_id
  table_id   = "prices_hourly"

  time_partitioning {
    type  = "DAY"
    field = "timestamp"
  }

  schema = <<EOF
  [
    {
      "name": "symbol",
      "type": "STRING",
      "mode": "NULLABLE",
      "description": "ASX company ticker"
    },
    {
      "name": "timestamp",
      "type": "TIMESTAMP",
      "mode": "NULLABLE",
      "description": "Timestamp"
    },
    {
      "name": "open",
      "type": "NUMERIC",
      "mode": "NULLABLE",
      "description": "Open price"
    },
    {
      "name": "close",
      "type": "NUMERIC",
      "mode": "NULLABLE",
      "description": "Close price"
    },
    {
      "name": "low",
      "type": "NUMERIC",
      "mode": "NULLABLE",
      "description": "Low price"
    },
    {
      "name": "high",
      "type": "NUMERIC",
      "mode": "NULLABLE",
      "description": "High price"
    },
    {
      "name": "volume",
      "type": "NUMERIC",
      "mode": "NULLABLE",
      "description": "Volume"
    }
  ]
  EOF
}

resource "google_bigquery_table" "prices_minutely" {
  dataset_id = google_bigquery_dataset.stocks.dataset_id
  table_id   = "prices_minutely"

  time_partitioning {
    type  = "DAY"
    field = "timestamp"
  }

  schema = <<EOF
  [
    {
      "name": "symbol",
      "type": "STRING",
      "mode": "NULLABLE",
      "description": "ASX company ticker"
    },
    {
      "name": "timestamp",
      "type": "TIMESTAMP",
      "mode": "NULLABLE",
      "description": "Timestamp"
    },
    {
      "name": "open",
      "type": "NUMERIC",
      "mode": "NULLABLE",
      "description": "Open price"
    },
    {
      "name": "close",
      "type": "NUMERIC",
      "mode": "NULLABLE",
      "description": "Close price"
    },
    {
      "name": "low",
      "type": "NUMERIC",
      "mode": "NULLABLE",
      "description": "Low price"
    },
    {
      "name": "high",
      "type": "NUMERIC",
      "mode": "NULLABLE",
      "description": "High price"
    },
    {
      "name": "volume",
      "type": "NUMERIC",
      "mode": "NULLABLE",
      "description": "Volume"
    }
  ]
  EOF
}

resource "google_bigquery_table" "listed_companies" {
  dataset_id = google_bigquery_dataset.stocks.dataset_id
  table_id   = "listed_companies"

  schema = <<EOF
  [
    {
      "name": "symbol",
      "type": "STRING",
      "mode": "NULLABLE",
      "description": "ASX company ticker"
    },
    {
      "name": "name",
      "type": "STRING",
      "mode": "NULLABLE",
      "description": "ASX company name"
    },
    {
      "name": "GIC",
      "type": "STRING",
      "mode": "NULLABLE",
      "description": "GICs industry group"
    },
    {
      "name": "listing_date",
      "type": "TIMESTAMP",
      "mode": "NULLABLE",
      "description": "Date listed"
    },
    {
      "name": "market_cap",
      "type": "NUMERIC",
      "mode": "NULLABLE",
      "description": "Market Cap"
    }
  ]
  EOF
}

resource "google_bigquery_table" "indices_hourly" {
  dataset_id = google_bigquery_dataset.stocks.dataset_id
  table_id   = "indices_hourly"

  time_partitioning {
    type  = "DAY"
    field = "timestamp"
  }

  schema = <<EOF
  [
    {
      "name": "symbol",
      "type": "STRING",
      "mode": "NULLABLE",
      "description": "ASX index symbol"
    },
    {
      "name": "timestamp",
      "type": "TIMESTAMP",
      "mode": "NULLABLE",
      "description": "Timestamp"
    },
    {
      "name": "open",
      "type": "NUMERIC",
      "mode": "NULLABLE",
      "description": "Open price"
    },
    {
      "name": "close",
      "type": "NUMERIC",
      "mode": "NULLABLE",
      "description": "Close price"
    },
    {
      "name": "low",
      "type": "NUMERIC",
      "mode": "NULLABLE",
      "description": "Low price"
    },
    {
      "name": "high",
      "type": "NUMERIC",
      "mode": "NULLABLE",
      "description": "High price"
    },
    {
      "name": "volume",
      "type": "NUMERIC",
      "mode": "NULLABLE",
      "description": "Volume"
    }
  ]
  EOF
}

resource "google_bigquery_table" "simulated_trades" {
  dataset_id = google_bigquery_dataset.stocks.dataset_id
  table_id   = "simulated_trades"

  time_partitioning {
    type  = "DAY"
    field = "timestamp"
  }

  schema = <<EOF
  [
    {
      "name": "id",
      "type": "STRING",
      "mode": "NULLABLE",
      "description": "Discord message ID"
    },
    {
      "name": "timestamp",
      "type": "TIMESTAMP",
      "mode": "NULLABLE",
      "description": "Timestamp rounded to next available minute during market open"
    },
    {
      "name": "timestamp_exact",
      "type": "TIMESTAMP",
      "mode": "NULLABLE",
      "description": "Exact timestamp of the discord message"
    },
    {
      "name": "content",
      "type": "STRING",
      "mode": "NULLABLE",
      "description": "The content of the message"
    },
    {
      "name": "author_id",
      "type": "STRING",
      "mode": "NULLABLE",
      "description": "The id of the author in Discord"
    },
    {
      "name": "author_name",
      "type": "STRING",
      "mode": "NULLABLE",
      "description": "The name of the author in Discord"
    },
    {
      "name": "action",
      "type": "STRING",
      "mode": "NULLABLE",
      "description": "The extracted action of the trade order [Buy, Sell, Add, Subtract]"
    },
    {
      "name": "volume",
      "type": "INTEGER",
      "mode": "NULLABLE",
      "description": "The volume of the action"
    },
    {
      "name": "symbol",
      "type": "STRING",
      "mode": "NULLABLE",
      "description": "The symbol of the action"
    },
    {
      "name": "stock_volume",
      "type": "INTEGER",
      "mode": "NULLABLE",
      "description": "The volume of the action if its a stock (Buy or Sell action)"
    },
    {
      "name": "cash_volume",
      "type": "INTEGER",
      "mode": "NULLABLE",
      "description": "The volume of the action if its cash (Add or Subtract action)"
    },
    {
      "name": "brokerage",
      "type": "INTEGER",
      "mode": "NULLABLE",
      "description": "The value of the brokerage fee"
    }
  ]
  EOF
}