#1
import shutil
shutil.move("file.txt", "dir/")

#2
shutil.copy("file.txt", "dir/")

#3
import os
files = os.listdir(".")
print([f for f in files if f.endswith(".txt")])

#4
from pathlib import Path
for f in Path(".").glob("*.txt"):
    print(f)
    
#5
import shutil
shutil.copytree("a", "b")