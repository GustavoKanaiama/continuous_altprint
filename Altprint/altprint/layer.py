from shapely.geometry import Polygon, MultiPolygon, LineString, MultiLineString
import numpy as np
from altprint.flow import calculate

# Define como será feito o percurso do raster (trajetória extrudindo) e como será lógica da construção de camadas que é dividida em perimetro e prenchimento


class Raster:  # Esta classe representa um caminho raster na impressão

    # método que inicializa o raster com os seguintes parâmetros: path: Um LineString representando o caminho do bico da impressora, flow: O fator multiplicador de fluxo (calculado usando a função de cálculo), speed: A velocidade de impressão (valor escalar)
    def __init__(self, path: LineString, flow, speed):

        self.path = path  # "path" é armazenado como uma variável de instância

        # "speed" é usada para criar uma matriz de velocidades (uma para cada ponto coordenado no caminho)
        self.speed = np.ones(len(path.coords)) * speed
        # A matriz de extrusão é inicializada com zeros (para acumular valores de extrusão)
        self.extrusion = np.zeros(len(path.coords))
        x, y = path.xy  # Extrai as coordenadas X e Y de "path"
        # itera o laço a quantidade de vezes equivalente a quantiade de coordenadas armazenadas na array "path"
        for i in range(1, len(path.coords)):
            # distância entre a coordenada x atual e a anterior
            dx = abs(x[i] - x[i - 1])
            # distância entre a coordenada y atual e a anterior
            dy = abs(y[i] - y[i - 1])
            # array que armazena o valor da quantidade de filamento utilizada para cada "conjunto" de coordenadas XY que compõe a traetória do raster até o ponto atual
            self.extrusion[i] = np.sqrt(
                (dx**2) + (dy**2)) * flow * calculate() + self.extrusion[i-1]


class Layer:  # class represents a layer in a 3D printing process
    """Layer Object that stores layer internal and external shapes, also perimeters and infill path"""  # noqa: E501

    def __init__(self, shape: MultiPolygon, perimeter_num, perimeter_gap, external_adjust, overlap):  # method that initializes the layer # noqa: E501
        # A MultiPolygon representing the layer’s shape (both internal and external)
        self.shape = shape
        self.perimeter_num = perimeter_num  # The number of perimeters for this layer
        # A parameter related to the spacing between perimeters
        self.perimeter_gap = perimeter_gap
        # An adjustment factor specific to external shapes
        self.external_adjust = external_adjust
        # A value indicating how much overlap there is between adjacent perimeters
        self.overlap = overlap
        self.perimeter_paths: List = []  # noqa: F821 #A list (initialized as empty) to store the paths of individual perimeters
        self.perimeter: List = []  # noqa: F821 #list (initialized as empty) for additional perimeter-related information
        self.infill: List = []  # noqa: F821 #list to store information related to infill paths
        # A MultiPolygon (initialized as an empty MultiPolygon) representing the border of the infill area
        self.infill_border: MultiPolygon = MultiPolygon()

    def make_perimeter(self):  # Este método constrói os caminhos de perímetro para uma camada erodindo a forma da camada e extraindo os segmentos de limite (externo) e furo (interno). Esses segmentos são armazenados no atributo perimeter_paths
        """Generates the perimeter based on the layer process"""

        # empty list "perimeter_paths" to store the individual segments of the perimeter
        perimeter_paths = []
        # the loop iterates through each section (geometry) within the layer’s shape (which is a MultiPolygon)
        for section in self.shape.geoms:
            for i in range(self.perimeter_num):  # the loop iterates number of perimeters
                eroded_shape = section.buffer(- self.perimeter_gap*(i)
                                              - self.external_adjust/2, join_style=2)  # Calculates an “eroded shape” by buffering the section with a negative distance
                # The negative distance is determined by subtracting the product of self.perimeter_gap * i and self.external_adjust / 2. The join_style=2 argument specifies how the buffer should handle intersections

                # If the eroded shape is empty (has no geometry), the loop breaks
                if eroded_shape.is_empty:
                    break
                # If the eroded shape is a single Polygon, it creates a list containing that polygon
                if type(eroded_shape) == Polygon:
                    polygons = [eroded_shape]
                # If the eroded shape is a MultiPolygon, it extracts the individual polygons from it
                elif type(eroded_shape) == MultiPolygon:
                    polygons = list(eroded_shape.geoms)

                # For each polygon (both exterior and interior)
                for poly in polygons:
                    for hole in poly.interiors:
                        # Adds the interior rings (holes) as individual LineString segments to perimeter_paths
                        perimeter_paths.append(LineString(hole))
                for poly in polygons:
                    # Adds the exterior ring (boundary) as a LineString segment to perimeter_paths
                    perimeter_paths.append(LineString(poly.exterior))
        # assigns the entire perimeter_paths list (composed of all the segments) to the self.perimeter_paths attribute (which is a MultiLineString)
        self.perimeter_paths = MultiLineString(perimeter_paths)

    def make_infill_border(self):  # method constructs the infill border for a layer by eroding the layer’s shape and extracting the individual polygons that form the border. These polygons are stored in the infill_border attribute
        """Generates the infill border based on the layer process"""

        # empty list called infill_border_geoms to store the individual geometries (polygons) of the infill border
        infill_border_geoms = []
        # the loop iterates through each section (geometry) within the layer’s shape (which is a MultiPolygon)
        for section in self.shape.geoms:
            eroded_shape = section.buffer(- self.perimeter_gap
                                          * self.perimeter_num
                                          - self.external_adjust/2
                                          + self.overlap, join_style=2)  # Calculates an “eroded shape” by buffering the section with a negative distance
            if not eroded_shape.is_empty:  # If the eroded shape is not empty
                # If the eroded shape is a single Polygon, it appends it to the infill_border_geoms list
                if type(eroded_shape) == Polygon:
                    infill_border_geoms.append(eroded_shape)
                else:
                    # If the eroded shape is a MultiPolygon, it extends the list with the individual polygons extracted from it
                    infill_border_geoms.extend(eroded_shape.geoms)

        # the entire infill_border_geoms list (composed of all the individual geometries) to the self.infill_border attribute (which is a MultiPolygon)
        self.infill_border = MultiPolygon(infill_border_geoms)
