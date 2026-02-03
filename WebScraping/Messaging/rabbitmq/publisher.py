import json
import uuid
import pika
from .connection import get_connection, setup_channel
from .config import COMMANDS_EXCHANGE


def publish_message(
    routing_key: str,
    payload: dict,
    correlation_id: str | None = None,
    host: str = "localhost"
) -> str:

    if correlation_id is None:
        correlation_id = str(uuid.uuid4())

    connection = get_connection(host)
    channel = setup_channel(connection)

    channel.basic_publish(
        exchange=COMMANDS_EXCHANGE,
        routing_key=routing_key,
        body=json.dumps(payload).encode("utf-8"),
        properties=pika.BasicProperties(
            content_type="application/json",
            delivery_mode=2,
            correlation_id=correlation_id,
        ),
    )

    connection.close()

    return correlation_id
