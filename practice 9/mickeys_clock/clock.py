import datetime

class Clock:
    def __init__(self):
        self.minutes = 0
        self.seconds = 0

    def update(self):
        now = datetime.datetime.now()
        self.minutes = now.minute
        self.seconds = now.second

    def get_minute_angle(self):
        return -(self.minutes * 6)

    def get_second_angle(self):
        return -(self.seconds * 6)