from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent / "../.."))
print(Path(__file__).resolve().parent / "../..")
from turtle import (
    forward, 
    penup, 
    pendown,
    right, 
    setup,
    pensize,
    bgcolor,
)
from superturtle.stroke import (
    dashes,
    dots,
    rainbow,
)
from superturtle.image import save
from superturtle.movement import fly
from superturtle.animation import animate

def rect(width, height):
    for i in range(2):
        forward(width)
        right(90)
        forward(height)
        right(90)

def square(side_length):
    for side in range(4):
        forward(side_length)
        right(90)

def context_manager_example():
    setup(300, 100)
    pensize(4)
    fly(-150, 0)
    with dots():
        forward(200)
    save("context_manager.png")

def animated_square_0():
    setup(200, 200)
    for frame in animate(40, loop=True, gif_filename="animated_square_0.gif"):
        size = frame.interpolate(50, 100, mirror=True)
        fly(-50, 50)
        square(size)

def animated_square_1():
    setup(400, 400)
    for frame in animate(60, loop=True, gif_filename="animated_square_1.gif"):
        with frame.rotate(0, 360):
            penup()
            forward(100)
            pendown()
            square(40)
            with frame.rotate(0, 360, cycles=2):
                penup()
                forward(60)
                pendown()
                square(20)

def eased_square():
    from easing_functions.easing import BounceEaseOut
    setup(400, 200)
    for frame in animate(60, loop=True, gif_filename="eased_square.gif"):
        with frame.translate([-100, 50], [100, 50], easing=BounceEaseOut):
            width = frame.interpolate(100, 40, easing=BounceEaseOut)
            rect(width, 100)

#context_manager_example()
#animated_square_0()
#animated_square_1()
eased_square()
