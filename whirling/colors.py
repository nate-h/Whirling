# Basic colors.
WHITE = (1,1,1)
BLACK = (0,0,0)
RED = (1,0,0)
LIME = (0,1,0)
BLUE = (0,0,1)
YELLOW = (1,1,0)
SILVER = (0.75,0.75,0.75)
CYAN = (0,1,1)
MAGENTA = (1,0,1)
GOLD = (1,0.85,0)
CHARTREUSE = (0.5,1,0)
ORANGE_RED = (1,0.27,0)
VIOLET = (0.93,0.51,0.93)
HOT_PINK = (1,.08,0.58)
LAWN_GREEN = (0.48,0.98,0)
DEEP_SKY_BLUE = (0,0.75,1)
TEAL = (0,0.5,0.5)
PURPLE = (0.5,0,0.5)
OLIVE = (0.5,0.5,0)
GRAY = (0.5,0.5,0.5)
MAROON = (0.5,0,0)
GREEN = (0,0.5,0)
NAVY = (0,0,0.5)

# 4 channel colors.
CLEAR = (0,0,0,0)

# Convenient arrays to iterate on.
COLORS = {
    'RED': RED,
    'LIME': LIME,
    'BLUE': BLUE,
    'YELLOW': YELLOW,
    'SILVER': SILVER,
    'CYAN': CYAN,
    'MAGENTA': MAGENTA,
    'GOLD': GOLD,
    'CHARTREUSE': CHARTREUSE,
    'ORANGE_RED': ORANGE_RED,
    'LAWN_GREEN': LAWN_GREEN,
    'DEEP_SKY_BLUE': DEEP_SKY_BLUE,
    'VIOLET': VIOLET,
    'HOT_PINK': HOT_PINK,
    'TEAL': TEAL,
    'PURPLE': PURPLE,
    'OLIVE': OLIVE,
    'GRAY': GRAY,
    'MAROON': MAROON,
    'GREEN': GREEN,
    'NAVY': NAVY,
}


def color4f(color):
    if len(color) not in [3, 4]:
        print('Not valid color.')
        return CLEAR
    if len(color) == 4:
        return color
    new_color = [0,0,0,1]
    for i, c in enumerate(color):
        new_color[i] = c
    return tuple(new_color)

def as255(color):
    """Converts 0 -> 1 color to 0 -> 255 color."""
    if len(color) not in [3, 4]:
        print('Not valid color.')
        return CLEAR
    new_color = []
    for i, c in enumerate(color):
        new_color.append(round(c*255))
    return tuple(new_color)
