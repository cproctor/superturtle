from superturtle.image import save
from superturtle.movement import no_delay
from superturtle.easing import easeOutCubic, easeInCubic
from turtle import forward, right, color, pensize
from static import interpolate

def square(side_length):
    for side in range(4):
        forward(side_length)
        right(90)

FRAMES = 16
pensize(2)
with no_delay():
    for t in range(FRAMES):
        size = interpolate(t, FRAMES, 100, 200)
        c = interpolate(t, FRAMES, 1, 0, easeInCubic)
        color((c, c, c))
        square(size)

save("../animated_square_0.jpg")
