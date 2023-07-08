{{
  config(
    materialized='view'
  )
}}

WITH

  trades AS (
    SELECT
      `timestamp`,
      author_name,
      UPPER(symbol) as symbol,
      `action`,
      cash_volume,
      stock_volume,
      brokerage,

      SUM(stock_volume) OVER (
        PARTITION BY author_name, symbol
        ORDER BY `timestamp`
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
      ) as stock_balance
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
      `action`,
      COALESCE(cash_volume, 0) as cash_volume,
      COALESCE(stock_volume, 0) as stock_volume,
      COALESCE(brokerage, 0) as brokerage,
      COALESCE(
        LAST_VALUE(stock_balance IGNORE NULLS) OVER (
          PARTITION BY author_name, symbol
          ORDER BY `timestamp`
        ), 
      0) as stock_balance
    FROM
      spine LEFT JOIN trades USING (author_name, symbol, `timestamp`)
  ),

  -- calculate an average buy price

  average_buy_prices AS (
    SELECT
      author_name,
      symbol, 
      `timestamp`,
      SAFE_DIVIDE(
        SUM(stock_volume * price) OVER (
          PARTITION BY author_name, symbol
          ORDER BY `timestamp`
          ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ),
        SUM(stock_volume) OVER (
          PARTITION BY author_name, symbol
          ORDER BY `timestamp`
          ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        )
      ) as average_buy_price
    FROM
      trades_on_spine
    WHERE (`action` = "buy" OR `action` IS NULL)
  ),

  -- Calculate balances

  trade_values AS (
    SELECT
      author_name,
      symbol, 
      `timestamp`,
      price,
      cash_volume,
      stock_balance,
      stock_balance * price as stock_balance_value,
      cash_volume - stock_volume * price - brokerage as cash_flow
    FROM
      trades_on_spine
  ),

  balances AS (
    SELECT
      author_name,
      symbol, 
      `timestamp`,
      price,

      SUM(cash_flow) OVER (
        PARTITION BY author_name
        ORDER BY `timestamp`, symbol DESC
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
      ) as cash_balance,

      SUM(cash_volume) OVER (
        PARTITION BY author_name
        ORDER BY `timestamp`, symbol DESC
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
      ) as cash_input_balance,

      stock_balance,
      stock_balance_value
    FROM
      trade_values
  )

SELECT 
  author_name,
  symbol, 
  `timestamp`,
  price,
  IF(symbol="$AUD", cash_balance, stock_balance) as balance,
  IF(symbol="$AUD", cash_balance, stock_balance_value) as balance_value,
  IF(symbol="$AUD", cash_input_balance, 0) as cash_input_balance,
  average_buy_price
FROM 
  balances
LEFT JOIN
  average_buy_prices
USING
  (author_name, symbol, `timestamp`)
