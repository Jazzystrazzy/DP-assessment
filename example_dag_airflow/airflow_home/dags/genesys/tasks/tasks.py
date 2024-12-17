import logging
from collections.abc import Callable
from typing import Any

import pandas as pd
import pendulum
from airflow.decorators import task
from genesys.tasks.helpers import (
    download_df_from_ADLS,
    extract_call_logs,
    extract_contacts,
    extract_users,
    initialize_api_client,
    load_secrets,
    transform_df,
    upload_df_to_ADLS,
)

task_logger = logging.getLogger("airflow.task")


@task.short_circuit(
    retries=1,
    execution_timeout=pendulum.duration(minutes=5),
    retry_delay=pendulum.duration(minutes=5),
)
def extract_data(conn_config, endp_config, endpoint) -> bool:
    """Extracts data from Genesys endpoints and stores it as csv in blob storage."""
    # Create and configure client
    api_client = initialize_api_client(load_secrets(conn_config["secrets"]))
    params = endp_config[endpoint]["params"]
    # Dispatcher mapping endpoints to their respective functions
    endpoint_dispatcher: dict[
        str,
        Callable[
            [Any, dict], pd.DataFrame | tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]
        ],
    ] = {
        "call_logs": extract_call_logs,
        "contacts": extract_contacts,
        "users": extract_users,
    }

    # Call extraction function based on the endpoint, returns one or more dataframes.
    result = endpoint_dispatcher[endpoint](api_client, params)
    first_filesystem = conn_config["adls"]["first_filesystem"]
    wasb_conn_id = conn_config["adls"]["conn_id"]

    # Check if result contains one or more dataframes.
    if isinstance(result, tuple):
        # If so, get all output names for these dataframes and store them in a list.
        df_names = list(endp_config["call_logs"]["output"].keys())

        # Upload all dataframes to raw blob storage.
        for df_pos, df in enumerate(result):
            # Grab eacht output name and retrieve the blob name, then upload df to ADLS.
            blob_name = conn_config["adls"]["blob_path"][df_names[df_pos]]
            upload_df_to_ADLS(wasb_conn_id, df, blob_name, first_filesystem)
        return True

    # If result only contains 1 df: upload single df to raw blob storage.
    elif isinstance(result, pd.DataFrame):
        blob_name = conn_config["adls"]["blob_path"][endpoint]
        upload_df_to_ADLS(wasb_conn_id, result, blob_name, first_filesystem)
        return True
    # If result contains no dataframes, or if dataframe is empty, skip rest of tasks.
    elif len(result) == 0:
        return False
    else:
        return False


@task(
    retries=1,
    execution_timeout=pendulum.duration(minutes=5),
    retry_delay=pendulum.duration(minutes=5),
)
def transform_data(conn_config, endp_config, endpoint):
    """Downloads, transforms, uploads dataframe to curated blob storage."""
    outputs = list(endp_config[endpoint]["output"].keys())

    wasb_conn_id = conn_config["adls"]["conn_id"]
    first_filesystem = conn_config["adls"]["first_filesystem"]
    second_filesystem = conn_config["adls"]["second_filesystem"]

    for output in outputs:
        blob_name = conn_config["adls"]["blob_path"][output]

        df = download_df_from_ADLS(wasb_conn_id, blob_name, first_filesystem)

        # Transforms report, after which it can be loaded to the dwh
        tr_df = transform_df(
            endp_config=endp_config,
            endpoint=endpoint,
            df=df,
        )

        upload_df_to_ADLS(wasb_conn_id, tr_df, blob_name, second_filesystem)
