import pytz
from datetime import datetime, time, timedelta, date

tz = pytz.timezone("America/Chicago")


def get_server_now():
    return datetime.now(tz)

def get_next_reset():
    now = datetime.now(tz)
    midnight = datetime.combine(now.date(), time(0,0), tzinfo=tz)
    next_reset = midnight + timedelta(days=1)
    return next_reset

def get_game_day_index(start_date):
    today = get_server_now().date()
    return (today - start_date).days