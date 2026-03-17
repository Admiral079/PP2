#1
f = open("test.txt", "r")
print(f.read())
f.close()

#2
f = open("test.txt", "r")
print(f.readline())
f.close()

#3
f = open("test.txt", "r")
print(f.readlines())
f.close()

#4
with open("test.txt", "r") as f:
    for line in f:
        print(line.strip())
        
#5
from pathlib import Path
p = Path("test.txt")
print(p.read_text())