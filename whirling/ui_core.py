from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import pygame as pg
import OpenGL.GL as ogl
from enum import Enum
import numpy as np
from whirling import colors


class UIAnchorPositions(Enum):
    BOTTOM_LEFT = 0  # Anchor will be attached at bottom left of text
    TOP_LEFT = 1     # Anchor will be attached at top left of text


class UIElement():
    def __init__(self):
        # declare position
        self.position = (0, 0, 0)
        self.anchor_position = UIAnchorPositions.TOP_LEFT

    def draw(self):
        pass

    def update(self):
        pass

    @property
    def width(self):
        pass

    @property
    def height(self):
        pass

    def translate_position(self, position, anchor_position):
        # This probably only works for text positioning.
        # TODO: figure out how to standardize element positioning so this works
        #       for all UI Elements.
        x = position[0]
        y = position[1]
        z = position[2]
        _window_w, window_h = pg.display.get_surface().get_size()

        # Process anchor.
        if anchor_position == UIAnchorPositions.TOP_LEFT:
            y -= self.height

        # return translated position.
        return (x, y, z)


class UIText(UIElement):
    fonts = {
        'roboto' :'whirling/fonts/Roboto-Black.ttf',
        'mono' :'whirling/fonts/SourceCodePro-Regular.otf'
    }
    def __init__(self, text_string, position, font_size=30, font_key='mono',
                 font_color=colors.WHITE, bg_color=colors.CLEAR,
                 anchor_position=UIAnchorPositions.BOTTOM_LEFT):
        self.original_position = position
        self.font_color = font_color
        self.bg_color = bg_color
        self.anchor_position = anchor_position
        self.font = pg.font.Font(self.fonts[font_key], font_size)
        self.text = text_string

    @property
    def text(self):
        return self.text_string

    @text.setter
    def text(self, text_string):
        self.text_string = text_string
        self.text_surface = self.font.render(
            self.text_string, True, colors.WHITE)

        # Add text color.
        text_color_surf = pg.Surface(self.text_surface.get_rect().size, pg.SRCALPHA)
        text_color_surf.fill(self.font_color)
        self.text_surface.blit(text_color_surf, (0, 0), special_flags=pg.BLEND_RGBA_MULT)

        # Add background color.
        bg_color_surf = pg.Surface(self.text_surface.get_rect().size, pg.SRCALPHA)
        bg_color_surf.fill(self.bg_color)
        bg_color_surf.blit(self.text_surface, (0, 0))
        self.text_surface = bg_color_surf

        # Convert surface to string buffer.
        self.text_data = pg.image.tostring(self.text_surface, "RGBA", 1)
        self.position = self.translate_position(
            self.original_position, self.anchor_position)

    @property
    def width(self):
        return self.text_surface.get_width()

    @property
    def height(self):
        return self.text_surface.get_height()

    def draw(self):
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)
        glRasterPos3d(*self.position)
        glDrawPixels(self.width, self.height,
                     GL_RGBA, GL_UNSIGNED_BYTE, self.text_data)


class UIImage(UIElement):
    def __init__(self, texset, texname):
        self.texture = texset.get(texname)
        self.abspos = None
        self.relpos = None
        self.color = (1,1,1,1)
        self.rotation = 0
        self.rotationCenter = None

    @property
    def width(self):
        return self.texture.width

    @property
    def height(self):
        return self.texture.height

    def draw(self, abspos=None, relpos=None, width=None, height=None,
            color=None, rotation=None, rotationCenter=None):
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        if color==None:
            color = self.color

        glColor4fv(color)

        if abspos:
            glLoadIdentity()
            glTranslate(abspos[0],abspos[1],0)
        elif relpos:
            glTranslate(relpos[0],relpos[1],0)

        if rotation==None:
            rotation=self.rotation

        if rotation != 0:
                if rotationCenter == None:
                    rotationCenter = (self.width / 2, self.height / 2)
                # (w,h) = rotationCenter
                glTranslate(rotationCenter[0],rotationCenter[1],0)
                glRotate(rotation,0,0,-1)
                glTranslate(-rotationCenter[0],-rotationCenter[1],0)

        if width or height:
            if not width:
                width = self.width
            elif not height:
                height = self.height

            glScalef(width/(self.width*1.0), height/(self.height*1.0), 1.0)


        glCallList(self.texture.displaylist)

        if rotation != 0: # reverse
            glTranslate(rotationCenter[0],rotationCenter[1],0)
            glRotate(-1*rotation,0,0,-1)
            glTranslate(-rotationCenter[0],-rotationCenter[1],0)

        glDisable(GL_TEXTURE_2D)
        glDisable(GL_BLEND)


class UIButton(UIText):
    def __init__(self, text_string, position, font_size=30, font_key='mono',
                 font_color=colors.WHITE, bg_color=colors.CLEAR,
                 anchor_position=UIAnchorPositions.TOP_LEFT):

        # Font size is calculated from height of button.
        super().__init__(text_string, position, font_size, font_key,
            font_color, bg_color, anchor_position)

    def draw(self):
        super().draw()


class UIAxis(UIElement):
    def __init__(self, size, offset):
        self.offset = offset
        self.x_color = colors.RED
        self.y_color = colors.GREEN
        self.z_color = colors.BLUE
        self.size = size

    def draw(self):
        glBegin(GL_LINES)

        # Red for x.
        glColor3f(*self.x_color)
        glVertex3fv((0, self.offset, 0))
        glVertex3fv((self.size, self.offset, 0))

        # Green for y.
        glColor3f(*self.y_color)
        glVertex3fv((self.offset, 0, 0))
        glVertex3fv((self.offset, self.size, 0))

        # Blue for z.
        glColor3f(*self.z_color)
        glVertex3fv((0, 0, 0))
        glVertex3fv((0, 0, self.size))

        glEnd()
