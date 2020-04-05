from abc import ABC, abstractmethod
from OpenGL.GL import *  # pylint: disable=unused-wildcard-import
from OpenGL.GLU import *  # pylint: disable=unused-wildcard-import
from OpenGL.GLUT import *  # pylint: disable=unused-wildcard-import
import pygame as pg
from whirling.ui_core import colors
from whirling.ui_core.primitives import Rect


class UIElement(ABC):
    def __init__(
        self, rect=Rect(), position=(0,0),
        bg_color=colors.CLEAR, border_color=colors.CLEAR,
        border_thickness=1
    ):
        # declare position and translate it.
        self.rect = rect.translate(*position)
        self.bg_color = bg_color
        self.border_color = border_color
        self.border_thickness = border_thickness

    def draw(self):
        self.draw_background()
        self.draw_border()

    def update(self):
        pass

    def draw_border(self, left=True, top=True, right=True, bottom=True):
        # Don't proceed if clear border color.
        if self.border_color is colors.CLEAR:
            return
        glColor4f(*colors.color4f(self.border_color))
        glLoadIdentity()
        glTranslate(*self.rect.position)
        glTranslatef(.5,.5,0)  # Get lines to fall on pixels.
        glLineWidth(self.border_thickness)
        glBegin(GL_LINES)

        if left:
            glVertex2f(0, 0)
            glVertex2f(0, self.height)

        if top:
            glVertex2f(0, self.height)
            glVertex2f(self.width, self.height)

        if right:
            glVertex2f(self.width, self.height)
            glVertex2f(self.width, 0)

        if bottom:
            glVertex2f(self.width, 0)
            glVertex2f(0, 0)

        glEnd()
        glLoadIdentity()

    def draw_background(self):
        # Don't proceed if clear border color.
        if self.bg_color is colors.CLEAR:
            return
        glColor4f(*colors.color4f(self.bg_color))
        glLoadIdentity()
        glTranslate(*self.rect.position)
        glBegin(GL_QUADS)
        glVertex2f(0, 0)
        glVertex2f(0, self.height)
        glVertex2f(self.width, self.height)
        glVertex2f(self.width, 0)
        glEnd()

    @property
    @abstractmethod
    def width(self):
        pass

    @property
    @abstractmethod
    def height(self):
        pass


class UIText(UIElement):
    fonts = {
        'roboto' :'whirling/assets/fonts/Roboto-Black.ttf',
        'mono' :'whirling/assets/fonts/SourceCodePro-Regular.otf'
    }
    def __init__(self, text_string, position, font_size=30, font_key='mono',
            font_color=colors.WHITE, bg_color=colors.CLEAR,
            border_color=colors.CLEAR
        ):

        super().__init__(
            position=position, bg_color=bg_color, border_color=border_color
        )

        self.font_color = font_color
        self.font = pg.font.Font(self.fonts[font_key], font_size)
        self.text = text_string


    @property
    def text(self):
        return self.text_string

    @text.setter
    def text(self, text_string):
        self.text_string = text_string
        self.text_surface = self.font.render(
            self.text_string, True, colors.as255(colors.WHITE))

        # Update rect.
        self.rect.width = self.text_surface.get_width()
        self.rect.height = self.text_surface.get_height()

        # Add text color.
        text_color_surf = pg.Surface(self.text_surface.get_rect().size, pg.SRCALPHA)
        text_color_surf.fill(colors.as255(self.font_color))
        self.text_surface.blit(text_color_surf, (0, 0), special_flags=pg.BLEND_RGBA_MULT)

        # Add background color.
        bg_color_surf = pg.Surface((self.width, self.height), pg.SRCALPHA)
        bg_color_surf.fill(colors.as255(self.bg_color))

        # Add border color to background.
        b_color = colors.as255(self.border_color)
        if self.border_color is not colors.CLEAR:
            pg.draw.line(bg_color_surf, b_color,
                (0, 0), (self.width, 0), 1)
            pg.draw.line(bg_color_surf, b_color,
                (self.width-1, 0), (self.width-1, self.height-1), 1)
            pg.draw.line(bg_color_surf, b_color,
                (self.width -1, self.height-1), (0, self.height-1), 1)
            pg.draw.line(bg_color_surf, b_color,
                (0, self.height-1), (0, 0), 1)

        # Blend background into text.
        bg_color_surf.blit(self.text_surface, (0, 0))
        self.text_surface = bg_color_surf

        # Convert surface to string buffer.
        self.text_data = pg.image.tostring(self.text_surface, "RGBA", 1)

    @property
    def width(self):
        return self.text_surface.get_width()

    @property
    def height(self):
        return self.text_surface.get_height()

    def draw(self):
        glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)
        glLoadIdentity()
        glRasterPos3d(*self.rect.position)
        glDrawPixels(self.width, self.height,
                     GL_RGBA, GL_UNSIGNED_BYTE, self.text_data)


