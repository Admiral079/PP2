class Ball:
    def __init__(self):
        self.x = 300
        self.y = 200
        self.radius = 25
        self.step = 20
        self.width = 600
        self.height = 400

    def move_up(self):
        if self.y - self.step - self.radius >= 0:
            self.y -= self.step

    def move_down(self):
        if self.y + self.step + self.radius <= self.height:
            self.y += self.step

    def move_left(self):
        if self.x - self.step - self.radius >= 0:
            self.x -= self.step

    def move_right(self):
        if self.x + self.step + self.radius <= self.width:
            self.x += self.step