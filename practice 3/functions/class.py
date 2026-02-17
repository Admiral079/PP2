class Student:
    university = "KBTU"

    def __init__(self, name):
        self.name = name


s1 = Student("Aman")
s2 = Student("Bob")

print(s1.university)
print(s2.university)