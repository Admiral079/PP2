#1
f = open("test.txt", "w")
f.write("Hello\n")
f.close()

#2
with open("test.txt", "a") as f:
    f.write("World\n")
    
#3
with open("numbers.txt", "w") as f:
    for i in range(5):
        f.write(str(i) + "\n")
        
#4
from pathlib import Path
Path("file.txt").write_text("Text data")

#5
with open("data.txt", "w") as f:
    f.writelines(["a\n", "b\n", "c\n"])