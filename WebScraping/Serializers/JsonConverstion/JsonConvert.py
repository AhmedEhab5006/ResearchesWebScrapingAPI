import json
from datetime import date, datetime
from uuid import UUID
from decimal import Decimal

def to_jsonable(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()

    if isinstance(obj, UUID):
        return str(obj)

    if isinstance(obj, Decimal):
        return str(obj)

    if isinstance(obj, set):
        return list(obj)

    if hasattr(obj, "pk"):
        return str(obj.pk)

    raise TypeError(f"Type {type(obj).__name__} is not JSON serializable")
