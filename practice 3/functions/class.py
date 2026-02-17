class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        return "Some sound"

class Dog(Animal):
    pass

d = Dog("Buddy")
print(d.name)
print(d.speak())