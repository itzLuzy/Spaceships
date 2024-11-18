from OpenGL.GL import *
import trimesh
from libs.gpu_tools import trimesh_to_gpu
from libs.shape import Shape
from libs.transformations import identity
from shapes import Moveable


vertex_shader = """
#version 330

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
uniform mat4 transform;

in vec3 position;
in vec2 texCoords;

out vec2 outTexCoords;
            

void main()
{
    vec4 vertexPos = model * vec4(position, 1.0);
    gl_Position = projection * view * transform * vertexPos;
    outTexCoords = texCoords;
}
"""

fragment_shader = """
#version 330

in vec2 outTexCoords;

out vec4 outColor;

uniform sampler2D samplerTex;

void main()
{
    vec4 texel = texture(samplerTex, outTexCoords);
    outColor = texel;
}
"""

class Ship(Shape,Moveable):
    def __init__(self, model_path):
        Shape.__init__(self, vertex_shader, fragment_shader)
        Moveable.__init__(self, 0.0, 0.0, 0.0)

        self.ship = trimesh.load(model_path)
        self.gpu_ship = trimesh_to_gpu(self.ship, self.shader_program)

    def setup_program(self, view_matrix, projection_matrix):
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glEnable(GL_DEPTH_TEST)

        glUseProgram(self.shader_program)

        glUniformMatrix4fv(
            glGetUniformLocation(self.shader_program, "view"), 
            1, 
            GL_TRUE, 
            view_matrix
        )

        glUniformMatrix4fv(
            glGetUniformLocation(self.shader_program, "projection"),
            1,
            GL_TRUE,
            projection_matrix,
        )

        glUniformMatrix4fv(
            glGetUniformLocation(self.shader_program, "model"),
            1,
            GL_TRUE,
            identity(),
        )
    
    def draw(self, *params, **kwargs):
        for shape in self.gpu_ship.values():
            glBindVertexArray(shape["vao"])
            if 'texture' in shape:
                glBindTexture(GL_TEXTURE_2D, shape["texture"])
            glDrawElements(GL_TRIANGLES, shape["size"], GL_UNSIGNED_INT, None)
            glBindVertexArray(0)
        glBindTexture(GL_TEXTURE_2D, 0)