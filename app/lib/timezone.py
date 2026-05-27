from datetime import datetime
from zoneinfo import ZoneInfo

BOGOTA_TZ = ZoneInfo("America/Bogota")


def now_bogota() -> datetime:
    """Fecha y hora actual en Bogotá, Colombia (America/Bogota)."""
    return datetime.now(BOGOTA_TZ).replace(tzinfo=None)
