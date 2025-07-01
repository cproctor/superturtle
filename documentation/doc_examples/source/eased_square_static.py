from superturtle.image import save
from superturtle.animation import animate
from turtle import forward, right, pensize, color
from superturtle.easing import easeOutBounce
from superturtle.easing import easeOutCubic, easeInExpo, easeOutExpo
from superturtle.movement import no_delay, fly
from static import interpolate

def rect(width, height):
    for i in range(2):
        forward(width)
        right(90)
        forward(height)
        right(90)

FRAMES = 80
pensize(2)

for t in range(FRAMES):
    c = interpolate(t, FRAMES, 0.9, 0.2, easeInExpo)
    x = interpolate(t, FRAMES, -200, 100, easeOutBounce)
    y = interpolate(t, FRAMES, 200, -200)
    w = interpolate(t, FRAMES, 100, 40, easeOutBounce)
    print(t, x, w, c)
    color((c, c, c))
    with no_delay():
        fly(x, y)
        rect(w, 100)

save("../eased_square.jpg")
