GRANT CONNECT ON DATABASE dwh TO airflow_datawarehouse;

GRANT USAGE ON SCHEMA gen TO airflow_datawarehouse;
GRANT USAGE ON SCHEMA gen_stg TO airflow_datawarehouse;

GRANT SELECT, TRUNCATE, INSERT, UPDATE ON ALL TABLES IN SCHEMA gen TO airflow_datawarehouse;
GRANT SELECT, TRUNCATE, INSERT, UPDATE ON ALL TABLES IN SCHEMA gen_stg TO airflow_datawarehouse;

GRANT USAGE ON SEQUENCE gen.conversations_segments_id_seq TO airflow_datawarehouse;

GRANT USAGE ON SEQUENCE gen_stg.conversations_segments_id_seq TO airflow_datawarehouse;

GRANT CONNECT ON DATABASE dwh TO querytool;

GRANT USAGE ON SCHEMA gen TO querytool;
GRANT USAGE ON SCHEMA gen_stg TO querytool;

GRANT SELECT ON ALL TABLES IN SCHEMA gen TO querytool;
GRANT SELECT ON ALL TABLES IN SCHEMA gen_stg TO querytool;