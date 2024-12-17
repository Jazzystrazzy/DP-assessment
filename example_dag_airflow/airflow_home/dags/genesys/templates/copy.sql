TRUNCATE TABLE {{ params.schema }}.{{ params.table }};

COPY {{ params.schema }}.{{ params.table }} (
    {{ params.fields | join(', ') }}
) FROM STDIN WITH CSV HEADER DELIMITER AS ';' QUOTE AS '"';