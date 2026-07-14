# image.py
# ----------------------
# By Chris Proctor
#

from turtle import getcanvas, Turtle
from pathlib import Path
from subprocess import run
from superturtle.svg import SVGTurtle

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

    **SVG fidelity**

    ``turtle.circle()`` is normally approximated as a polygon. Inside
    ``save_svg``, circles and arcs (when ``steps`` is not given) are
    exported as true SVG ``<circle>`` or ``<path>`` arc elements.  Passing
    an explicit ``steps`` argument preserves the polygon-approximation
    behaviour, which is useful for drawing regular polygons.

    Fill regions (``turtle.fill()``, or ``begin_fill()``/``end_fill()``)
    are exported as closed SVG ``<polygon>`` elements whose ``fill``
    attribute carries the turtle fill color and whose ``stroke`` attribute
    carries the pen color.  This means the closed boundary is visible to a
    pen plotter as a single continuous path, and downstream tools such as
    Inkscape or vpype can apply hatch fills or other processing to the
    colored region.  Note that the line strokes drawn *inside* a fill
    region are merged into the polygon element and are not emitted as
    separate ``<polyline>`` elements.

    Arguments:
        width (int): Width of resulting SVG file in pixels.
        height (int): Height of resulting SVG file in pixels.
        filename (str): Location to save resulting SVG.
        dryrun (bool): (Optional) Disable saving to SVG and draw to the screen instead.
        group_colors (bool): (Optional) Group strokes by color in the SVG output,
            which makes color-based layer workflows in Inkscape and vpype easier.
            Defaults to True. Set to False to preserve strict draw order.

    ::

        from turtle import circle, forward, left, setup, screensize
        from superturtle.image import save_svg

        width, height = 816, 1056
        setup(width + 2, height + 2)
        screensize(width, height)

        with save_svg(width, height, "image.svg"):
            # Exported as a true SVG <circle>, not a polygon approximation.
            circle(100)

            # Filled square: exported as a closed <polygon> with fill and stroke.
            color("black", "red")
            with fill():
                for _ in range(4):
                    forward(80)
                    left(90)
    """
    def __init__(self, width, height, filename, dryrun=False, group_colors=True):
        self.dryrun = dryrun
        self.filename = filename
        self.group_colors = group_colors
        if not dryrun:
            self._svg_turtle = SVGTurtle(width, height)

    def __enter__(self):
        if not self.dryrun:
            Turtle._pen = self._svg_turtle
        return self

    def __exit__(self, type, value, traceback):
        if not self.dryrun:
            self._svg_turtle.save_as(self.filename, group_colors=self.group_colors)
            Turtle._pen = None
