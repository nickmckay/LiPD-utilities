import os
import tkinter as tk
from tkinter import filedialog
import sys

try:
    root = tk.Tk()
    root.withdraw()
    _path = filedialog.askopenfilenames(parent=root, initialdir=os.path.expanduser('~/Desktop'), title='Please select a file')
    root.update()
    print(str(_path))
    sys.stdout.flush()
except Exception as e:
    print("gui_file_browse.py error: {}".format(e))