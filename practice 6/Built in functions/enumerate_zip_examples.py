#1
a = ["a", "b", "c"]
for i, v in enumerate(a):
    print(i, v)
    
#2
a = [1, 2, 3]
b = [4, 5, 6]
for x, y in zip(a, b):
    print(x + y)
    
#3
names = ["A", "B"]
scores = [10, 20]
print(dict(zip(names, scores)))

#4
a = ["x", "y", "z"]
print(list(enumerate(a)))

#5
a = [3, 1, 2]
print(sorted(a))