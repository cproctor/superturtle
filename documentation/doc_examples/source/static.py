def interpolate(t, total, start, end, easing=None):
    r = t/total
    if easing:
        r = easing()(r)
    return start + r * (end - start)
