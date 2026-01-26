x = int(input())

def func():
    global x
    x += 5
func()
print(x)