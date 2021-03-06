from os.path import splitext
from OpenGL.GL import *  # pylint: disable=unused-wildcard-import,redefined-builtin,wildcard-import
from OpenGL.GLU import *  # pylint: disable=unused-wildcard-import,redefined-builtin,wildcard-import
from OpenGL.GLUT import *  # pylint: disable=unused-wildcard-import,redefined-builtin,wildcard-import
import pygame as pg

# Code adapated from here:
# https://www.pygame.org/wiki/SimpleOpenGL2dClasses


# All textures in whirling are defined here.
# Using a texture set ensures no wasted compute.
IMAGES = {
    'ffw.png',
    'next.png',
    'pause.png',
    'play.png',
    'prev.png',
    'rw.png',
    'stop.png',
    'next_arrow.png',
    'previous_arrow.png',
    'up_arrow.png',
    'down_arrow.png',
}


def loadImage(image):
    texture_surface = pg.image.load(image)

    texture_data = pg.image.tostring(texture_surface, "RGBA", 1)

    width = texture_surface.get_width()
    height = texture_surface.get_height()

    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA,
                 GL_UNSIGNED_BYTE, texture_data)

    return texture, width, height


def delTexture(texture):
    # glDeleteTextures(texture)
    # TODO figure out why this doesn't work.
    # The error I get is:
    # TypeError: No array-type handler for type numpy.uint32 (value: 1) registered
    pass


def createTexDL(texture, width, height):
    new_list = glGenLists(1)
    glNewList(new_list,GL_COMPILE)
    glBindTexture(GL_TEXTURE_2D, texture)
    glBegin(GL_QUADS)

    # Bottom Left Of The Texture and Quad
    glTexCoord2f(0, 0); glVertex2f(0, 0)

    # Top Left Of The Texture and Quad
    glTexCoord2f(0, 1); glVertex2f(0, height)

    # Top Right Of The Texture and Quad
    glTexCoord2f(1, 1); glVertex2f( width,  height)

    # Bottom Right Of The Texture and Quad
    glTexCoord2f(1, 0); glVertex2f(width, 0)
    glEnd()
    glEndList()

    return new_list


def delDL(some_list):
    glDeleteLists(some_list, 1)

def render(layers):
    for l in layers:
        l.render()

class GL_Texture:
    def __init__(self, texname=None, texappend=".png"):
        filename = os.path.join('whirling/assets', texname)
        filename += texappend
        self.texture, self.width, self.height = loadImage(filename)
        self.displaylist = createTexDL(self.texture, self.width, self.height)

    def __del__(self):
        if self.texture != None:
            delTexture(self.texture)
            self.texture = None
        if self.displaylist != None:
            delDL(self.displaylist)
            self.displaylist = None

    def __repr__(self):
        return self.texture.__repr__()

class Textureset:
    """Texturesets contain and name textures."""

    def __init__(self, textures=[]):
        self.textures = {}
        for texture in textures:
            texname, texappend = splitext(texture)
            self.load(texname=texname, texappend=texappend)
    def load(self, texname=None, texappend=".png"):
        self.textures[texname] = GL_Texture(texname, texappend)
    def set(self, texname, data):
        self.textures[texname] = data
    def delete(self, texname):
        del self.textures[texname]
    def __del__(self):
        self.textures.clear()
        del self.textures
    def get(self, name):
        return self.textures[name]

class WhirlingTextures:
    class __OnlyOne(Textureset):
        def __init__(self):
            super().__init__(IMAGES)
    instance = None
    def __init__(self):
        if not WhirlingTextures.instance:
            WhirlingTextures.instance = WhirlingTextures.__OnlyOne()
    def __getattr__(self, name):
        return getattr(self.instance, name)
