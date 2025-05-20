from django import template
from datetime import datetime
import pytz

register = template.Library()

@register.filter
def iso_to_local_datetime(value, tz_name='America/Mexico_City'):
    try:
        dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
        utc_dt = dt.astimezone(pytz.utc)
        local_tz = pytz.timezone(tz_name)
        local_dt = utc_dt.astimezone(local_tz)
        return local_dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return value