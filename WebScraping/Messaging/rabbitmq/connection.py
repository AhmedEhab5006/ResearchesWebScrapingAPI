import pika
from .config import COMMANDS_EXCHANGE, COMMANDS_EXCHANGE_TYPE, DJANGO_REPLY_QUEUE

def get_connection(host="localhost"):
    params = pika.ConnectionParameters(host)
    return pika.BlockingConnection(params)

def setup_channel(connection: pika.BlockingConnection):
    ch = connection.channel()
    ch.exchange_declare(exchange=COMMANDS_EXCHANGE, exchange_type=COMMANDS_EXCHANGE_TYPE, durable=True)
    ch.queue_declare(queue=DJANGO_REPLY_QUEUE, durable=True)
    return ch
