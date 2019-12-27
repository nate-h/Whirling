import numpy
from OpenGL import GL
from OpenGL.GL import shaders
import ctypes

def setup_shaders(vpMatrix):
    global shaderProgram, vshader, fshader
    global texCoordAttribute, positionAttribute
    
    vshader = shaders.compileShader('''#version 440
    layout (location = 0) uniform mat4 vpMatrix;
    layout (location = 0) in vec2 vPosition;
    layout (location = 1) in vec2 vTexCoord0;
    //layout (location = 2) in vec4 vVertColor;
    out vec2 texCoord0;
    //out vec4 vertColor;
    void main(void) {
        gl_Position = vpMatrix * vec4(vPosition, 0.0, 1.0);
        texCoord0 = vTexCoord0;
    }''', GL.GL_VERTEX_SHADER)

    fshader = shaders.compileShader('''#version 440
    in vec2 texCoord0;
    //in vec4 vertColor;
    layout (location = 1) uniform sampler2D u_texture0;
    void main(void) {
        gl_FragColor = texture2D(u_texture0, texCoord0);
    }''', GL.GL_FRAGMENT_SHADER)

    shaderProgram = shaders.compileProgram(vshader, fshader)

    texCoordAttribute = GL.glGetAttribLocation(shaderProgram, 'vTexCoord0')
    positionAttribute = GL.glGetAttribLocation(shaderProgram, 'vPosition')
    texUniform = GL.glGetUniformLocation(shaderProgram, 'u_texture0')

    GL.glEnableVertexAttribArray(positionAttribute)
    GL.glEnableVertexAttribArray(texCoordAttribute)
    
    GL.glUseProgram(shaderProgram)
    
    GL.glUniformMatrix4fv(
        GL.glGetUniformLocation(shaderProgram, 'vpMatrix'),
        1,
        False,
        vpMatrix,
    )
    GL.glUniform1i(texUniform, 0)
    
    # TODO: cleanup (delete shaders)

class GLTexture:
    def __init__(self, textureId, width, height):
        self.texture = textureId
        self.width, self.height = width, height

    def delete(self):
        GL.glDeleteTextures([self.texture])

class GLTextureRegion:
    def __init__(self, glTexture, subX, subY, subWidth, subHeight):
        self.texture = glTexture
        #self.tx, self.ty = subX, subY
        self.tw, self.th = subWidth, subHeight

        self.normalizedCoords = (
            subX / glTexture.width, subY / glTexture.height,
            (subX + subWidth) / glTexture.width, subY / glTexture.height,
            subX / glTexture.width, (subY + subHeight) / glTexture.height,
            (subX + subWidth) / glTexture.width, (subY + subHeight) / glTexture.height,
        )

    def write_tex_coords(self, aj):
        nc = self.normalizedCoords
        aj[4 * 0 + 2] = nc[0]
        aj[4 * 0 + 3] = nc[1]
        aj[4 * 1 + 2] = nc[2]
        aj[4 * 1 + 3] = nc[3]
        aj[4 * 2 + 2] = nc[4]
        aj[4 * 2 + 3] = nc[5]
        aj[4 * 3 + 2] = nc[6]
        aj[4 * 3 + 3] = nc[7]

    def write_vertices(self, aj, x, y):
        aj[4 * 0 + 0] = x
        aj[4 * 0 + 1] = y
        aj[4 * 1 + 0] = x + self.tw
        aj[4 * 1 + 1] = y
        aj[4 * 2 + 0] = x
        aj[4 * 2 + 1] = y + self.th
        aj[4 * 3 + 0] = x + self.tw
        aj[4 * 3 + 1] = y + self.th

    def update_array(self, vboData, arrayIndex, x, y):
        aj = vboData[arrayIndex]
        self.write_vertices(aj, x, y)
        self.write_tex_coords(aj)

    def delete(self):
        '''deletes the underlying texture'''
        self.texture.delete()

class Batch:
    def __init__(self, maxQuads = 10000):
        self.maxQuads = maxQuads

        self.vboIndices = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.vboIndices)
        vidA = []
        for i in range(maxQuads):
            vidA.extend([
                4 * i + 0,
                4 * i + 2,
                4 * i + 1,
                4 * i + 2,
                4 * i + 1,
                4 * i + 3
            ])
        self.vboIndexData = numpy.array(vidA, numpy.ushort)
        del vidA
        GL.glBufferData(
            GL.GL_ELEMENT_ARRAY_BUFFER,
            self.vboIndexData,
            GL.GL_STATIC_DRAW,
        )

        self.vbo = GL.glGenBuffers(1)  # texture coords & vertices
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        self.vboData = numpy.zeros((maxQuads, 4 * 4), numpy.float32)
        GL.glBufferData(
            GL.GL_ARRAY_BUFFER,
            self.vboData,
            GL.GL_DYNAMIC_DRAW
        )

        self.currentTexture = None
        self.objectIndex = 0

    def begin(self):
        GL.glBindBuffer(
            GL.GL_ARRAY_BUFFER,
            self.vbo,
        )
        if self.currentTexture:
            GL.glBindTexture(
                GL.GL_TEXTURE_2D,
                self.currentTexture.texture,
            )
        GL.glEnable(GL.GL_TEXTURE_2D)
        GL.glActiveTexture(GL.GL_TEXTURE0)

    def draw(self, textureRegion, x, y):
        if self.currentTexture != textureRegion.texture:
            self.flush()
            self.currentTexture = textureRegion.texture
            GL.glBindTexture(
                GL.GL_TEXTURE_2D,
                textureRegion.texture.texture,
            )
        elif self.objectIndex >= self.maxQuads:
            self.flush()
        textureRegion.update_array(
            self.vboData,
            self.objectIndex,
            x, y
        )
        self.objectIndex += 1

    def end(self):
        self.flush()

    def flush(self):
        if not self.objectIndex:
            return
        GL.glVertexAttribPointer(
            texCoordAttribute,
            2,
            GL.GL_FLOAT,
            GL.GL_TRUE,
            4 * self.vboData.itemsize,
            ctypes.c_void_p(2 * self.vboData.itemsize)
        )
        GL.glVertexAttribPointer(
            positionAttribute,
            2,
            GL.GL_FLOAT,
            GL.GL_FALSE,
            4 * self.vboData.itemsize,
            ctypes.c_void_p(0)
        )
        GL.glBufferSubData(
            GL.GL_ARRAY_BUFFER,
            0,
            16 * self.objectIndex * self.vboData.itemsize,
            self.vboData,
        )
        GL.glDrawElements(
            GL.GL_TRIANGLES,
            6 * self.objectIndex,
            GL.GL_UNSIGNED_SHORT,
            ctypes.c_void_p(0),
        )
        self.objectIndex = 0

    def delete(self):
        GL.glDeleteBuffers(1, [self.vbo])
        GL.glDeleteBuffers(1, [self.vboIndices])