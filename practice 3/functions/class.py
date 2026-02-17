class Employee:
    def work(self):
        return "Working"

class Manager(Employee):
    def work(self):
        base = super().work()
        return base + " Managing team."

m = Manager()
print(m.work())