from collections import namedtuple

Point = namedtuple('Point', ['x', 'y'])

class Rect:
    """Rectangle class"""
    def __init__(self, left=0, top=0, right=0, bottom=0):
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom
        self.original_left = left
        self.original_right = right

    @property
    def width(self):
        return self.right - self.left

    @property
    def height(self):
        return self.top - self.bottom

    @width.setter
    def width(self, width):
        self.right = self.left + width

    @height.setter
    def height(self, height):
        self.top = self.bottom + height

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

    def contains_point(self, point):
        x = point[0]
        y = point[1]
        return self.left <= x <= self.right and self.bottom <= y <= self.top