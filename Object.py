class Object():
    def __init__(self, fileName):
        self.vertices = []
        self.faces = []

        try:
            f = open(fileName)
            for line in f:
                if line[:2] == "v ":
                    index1 = line.find(" ") + 1
                    index2 = line.find(" ", index1 + 1)
                    index3 = line.find(" ", index2 + 1)

                    vertex = [float(line[index1:index2]), float(line[index2:index3]), float(line[index3:-1])]
                    vertex = [round(vertex[0], 2), round(vertex[1], 2), round(vertex[2], 2)]
                    self.vertices.append(vertex)

                elif line[0] == "f":
                    face = line.replace("f ", "").replace("\n", "").split(" ")
                    triangle = []
                    for str_point in face:
                        triangle.append([(int(v_index)-1) for i, v_index in enumerate(str_point.split("/"))])

                    self.faces.append(triangle)

            f.close()
        except IOError:
            print(".obj file not found.")