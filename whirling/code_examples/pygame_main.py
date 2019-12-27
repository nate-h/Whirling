import pygame as pg
import batch
from OpenGL import GL
import numpy

def loadTexture(file):
    '''returns a GLTexture for a given file name'''
    surface = pg.image.load(file)
    texture = GL.glGenTextures(1)

    GL.glBindTexture(GL.GL_TEXTURE_2D, texture)

    w = surface.get_width()
    h = surface.get_height()

    GL.glTexImage2D(
        GL.GL_TEXTURE_2D,
        0,
        GL.GL_RGBA,
        w, h,
        0,
        GL.GL_RGBA,
        GL.GL_UNSIGNED_BYTE,
        pg.image.tostring(
            surface,
            'RGBA'
        ),
    )

    GL.glTexParameter(
        GL.GL_TEXTURE_2D,
        GL.GL_TEXTURE_MIN_FILTER,
        GL.GL_NEAREST,
    )
    GL.glTexParameter(
        GL.GL_TEXTURE_2D,
        GL.GL_TEXTURE_MAG_FILTER,
        GL.GL_NEAREST,
    )

    return batch.GLTexture(texture, w, h)

def loadSheet(fileOrGLTexture, subWidth, subHeight=0, numFrames=0, x=0, y=0):
    '''
    returns an array of GLTextureRegions containing a animation/sheet
    numframes: if set to 0, the remaining width will be divided into equally wide frames based on subWidth.
    subHeight: if set to 0, the entire height will be used.
    '''
    if isinstance(fileOrGLTexture, batch.GLTexture):
        texture = fileOrGLTexture
    else:
        texture = loadTexture(fileOrGLTexture)
    if not subHeight:
        subHeight = texture.height
    if not numFrames:
        numFrames = int((texture.width - x) / subWidth)
        numFrames *= int((texture.height - y) / subHeight)
    subsurfaces = [batch.GLTextureRegion(
        texture,
        (x + i * subWidth) % texture.width,
        y + subHeight * int(int(i * subWidth) / texture.width),
        subWidth,
        subHeight,
    ) for i in range(numFrames)]
    return subsurfaces

def deleteSheet(sheet):
    sheet[0].delete()

if __name__ == '__main__':
    pg.init()
    displaySurface = pg.display.set_mode((640,480), pg.OPENGL | pg.DOUBLEBUF)
    GL.glViewport(0, 0, 640, 480)
    
    animation = loadSheet(
        'animation.png',
        20,
    )

    projectionMatrix = numpy.array((
        (2/320, 0, 0, 0),
        (0, -2/240, 0, 0),
        (0, 0, 1, 0),
        (0, 0, 0, 1)
    ), numpy.float32)
    viewMatrix = numpy.array((
        (1, 0, 0, 0),
        (0, 1, 0, 0),
        (0, 0, 1, 0),
        (-160, -120, 0, 1)
    ), numpy.float32)
    
    batch.setup_shaders(vpMatrix = numpy.dot(viewMatrix, projectionMatrix))
    renderer = batch.Batch()
    
    running = True
    imageIndex = 0
    clock = pg.time.Clock()
    
    while running:
        imageIndex = (imageIndex + 0.1) % len(animation)
        
        GL.glClearColor(0, 0, 0, 1)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)
        
        renderer.begin()
        for i in range(710):
            renderer.draw(
                animation[int(imageIndex)],
                10 + (20 * i) % 300,
                10 + 20 * int(20 * i / 300)
            )
        renderer.end()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                running = False

        pg.display.flip()

        clock.tick(0)
        pg.display.set_caption('FPS: ' + str(clock.get_fps()))

    renderer.delete()
    deleteSheet(animation)