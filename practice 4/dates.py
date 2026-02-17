from datetime import datetime, timezone

utc_now = datetime.now(timezone.utc)
print(utc_now)