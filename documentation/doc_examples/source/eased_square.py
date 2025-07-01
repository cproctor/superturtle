from superturtle.animation import animate
from turtle import forward, right
from superturtle.easing import easeOutBounce

def rect(width, height):
    for i in range(2):
        forward(width)
        right(90)
        forward(height)
        right(90)

for frame in animate(60, loop=True, gif_filename="../eased_square.gif"):
    with frame.translate([-100, 50], [100, 50], easing=easeOutBounce):
        width = frame.interpolate(100, 40, easing=easeOutBounce)
        rect(width, 100)
