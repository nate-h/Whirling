from collections import namedtuple

Point = namedtuple('Point', ['x', 'y'])

class Rect:
    def __init__(self, left, top, right, bottom):
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom

    @property
    def width(self):
        return self.right - self.left

    @property
    def height(self):
        return self.top - self.bottom

    @property
    def position(self):
        return (self.left, self.bottom, 0)

    def translate(self, dx, dy):
        return Rect(self.left + dx, self.top + dy,
            self.right + dx, self.bottom + dy)

    def __str__(self):
        s = 'Left: %d, Top: %d, Right: %d, Bottom: %d Width: %d, Height: %d'
        return s % (self.left, self.top, self.right, self.bottom,
            self.width, self.height)
