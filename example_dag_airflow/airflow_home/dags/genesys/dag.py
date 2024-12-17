import json
from datetime import timedelta
from pathlib import Path

import genesys.tasks.tasks as dag_tasks
import pendulum
from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator
from datalab.operators.sql.postgres.transfers.adls_to_postgres import (  # type: ignore
    ADLSToPostgresOperator,
)
from notifiers.slack import failure_slack_alert  # type: ignore

with (
    open("dags/genesys/configs/endpoints.json") as config1,
    open("dags/genesys/configs/connections.json") as config2,
):
    endpoints_config = json.load(config1)
    connections_config = json.load(config2)


def generate_genesys_dag(endpoint):
    """Generates a Genesys dag."""
    with DAG(
        dag_id=f"genesys_{endpoint}_etl_v1.0",
        max_active_runs=1,
        schedule=endpoints_config[endpoint]["schedule"],
        start_date=pendulum.datetime(2024, 1, 1, tz="Europe/Amsterdam"),
        tags=["genesys", "report", "etl", "call", "logs", "contacts", "users"],
        on_failure_callback=failure_slack_alert("slack_connection"),
        doc_md=__doc__,
        template_searchpath=str(Path("dags/genesys/templates").absolute()),
        catchup=False,
    ) as dag:

        extracted = dag_tasks.extract_data(
            conn_config=connections_config,
            endp_config=endpoints_config,
            endpoint=endpoint,
        )

        transformed = dag_tasks.transform_data(
            conn_config=connections_config,
            endp_config=endpoints_config,
            endpoint=endpoint,
        )

        extracted >> transformed

        for output, output_config in endpoints_config[endpoint]["output"].items():

            load_data_into_staging = ADLSToPostgresOperator(
                task_id=f"load_{output}_data_into_staging",
                postgres_conn_id=connections_config["dwh"]["conn_id"],
                adls_conn_id=connections_config["adls"]["conn_id"],
                adls_filesystem=connections_config["adls"]["second_filesystem"],
                filenames=connections_config["adls"]["blob_path"][output],
                copy_query="copy.sql",
                params={
                    "schema": connections_config["dwh"]["staging_schema"],
                    "table": output,
                    "fields": output_config["fields"],
                },
                retries=1,
                execution_timeout=timedelta(seconds=30),
                retry_delay=timedelta(minutes=5),
            )

            upsert_staging_into_main = PostgresOperator(
                task_id=f"upsert_{output}_staging_into_main",
                postgres_conn_id=connections_config["dwh"]["conn_id"],
                sql="upsert.sql",
                params={
                    "staging_schema": connections_config["dwh"]["staging_schema"],
                    "production_schema": connections_config["dwh"]["production_schema"],
                    "table": output,
                    "key": output_config["key"],
                    "fields": output_config["fields"],
                },
                retries=1,
                execution_timeout=timedelta(seconds=30),
                retry_delay=timedelta(minutes=5),
            )

            transformed >> load_data_into_staging >> upsert_staging_into_main

    return dag


for endpoint in endpoints_config:
    generate_genesys_dag(endpoint)
