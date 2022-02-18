# image.py
# ----------------------
# By Chris Proctor
#

from turtle import getcanvas
from pathlib import Path
from subprocess import run

def save(filename):
    """Saves the canvas as an image.

    Arguments:
        filename (str): Location to save the file, including file extension.
    """
    temp_file = Path("_temp.eps")
    getcanvas().postscript(file=temp_file)
    cmd = f"convert {temp_file} -colorspace RGB {filename}"
    run(cmd, shell=True, check=True)
    temp_file.unlink()

