class Father:
    def skills(self):
        return "Driving"

class Mother:
    def skills2(self):
        return "Cooking"

class Child(Father, Mother):
    pass

c = Child()
print(c.skills())
print(c.skills2())