{% macro incremental_sentence(source_col='timestamp', alt_table_col=None, filter_clause=True, timestamp_type='timestamp', lookback="7") -%}

  {% set table_col = alt_table_col or source_col %}

  {% if timestamp_type == 'date' %}
      {{ source_col + " > DATE_SUB(CURRENT_DATE(), INTERVAL " + lookback + " DAY)" }}
  {% else %}
      {{ source_col + " > DATE_SUB(CURRENT_TIMESTAMP(), INTERVAL " + lookback + " DAY)" }}
  {% endif %}

    AND

    {{ source_col }} >

    {% if timestamp_type == 'date' %}
      {{
        find_max_timestamp(
          ref=this,
          column=table_col,
          filter_clause=table_col + " > DATE_SUB(CURRENT_DATE(), INTERVAL " + lookback + " DAY)" if filter_clause else None,
          timestamp_type=timestamp_type
        )
      }}
    {% else %}
      {{
        find_max_timestamp(
          ref=this,
          column=table_col,
          filter_clause=table_col + " > DATE_SUB(CURRENT_TIMESTAMP(), INTERVAL " + lookback + " DAY)" if filter_clause else None,
          timestamp_type=timestamp_type
        )
      }}
    {% endif %}

  {%- endmacro %}


{% macro find_max_timestamp(ref, column, filter_clause=None, timestamp_type='timestamp') -%}

  (
    SELECT
      MAX({{ column }}) as x
    FROM
      {{ ref }}
    {% if filter_clause %}
      WHERE
        {{ filter_clause}}
    {% endif %}
   )

{%- endmacro %}