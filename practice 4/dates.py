from datetime import datetime, timezone, timedelta

tz = timezone(timedelta(hours=5))
now = datetime.now(tz)

print(now)