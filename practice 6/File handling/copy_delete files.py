#1
import shutil
shutil.copy("test.txt", "copy.txt")

#2
import shutil
shutil.copyfile("test.txt", "backup.txt")

#3
import os
os.remove("copy.txt")

#4
from pathlib import Path
Path("backup.txt").unlink()

#5
import shutil
shutil.move("test.txt", "moved.txt")