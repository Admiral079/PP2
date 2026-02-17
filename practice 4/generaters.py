def my_generator():
    yield 1
    yield 2
    yield 3


gen = my_generator()

print(next(gen))
print(next(gen))
print(next(gen))