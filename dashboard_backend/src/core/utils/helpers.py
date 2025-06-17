from datetime import datetime


def c_to_f(t):
    # Convert Celsius to Fahrenheit
    return round(((9.0 / 5.0) * t + 32.0), 1)


def convert_datetime_to_str(datetime: datetime, format: str):
    """Convert date to date string with specific date format."""
    try:
        return datetime.strftime(format)
    except Exception:
        return None


def get_current_time(time_zone):
    """Get current time in specific time zone."""
    return datetime.now(time_zone)
