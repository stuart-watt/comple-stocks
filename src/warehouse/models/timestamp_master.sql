SELECT DISTINCT
  DATE(`timestamp`) as `date`,
  TIMESTAMP_TRUNC(`timestamp`, HOUR) AS `timestamp`
FROM
  {{ source("stocks", "prices_hourly") }}
ORDER BY `timestamp`
