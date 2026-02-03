import os
import sys
from pathlib import Path

# 1) add project root (where manage.py lives) to sys.path BEFORE importing django
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

# 2) set DJANGO_SETTINGS_MODULE
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ResearchesWebScrapingAPI.settings")

# (اختياري) تشخيص سريع
print("PROJECT_ROOT =", PROJECT_ROOT)
print("sys.path[0]  =", sys.path[0])
print("cwd          =", Path.cwd())

# 3) now import django and setup
import django
django.setup()

# ---- rest of your imports AFTER setup ----
from rabbitmq.consumers.ResearcherDataConsumer import start_reply_consumer


def handle_enrichment(msg, properties):
    print("===================================")
    print("Enrichment received:")
    print(msg)
    print("Correlation ID:", getattr(properties, "correlation_id", None))
    print("===================================")


def run():
    print("Starting Django Messaging Worker...")
    start_reply_consumer(handle_enrichment)


if __name__ == "__main__":
    run()
