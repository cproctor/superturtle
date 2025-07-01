from superturtle.animation import animate
from turtle import *

def square(side_length):
    for side in range(4):
        forward(side_length)
        right(90)

for frame in animate(60, loop=True, gif_filename="../animated_square_1.gif"):
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
