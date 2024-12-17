import logging
import tempfile
from typing import Any

import pandas as pd
import pendulum
import PureCloudPlatformClientV2
from airflow.models import Variable
from airflow.providers.microsoft.azure.hooks.wasb import WasbHook
from PureCloudPlatformClientV2.rest import ApiException

task_logger = logging.getLogger("airflow.task")


##################################Initialize client#####################################


def initialize_api_client(secrets: tuple) -> Any:
    """Initializes Genesys API client based on client_id and client_secret.

    Args:
        secrets: Tuple of client credentials secrets, fetched from Airflow Variables.

    Returns:
        Initialized and configured API client.
    """
    client = PureCloudPlatformClientV2

    region = client.PureCloudRegionHosts.eu_central_1
    client.configuration.host = region.get_api_host()

    token = client.api_client.ApiClient().get_client_credentials_token(
        client_id=secrets[0],
        client_secret=secrets[1],
    )

    client.configuration.access_token = token.access_token

    return client


def load_secrets(secret_id: str) -> tuple[str, str]:
    """Retrieves the secrets associated with the provided secret_id.

    Args:
        secret_id (str): The Airflow Variable ID of the secrets to retrieve.

    Returns:
        A tuple containing the client_id and client_secret.
    """
    secrets = Variable.get(secret_id, deserialize_json=True)
    client_id, client_secret = secrets["client_id"], secrets["client_secret"]

    return client_id, client_secret


#################################Call log extraction####################################


def extract_conversations(conversations: Any) -> pd.DataFrame:
    """Transforms call log data from the API response into conversations DataFrame.

    Args:
        conversations: The list of conversation entities from the API response.

    Returns:
        A pandas DataFrame containing the call id and details.
    """
    conversations_log = [
        {
            "id": conversation.conversation_id,
            "start_time": conversation.conversation_start,
            "end_time": conversation.conversation_end,
            "originating_direction": conversation.originating_direction,
        }
        for conversation in conversations
    ]
    return pd.DataFrame(conversations_log).drop_duplicates()


def extract_participants(conversations: Any) -> pd.DataFrame:
    """Transforms call log data from the API response into participants DataFrame.

    Args:
        conversations: The list of conversation entities from the API response.

    Returns:
        A pandas DataFrame containing the call id and participant details.
    """
    participants_per_call = [
        {
            "conversation_id": conversation.conversation_id,
            "id": participant.participant_id,
            "name": participant.participant_name,
            "purpose": participant.purpose,
            "team_id": participant.team_id,
            "user_id": participant.user_id,
            "session_id": session.session_id,
            "session_ani": session.ani,
            "session_dnis": session.dnis,
            "talk_time": next(
                (
                    metric.value
                    for metric in (session.metrics or [])
                    if metric.name == "tTalkComplete"
                ),
                None,
            ),
        }
        for conversation in conversations
        for participant in conversation.participants
        for session in participant.sessions
    ]
    return pd.DataFrame(participants_per_call)


def extract_segments(conversations: Any) -> pd.DataFrame:
    """Transforms call log data from the API response into segments DataFrame.

    Args:
        conversations: The list of conversation entities from the API response.

    Returns:
        A pandas DataFrame containing the call id and segment details.
    """
    segments_per_call = [
        {
            "conversation_id": conversation.conversation_id,
            "type": segment.segment_type,
            "start_time": segment.segment_start,
            "end_time": segment.segment_end,
            "session_id": session.session_id,
        }
        for conversation in conversations
        for participant in conversation.participants
        for session in participant.sessions
        if session.segments
        for segment in session.segments
    ]
    return pd.DataFrame(segments_per_call)


