from pika.exchange_type import ExchangeType

COMMANDS_EXCHANGE = "external.researches.exchange"
COMMANDS_EXCHANGE_TYPE = ExchangeType.direct

RK_PAPERS_INGEST_REQUESTED = "external.researches.fetch"

DJANGO_REPLY_QUEUE = "django.enrichment.results.queue"
SYSTEM2_INGEST_QUEUE = "external.researches.queue"

DEAD_LETTER_EXCHANGE = "external.researches.dlx"
DEAD_LETTER_ROUTING_KEY = "external.researches.RK"
DEAD_LETTER_QUEUE = "external.researches.dlq"
