import pika
from .config import (
    COMMANDS_EXCHANGE,
    COMMANDS_EXCHANGE_TYPE,
    DJANGO_REPLY_QUEUE,
    SYSTEM2_INGEST_QUEUE,
    DEAD_LETTER_EXCHANGE,
    DEAD_LETTER_ROUTING_KEY,
    DEAD_LETTER_QUEUE,
)

def get_connection(host="rabbitmq"):
    params = pika.ConnectionParameters(host)
    return pika.BlockingConnection(params)

def setup_channel(connection: pika.BlockingConnection):
    ch = connection.channel()

    ch.exchange_declare(
        exchange=COMMANDS_EXCHANGE,
        exchange_type=COMMANDS_EXCHANGE_TYPE,
        durable=True
    )

    ch.exchange_declare(
        exchange=DEAD_LETTER_EXCHANGE,
        exchange_type=COMMANDS_EXCHANGE_TYPE,
        durable=True
    )

    ch.queue_declare(
        queue=DEAD_LETTER_QUEUE,
        durable=True
    )

    ch.queue_bind(
        queue=DEAD_LETTER_QUEUE,
        exchange=DEAD_LETTER_EXCHANGE,
        routing_key=DEAD_LETTER_ROUTING_KEY
    )

    ch.queue_declare(
        queue=SYSTEM2_INGEST_QUEUE,
        durable=True,
        arguments={
            "x-dead-letter-exchange": DEAD_LETTER_EXCHANGE,
            "x-dead-letter-routing-key": DEAD_LETTER_ROUTING_KEY,
        }
    )

    ch.queue_declare(queue=DJANGO_REPLY_QUEUE, durable=True)

    return ch
