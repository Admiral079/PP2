class Person:
    def __init__(self, name):
        self.name = name

    def introduce(self):
        return f"My name is {self.name}"

class Student(Person):
    def __init__(self, name, gpa):
        super().__init__(name)
        self.gpa = gpa

    def introduce(self):
        return f"My name is {self.name}, GPA: {self.gpa}"

s = Student("Aman", 3.8)
print(s.introduce())