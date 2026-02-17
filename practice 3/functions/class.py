class Car:
    def __init__(self, brand, speed):
        self.brand = brand
        self.speed = speed

    def accelerate(self, value):
        self.speed += value


car1 = Car("Toyota", 100)
car1.accelerate(20)

print(car1.speed)  # 120