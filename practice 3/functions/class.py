class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def greet(self):
        return f"Hello, my name is {self.name}"


p1 = Person("Aman", 18)
print(p1.greet())