class UIImage(UIElement):
    def __init__(self, rect, texset, texname, **kwargs):

        super().__init__(rect=rect, **kwargs)

        self.texset = texset
        self.texture = self.texset.get(texname)
        self.color = (1,1,1,1)
        self.rotation = 0
        self.rotationCenter = None

    @property
    def width(self):
        return self.rect.width

    @property
    def height(self):
        return self.rect.height

    def draw(self, color=None, rotation=None, rotationCenter=None):
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        if color==None:
            color = self.color

        glColor4fv(color)

        glLoadIdentity()
        glTranslate(*self.rect.position)

        if rotation==None:
            rotation=self.rotation

        if rotation != 0:
            if rotationCenter == None:
                rotationCenter = (self.width / 2, self.height / 2)
            # (w,h) = rotationCenter
            glTranslate(rotationCenter[0],rotationCenter[1],0)
            glRotate(rotation,0,0,-1)
            glTranslate(-rotationCenter[0],-rotationCenter[1],0)

        glScalef(self.width/(self.texture.width*1.0),
            self.height/(self.texture.height*1.0), 1.0)


        glCallList(self.texture.displaylist)

        if rotation != 0: # reverse
            glTranslate(rotationCenter[0],rotationCenter[1],0)
            glRotate(-1*rotation,0,0,-1)
            glTranslate(-rotationCenter[0],-rotationCenter[1],0)

        glDisable(GL_TEXTURE_2D)


class UIButton(UIImage):
    def __init__(self, rect, action, texset, texname, **kwargs):

        super().__init__(rect=rect, texset=texset, texname=texname, **kwargs)

        self.action = action

    @property
    def width(self):
        return self.rect.width

    @property
    def height(self):
        return self.rect.height

    def perform_action(self):
        self.action()

    def handle_event(self, event):
        _w, h = pg.display.get_surface().get_size()
        if event.type == pg.MOUSEBUTTONDOWN:
            pass
            # if self.rect.contains_point(event.pos):
            #     self.image = self.image_hover
            # else:
            #     self.image = self.image_normal

        # Clicking.
        if event.type == pg.MOUSEBUTTONDOWN:
            x, y = event.pos
            if self.rect.contains_point((x, -y+h)):
                self.perform_action()

class UIToggleButton(UIButton):
    def __init__(self, rect, states, texset, **kwargs):
        self.states = states
        self.state = self.get_next_state()
        super().__init__(
            rect=rect, action=self.state[1]['action'], texset=texset, texname=self.state[0], **kwargs)

    def perform_action(self):
        self.action()
        self.toggle_state()

    def get_next_state(self):
        if not hasattr(self, 'state') or self.state is None:
            return list(self.states.items())[0]
        raw_index = list(self.states.keys()).index(self.state[0])
        index = (raw_index + 1) % len(self.states)
        return list(self.states.items())[index]

    def toggle_state(self):
        self.state = self.get_next_state()
        texname = self.state[0]
        self.action = self.state[1]['action']
        self.texture = self.texset.get(texname)

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


class UIDock(UIElement):
    def __init__(self, rect, bg_color=colors.CLEAR, border_color=colors.BLACK):

        # Initialize base class.
        super().__init__(rect, bg_color=bg_color, border_color=border_color)

    @property
    def width(self):
        return self.rect.width

    @property
    def height(self):
        return self.rect.height

    def draw(self):
        super().draw()
