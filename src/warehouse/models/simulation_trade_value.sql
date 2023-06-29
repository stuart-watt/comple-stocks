{{
  config(
    partition_by = {
      "field": "timestamp",
      "data_type": "timestamp",
      "granularity": "day"
    }
  )
}}

WITH

  trades AS (
    SELECT
      `timestamp`,
      author_name,
      UPPER(symbol) as symbol,
      volume,
      cash_volume,
      stock_volume,
      brokerage,
      balance
    FROM
      {{ source("stocks", "simulated_trades") }}
  ),

  spine AS (
    SELECT 
      author_name,
      symbol, 
      `timestamp`, 
      price 
    FROM 
      {{ ref("prices_minutely_resampled") }}
    JOIN
      (SELECT DISTINCT author_name, symbol FROM trades)
    USING
      (symbol)
    WHERE 
      `timestamp` >= (SELECT MIN(`timestamp`) FROM trades)
  ),

  trades_on_spine AS (
    SELECT
      author_name,
      symbol, 
      `timestamp`,
      price,
      COALESCE(volume, 0) as volume,
      COALESCE(cash_volume, 0) as cash_volume,
      COALESCE(stock_volume, 0) as stock_volume,
      COALESCE(brokerage, 0) as brokerage,
      COALESCE(
        LAST_VALUE(balance IGNORE NULLS) OVER (
          PARTITION BY author_name, symbol
          ORDER BY `timestamp`
        ), 
      0) as balance
    FROM
      spine LEFT JOIN trades USING (author_name, symbol, `timestamp`)
  )

SELECT
  author_name,
  symbol, 
  `timestamp`,
  price,
  volume,
  cash_volume,
  stock_volume,
  brokerage,
  balance,
  IF(symbol = "$AUD", 0, balance * price) as stock_balance_value,
  IF(symbol = "$AUD", 0, stock_volume * price) as stock_volume_value,
  cash_volume - stock_volume * price - brokerage as cash_flow
FROM
  trades_on_spine
