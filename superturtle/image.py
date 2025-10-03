# image.py
# ----------------------
# By Chris Proctor
#

from turtle import getcanvas, Turtle
from pathlib import Path
from subprocess import run
from svg_turtle import SvgTurtle

def save(filename):
    """
    Saves the canvas as a raster-based image, comparable to taking a screenshot.
    Suitable file extensions include .png and .jpg. 

    Arguments:
        filename (str): Location to save the file, including file extension.
    """
    temp_file = Path("_temp.eps")
    getcanvas().postscript(file=temp_file)
    cmd = f"magick {temp_file} -colorspace RGB {filename}"
    run(cmd, shell=True, check=True)
    temp_file.unlink()

class save_svg:
    """
    A context manager which saves turtle drawing in SVG format.
    Drawing within this context manager will be saved to the SVG file, and will
    not draw on the screen. You can use `dryrun=True` to draw to the screen instead
    of to the SVG file while you develop your drawing.

    The specified width and height define the SVG's viewBox, centered on 
    (0, 0). Anything outside of this area will be cut off. 
    If you are planning to draw the resulting SVG with a pen plotter, 
    keep in mind that 1 inch == 96 pixels. A standard sheet of paper (8.5" by 11")
    is 816 px by 1056 px. 

    It can helpful to set the turtle's canvas to the same size as your drawing 
    so that you can see how your drawing fits on the page. To do this, use turtle's
    `setup(width, height)` function to set the window size and 
    `screensize(width, height)` function to set the canvas size. It helps to add a 
    couple of extra pixels to the window size to avoid getting scroll bars.

    Arguments:
        width (int): Width of resulting SVG file in pixels.
        height (int): Height of resulting SVG file in pixels.
        filename (str): Location to save resulting SVG.
        dryrun (bool): (Optional) Disable saving to SVG and draw to the screen instead.

    ::

        from turtle import circle, setup, screensize
        from superturtle.image import save_svg

        width, height = 816, 1056
        setup(width + 2, height + 2)
        screensize(width, height)

        with save_svg(width, height, "image.svg"):
            circle(100)
    """
    def __init__(self, width, height, filename, dryrun=False):
        self.dryrun = dryrun
        self.svg_turtle = SvgTurtle(width, height)
        self.filename = filename
    def __enter__(self):
        if not self.dryrun:
            Turtle._pen = self.svg_turtle
    def __exit__(self, type, value, traceback):
        if not self.dryrun:
            self.svg_turtle.save_as(self.filename)
            Turtle._pen = None

