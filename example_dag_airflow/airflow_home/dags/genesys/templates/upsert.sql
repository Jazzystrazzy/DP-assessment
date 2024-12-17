{%- macro comma_separated_list(items, alias = None) -%}
    {%- for item in items %}{% if alias %}{{ alias }}.{% endif %}{{ item }}{% if not loop.last %}, {% endif %}{% endfor -%}
{%- endmacro -%}


INSERT INTO {{ params.production_schema }}.{{ params.table }}
({{ comma_separated_list(params.fields) }}) 
SELECT {{ comma_separated_list(params.fields) }}
FROM {{ params.staging_schema }}.{{ params.table }}
ON CONFLICT ({{ comma_separated_list(params.key) }})
DO 
   UPDATE SET 
   {%- for field in params.fields %}
   {{ field }} = EXCLUDED.{{ field }}{% if not loop.last %},{% endif %}
   {%- endfor %};