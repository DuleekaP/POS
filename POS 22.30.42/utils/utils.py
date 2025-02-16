import datetime

def format_date(date):
    """Format a datetime object into a readable string."""
    return date.strftime("%Y-%m-%d")

def validate_positive_integer(value):
    """Check if a value is a positive integer."""
    if not isinstance(value, int) or value <= 0:
        raise ValueError("Value must be a positive integer.")