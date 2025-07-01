from superturtle.animation import animate
from turtle import forward, right

def square(side_length):
    for side in range(4):
        forward(side_length)
        right(90)

for frame in animate(40, loop=True, gif_filename="../animated_square_0.gif"):
    size = frame.interpolate(50, 100, mirror=True)
    square(size)

