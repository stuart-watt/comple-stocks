{{
  config(
    partition_by = {
      "field": "timestamp",
      "data_type": "timestamp",
      "granularity": "day"
    },
  )
}}

WITH

    prices AS (
    SELECT
      symbol,
      `timestamp` as exact_timestamp,
      DATETIME_TRUNC(`timestamp`, HOUR) as `timestamp`,
      `close` as price
    FROM
      {{ source("stocks", "prices_hourly")}}
  ),

  -- keep last value after rounding

  prices_numbered AS (
    SELECT
      symbol,
      `timestamp`,
      price,
      ROW_NUMBER() OVER (
        PARTITION BY symbol, `timestamp` 
        ORDER BY exact_timestamp DESC
      ) as rn
    FROM
      prices
  ),
 
  -------------------------------------
  -- Create a hourly timestamp spine --
  -------------------------------------

  trading_dates AS (
    SELECT DISTINCT
      DATE(`timestamp`) as `date`
    FROM
      prices
  ),

  timestamp_spine AS (
    SELECT
      `timestamp`,
      DATE(`timestamp`) as `date`
    FROM
      UNNEST(
        GENERATE_TIMESTAMP_ARRAY(
          (SELECT TIMESTAMP(MIN(`date`)) FROM trading_dates), 
          CURRENT_TIMESTAMP(),
          INTERVAL 1 HOUR
          )
      ) AS `timestamp`
    WHERE
      EXTRACT(TIME FROM `timestamp`) >= "00:00:00" AND EXTRACT(TIME FROM `timestamp`) <= "06:00:00" -- Trading hours of ASX in UTC+0
  ),

  timestamp_master AS (
    SELECT 
      * 
    FROM 
      timestamp_spine 
    JOIN 
      trading_dates -- this join removes non-trading days
    USING (`date`)
    ORDER BY `timestamp`
  ),

  -------------------------
  -- Create master spine --
  -------------------------

  stock_master AS (
    SELECT
      `timestamp`,
      symbol
    FROM
      timestamp_master,
      (SELECT DISTINCT symbol FROM prices UNION ALL SELECT "$AUD" as symbol) -- adds symbol for AUD
  ),

  new_prices AS (
    SELECT
      symbol,
      `timestamp`,
      LAST_VALUE(price IGNORE NULLS) OVER (
        PARTITION BY symbol 
        ORDER BY `timestamp`
      ) AS price
    FROM
      stock_master
    LEFT JOIN
      (SELECT * FROM prices_numbered WHERE rn = 1)
    USING (symbol, `timestamp`)
  )

SELECT 
  symbol,
  `timestamp`,
  COALESCE(price, 1) as price
FROM 
  new_prices 
