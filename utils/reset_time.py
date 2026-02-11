import pytz
from datetime import datetime, time, timedelta, date

tz = pytz.timezone("America/Chicago")


def get_server_now():
    return datetime.now(tz)

def get_today_date():
    return datetime.now(pytz.UTC).astimezone(tz).strftime("%Y-%m-%d")

def get_next_reset():
    now = datetime.now(tz)
    naive_midnight = datetime.combine(now.date(), time(0,0))
    midnight = tz.localize(naive_midnight)
    next_reset = midnight + timedelta(days=1)
    return next_reset

def get_game_day_index(start_date):
    today = get_server_now().date()
    days = (today - start_date).days
    print("Days: ",days)
    return days