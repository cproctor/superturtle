from superturtle.image import save
from superturtle.easing import easeOutCubic, easeInCubic
from superturtle.movement import no_delay, fly
from static import interpolate
from turtle import *

def square(side_length):
    for side in range(4):
        forward(side_length)
        right(90)

FRAMES = 40
pensize(2)
for t in range(FRAMES):
    c = interpolate(t, FRAMES, 0.8, 0, easeInCubic)
    c1 = interpolate(t, FRAMES, 0.5, 0)
    color((c, c, c))
    with no_delay():
        fly(0, 0)
        seth(0)
        θ = interpolate(t, FRAMES, 0, 360)
        left(θ)
        penup()
        forward(100)
        pendown()
        square(40)
        θ2 = interpolate(t, FRAMES, 0, 720)
        left(θ2)
        penup()
        forward(60)
        pendown()
        color((0, 1-c1, 0.5 + c1))
        square(20)

save("../animated_square_1.jpg")
