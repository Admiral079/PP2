from datetime import datetime, timedelta

now = datetime.now()
future = now + timedelta(days=10)

print(future)