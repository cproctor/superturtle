# Helpers
# By Chris Proctor
# ----------------
# A mishmash of useful functions. Feel free to use these in your own projects if they are helpful to you.

# =============================================================================
# ! Advanced !
# =============================================================================
# This module contains some fancy code that we don't expect you to understand
# yet. That's ok--as long as we know how to use code, we don't have to
# understand everything about it. 
# Check out the documentation for documentation on how to use this code.

# Of course, if you want to dig into this module, feel free. You can ask a
# teacher about it if you're interested.
# =============================================================================

from turtle import *
from itertools import chain, cycle

def fly(x,y):
    """Moves the turtle to (x,y) without drawing.

    This is really just a simple shortcut for lifting the pen, 
    going to a position, and putting the pen down again. But it's such
    a commonly-used pattern that it makes sense to put it into a function.
    Here's an example::

        from turtle import setheading, forward
        from movement import fly
        from math import sin, cos, tau

        def to_radians(degrees):
            return degrees * (tau / 360)

        for angle in range(0, 360, 20):
            fly(50 * cos(to_radians(angle)), 50 * sin(to_radians(angle)))
            setheading(angle)
            forward(100)
    """
    penup()
    goto(x,y)
    pendown()

def update_position(x, y=None):
    """
    Updates the turtle's position, adding x to the turtle's current x and y to the
    turtle's current y. 
    Generally, this function should be called with two arguments, but it may
    also be called with a list containing x and y values::

        update_position(10, 20)
        update_position([10, 20])
    """
    if y is None:
        x, y = x
    current_x, current_y = position()
    penup()
    goto(x + current_x, y + current_y)
    pendown()

class restore_state_when_finished:
    """
    A context manager which records the turtle's position and heading
    at the beginning and restores them at the end of the code block.
    For example::

        from turtle import forward, right
        from helpers import restore_state_when_finished
        for angle in range(0, 360, 15):
            with restore_state_when_finished():
                right(angle)
                forward(100)
    """

    def __enter__(self):
        self.position = position()
        self.heading = heading()

    def __exit__(self, *args):
        penup()
        setposition(self.position)
        setheading(self.heading)
        pendown()

class no_delay:
    """A context manager which causes drawing code to run instantly.

       For example::

           from movement import fly, no_delay
        from turtle import forward, right
        fly(-150, 150)
        with no_delay():
            for i in range(720):
                forward(300)
                right(71)
        input()
    """

    def __enter__(self):
        self.n = tracer()
        self.delay = delay()
        tracer(0, 0)

    def __exit__(self, exc_type, exc_value, traceback):
        update()
        tracer(self.n, self.delay)

if __name__ == '__main__':
    from turtle import forward, right

    with no_delay():
        for i in range(10000):
            forward(300)
            right(181)
    input("That was fast!")
