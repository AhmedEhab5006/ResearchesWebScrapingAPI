import json
from ..connection import get_connection, setup_channel
from ..config import DJANGO_REPLY_QUEUE

def start_reply_consumer(on_enrichment_received, host="localhost"):
    connection = get_connection(host)
    channel = setup_channel(connection)

    def callback(ch, method, properties, body: bytes):
        msg = json.loads(body.decode("utf-8"))
        on_enrichment_received(msg, properties)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=DJANGO_REPLY_QUEUE, on_message_callback=callback, auto_ack=False)

    print("Django Reply Consumer started...")
    channel.start_consuming()
