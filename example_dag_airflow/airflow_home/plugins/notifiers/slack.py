from __future__ import annotations

from functools import cached_property
from typing import Any

from airflow.notifications.basenotifier import BaseNotifier
from airflow.providers.slack.hooks.slack_webhook import SlackWebhookHook

ICON_URL: str = "https://raw.githubusercontent.com/apache/airflow/2.6.0/airflow/www/static/pin_100.png"


class SlackWebhookNotifier(BaseNotifier):
    """Slack Webhook Notifier.

    Args:
        conn_id: Slack connection id.
        text: The formatted text of the message to be published.
        channel: The channel the message should be posted to.
        username: The username to post to slack with.
        icon_url: The icon image URL string to use in place of the default icon.
        attachments: The attachments to send on Slack. Should be a list of
            dictionaries representing Slack attachments.
        blocks: The blocks to send on Slack. Should be a list of
    """

    template_fields = ("text", "channel", "username", "attachments", "blocks")

    def __init__(
        self,
        *,
        conn_id: str = "slack_api_default",
        text: str = "Hey, I'm using slack!",
        channel: str = "general",
        username: str = "Airflow",
        icon_url: str = ICON_URL,
        attachments: list[dict[str, Any]] | None = None,
        blocks: list[dict[str, Any]] | None = None,
    ):
        super().__init__()
        self.conn_id = conn_id
        self.text = text
        self.channel = channel
        self.username = username
        self.icon_url = icon_url
        self.attachments = attachments
        self.blocks = blocks

    @cached_property
    def hook(self) -> SlackWebhookHook:
        """Slack webhook Hook."""
        return SlackWebhookHook(slack_webhook_conn_id=self.conn_id)

    def notify(self, context: Any) -> None:
        """Send a message to a Slack Channel."""
        self.hook.send(
            text=self.text,
            attachments=self.attachments,
            blocks=self.blocks,
            channel=self.channel,
            username=self.username,
            icon_url=self.icon_url,
        )


def failure_slack_alert(conn_id: str) -> SlackWebhookNotifier:
    """A standard slack message to be send when a DAG-task fails.

    Function can be referenced in the on_failure_callback parameter of a DAG.
    """
    slack_msg = (
        ":red_circle: Task Failed.\n"
        "\t\t*Task id*: {{ ti.task_id }}\n"
        "\t\t*Dag id*: {{ ti.dag_id }}\n"
        "\t\t*Run id*: {{ ti.run_id }}\n"
        "\t\t*Execution Date*: {{ ti.execution_date }}"
    )

    return SlackWebhookNotifier(
        conn_id=conn_id,
        channel="van-wezel-airflow-messages",
        text=slack_msg,
    )
