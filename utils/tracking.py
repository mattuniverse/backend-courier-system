import secrets
from datetime import datetime


def generate_tracking_no() -> str:
    date_part = datetime.now().strftime("%Y%m%d")
    random_part = secrets.token_hex(3).upper()
    return f"CP{date_part}-{random_part}"
