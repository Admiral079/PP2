#1
a = [1, 2, 3]
print(list(map(lambda x: x*x, a)))

#2
a = [1, 2, 3, 4]
print(list(filter(lambda x: x % 2 == 0, a)))

#3
from functools import reduce
a = [1, 2, 3, 4]
print(reduce(lambda x, y: x + y, a))

#4
a = ["1", "2", "3"]
print(list(map(int, a)))

#5
a = [0, 1, 2, 0, 3]
print(sum(map(bool, a)))