def transform_to_conversations_segments_participants(
    conversations,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Transforms call log data from the API response into segments DataFrame.

    Args:
        conversations: The list of conversation entities from the API response.

    Returns:
        A pandas DataFrame containing the call id and segment details.
    """
    df_conversations = extract_conversations(conversations)
    df_participants_per_call = extract_participants(conversations)
    df_segments_per_call = extract_segments(conversations)
    return df_conversations, df_participants_per_call, df_segments_per_call


def extract_call_logs(
    client: Any, params: dict
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Fetches and returns call log information from the ConversationsApi response.

    Args:
        client: An instance of the Genesys PureCloudPlatformClientV2 client.
        params: A config file containing parameters.

    Returns:
        A pandas DataFrame containing all requested call log information.
    """
    conv_api = client.ConversationsApi()
    query = client.ConversationQuery()
    query.paging = PureCloudPlatformClientV2.PagingSpec()

    query.interval = params["interval"]

    page_number = 1

    all_calls, all_participants, all_segments = [], [], []

    while page_number:
        try:
            query.paging.page_number = page_number
            api_response = conv_api.post_analytics_conversations_details_query(query)

            if api_response.conversations:
                calls_page, participants_page, segments_page = (
                    transform_to_conversations_segments_participants(
                        api_response.conversations
                    )
                )

                all_calls.append(calls_page)
                all_participants.append(participants_page)
                all_segments.append(segments_page)

                page_number += 1

            else:
                page_number = False

        except ApiException as e:
            task_logger.info(f"Exception when calling ConversationsApi: {e}")

    df_calls = pd.concat(all_calls, ignore_index=True)
    df_participants = pd.concat(all_participants, ignore_index=True)
    df_segments = pd.concat(all_segments, ignore_index=True)

    return df_calls, df_participants, df_segments


##################################Contact extraction####################################


def fetch_contacts_page(client: Any, limit: int, cursor: str) -> dict:
    """Fetch a single page of contacts from the API.

    Args:
        client: API client instance.
        limit: Number of records per page.
        cursor: Cursor for pagination.

    Returns:
        A dictionary containing the page of contacts and the next cursor.
    """
    try:
        response = client.ExternalContactsApi().get_externalcontacts_scan_contacts(
            limit=limit, cursor=cursor
        )
        return {
            "contacts": response,
            "next_cursor": response.cursors.after if response.cursors else None,
        }
    except ApiException as e:
        task_logger.info(
            f"Exception when calling get_externalcontacts_scan_contacts: {e}"
        )
        return {"contacts": [], "next_cursor": None}


def transform_contact_data(contacts: list[dict]) -> list[dict]:
    """Transforms contact data into a structured dictionary.

    Args:
        contacts: A list of contact entities.

    Returns:
        A list of dictionaries with structured contact data.
    """
    transformed = []
    for contact in contacts.entities:  # type: ignore
        contact_info = {
            "first_name": getattr(contact, "first_name", None),
            "last_name": getattr(contact, "last_name", None),
            "id": getattr(contact, "id", None),
            "email_work": getattr(contact, "work_email", None),
            "email_personal": getattr(contact, "personal_email", None),
            "phone_work": (
                getattr(contact.work_phone, "e164", None)
                if contact.work_phone
                else None
            ),
            "phone_mobile": (
                getattr(contact.cell_phone, "e164", None)
                if contact.cell_phone
                else None
            ),
        }
        transformed.append(contact_info)
    return transformed


def extract_contacts(client: Any, params: dict) -> pd.DataFrame:
    """Fetches and returns data from the ExternalContactsApi response.

    Args:
        client: An instance of the Genesys PureCloudPlatformClientV2 client.
        params: A config file containing parameters.

    Returns:
        A list of dictionaries with structured contact data.
    """
    params = params
    all_contacts = []
    # Cursor needs to be defined outside the while loop for pagination logic to work.
    cursor = params["cursor"]

    while True:
        page_data = fetch_contacts_page(client, params["limit"], cursor)
        contacts = page_data["contacts"]
        if not contacts:
            break  # Exit the loop if no contacts are returned

        transformed_contacts = transform_contact_data(contacts)
        all_contacts.extend(transformed_contacts)

        cursor = page_data["next_cursor"]
        if not cursor:
            break  # No more pages to fetch

    return pd.DataFrame(all_contacts)


###################################User extraction######################################


def extract_users(client: Any, params: dict) -> pd.DataFrame:
    """Fetches and returns information from the UserApi response.

    Args:
        client: An instance of the Genesys PureCloudPlatformClientV2 client.
        params: A config file containing parameters.

    Returns:
        A pandas dataframe containing all requested user information.
    """
    page_size = params["page_size"]
    users = client.UsersApi().get_users(page_size=page_size)
    all_users = []

    for user in users.entities:
        user_info = {}

        user_info["id"] = user.id
        user_info["name"] = user.name
        user_info["email"] = user.email

        if user.addresses:
            for item in user.addresses:
                addr = item.address
                # Categorize the address based on its content
                if addr is None:
                    pass
                elif addr.startswith("+316"):  # Mobile phone/non-geographic number
                    user_info["phone_mobile"] = addr
                else:  # Any other number is a work phone number
                    user_info["phone_work"] = addr
                # If 'addresses' is missing or empty, just continue to the next user

        else:
            continue

        all_users.append(user_info)

    return pd.DataFrame(all_users)


###################################DAG functions######################################


def download_df_from_ADLS(
    wasb_conn_id: str, blob_name: str, filesystem: str
) -> pd.DataFrame:
    """Transforms csv to dataframe and downloads it from blob storage to local scope.

    Args:
        wasb_conn_id: String representing WASB connection id.
        blob_name: Filepath to azure blob storage container.
        filesystem: Filesystem within storage container, either raw or curated.

    Returns:
        A pandas dataframe containing all requested user information.
    """
    wasb_hook = WasbHook(wasb_conn_id)

    with tempfile.NamedTemporaryFile() as temp_file:
        wasb_hook.get_file(
            file_path=temp_file.name,
            container_name=filesystem,
            blob_name=blob_name,
        )

        df = pd.read_csv(
            temp_file.name,
            sep=";",
            dtype={"phone_work": str, "phone_mobile": str},
            index_col=False,
        )

        task_logger.info(f"Downloaded dataframe from ADLS -> container: {filesystem}.")
        return df


def upload_df_to_ADLS(
    wasb_conn_id: str, df: pd.DataFrame, blob_name: str, filesystem: str
):
    """Transforms dataframe to csv and uploads it to raw blob storage.

    Args:
        wasb_conn_id: String representing WASB connection id.
        df: A pandas dataframe.
        blob_name: Filepath to azure blob storage container.
        filesystem: Filesystem within storage container, either raw or curated.

    Returns:
        A pandas dataframe containing all requested user information.
    """
    wasb_hook = WasbHook(wasb_conn_id)

    data = df.to_csv(  # type: ignore
        header=True,
        index=False,
        sep=";",
        na_rep="",
        lineterminator=None,
    )

    wasb_hook.upload(
        container_name=filesystem,
        blob_name=blob_name,
        data=data,
        overwrite=True,
    )
    task_logger.info(
        f"Uploaded {df} dataframe of length: {len(df)} to ADLS container: {filesystem}."
    )


######################################################################################
def strip_phone_number(series):
    """Takes a string, removes 'tel:' and returns final item."""
    if series.isnull().all():
        return series
    else:
        return series.apply(lambda x: x.replace("tel:", ""))


transform_functions = {
    "phone_number": strip_phone_number,
}


def transform_df(endp_config, endpoint, df):
    """Transforms report data into dataframe with correct column names."""
    df["dl_imported_at"] = str(pendulum.now())

    for output in endp_config[endpoint]["output"]:
        for column, transformation in endp_config[endpoint]["output"][output][
            "fields"
        ].items():
            if transformation != "nothing":
                func = transform_functions.get(transformation)
                if func and column in df:
                    df.loc[:, column] = func(df[column])
                else:
                    task_logger.info(
                        f"Function '{func}' not found or column '{column}' not in df."
                    )

    return df
