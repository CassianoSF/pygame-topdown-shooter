import pygame, numpy, pyrr, math, os, string
from OpenGL.GL import *
from Shader import Shader
from VertexBuffer import VertexBuffer
from VertexArray import VertexArray
from IndexBuffer import IndexBuffer
from Texture import Texture

class Object():
    def __init__(self, objFileName, textureFileName):
        vertices = []
        indices = []
        tex_map = []
        normals = []

        try:
            file = open(objFileName)
            temp_vertices = []
            temp_tex_map = []
            temp_normals = []

            for line in file:
                if line[:2] == "v ":
                    temp_vertices.append(
                        list(map(float, line.replace("v ", "").replace("\n", "").split(" ")))
                    )
                if line[:3] == "vt ":
                    temp_tex_map.append(
                        list(map(float, line.replace("vt ", "").replace("\n", "").split(" ")))
                    )
                if line[:3] == "vn ":
                    temp_normals.append(
                        list(map(float, line.replace("vn ", "").replace("\n", "").split(" ")))
                    )
                elif line[:2] == "f ":
                    if("/" in line):
                        face = line.replace("f ", "").replace("\n", "").split(" ")
                        for triangle in face:
                            v_index, t_index, n_index = triangle.split("/")

                            v_index = int(v_index or 1) -1
                            t_index = int(t_index or 1) -1
                            n_index = int(n_index or 1) -1

                            if len(temp_vertices) > v_index:
                                vertices.append(temp_vertices[v_index])

                            if len(temp_tex_map) > t_index:
                                tex_map.append(temp_tex_map[t_index])

                            if len(temp_normals) > n_index:
                                normals.append(temp_normals[n_index])

                            indices.append(len(indices))
                    else:
                        v_indices = line.replace("f ", "").replace("\n", "").split(" ")
                        for v_index in v_indices:
                            v_index = int(v_index or 1) -1
                            if len(temp_vertices) > v_index:
                                vertices.append(temp_vertices[v_index])
                            
                            indices.append(len(indices))


            if not len(tex_map):
                for i, el in enumerate(vertices):
                    if i % 4 == 0:
                        tex_map.append(1)
                        tex_map.append(1)
                    if i % 4 == 1:
                        tex_map.append(0)
                        tex_map.append(1)
                    if i % 4 == 2:
                        tex_map.append(1)
                        tex_map.append(0)
                    if i % 4 == 3:
                        tex_map.append(0)
                        tex_map.append(0)

            file.close()
            vertices = numpy.array(vertices, dtype="float32").flatten()
            tex_map = numpy.array(tex_map, dtype="float32").flatten()
            normals = numpy.array(normals, dtype="float32").flatten()
            indices = numpy.array(indices, dtype="int32")


            self.texture = Texture(textureFileName)
            self.shader = Shader("VertexShader.shader", "FragmentShader.shader")
            self.va = VertexArray()
            self.vb_positions = VertexBuffer(vertices)
            self.va.add_buffer(0, 3, self.vb_positions)
            self.vb_texture = VertexBuffer(tex_map)
            self.va.add_buffer(1, 2, self.vb_texture)
            self.ib = IndexBuffer(indices)

            print(temp_vertices)
            print(temp_tex_map)

            self.model = {
                'translation': [0.0, 0.0, 0.0],
                'rotation':    [0.0, 0.0, 0.0],
                'scale':       [1.0, 1.0, 1.0]
            }

        except IOError:
            print(".obj file not found.")

    def translate(self, x, y, z):
        self.model['translation'] = [
            self.model['translation'][0] + x,
            self.model['translation'][1] + y,
            self.model['translation'][2] + z
        ]

    def scale(self, x, y, z):
        self.model['scale'] = [x,y,z]

    def render(self, mvp):
        self.texture.bind()
        self.shader.add_uniform_1i("the_texture", 0)
        self.shader.add_uniform_matrix_4f("mvp", mvp)
        self.shader.bind()
        self.va.bind()
        self.ib.bind()
        glDrawElements(GL_TRIANGLES, self.va.size, GL_UNSIGNED_INT, None)