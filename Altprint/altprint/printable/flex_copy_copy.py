from altprint.printable.base import BasePrint
from altprint.slicer import STLSlicer
from altprint.layer import Layer, Raster
from altprint.height_method import StandartHeightMethod
from altprint.infill.rectilinear_infill import RectilinearInfill
from altprint.gcode import GcodeExporter
from altprint.lineutil import split_by_regions, retract
from altprint.settingsparser import SettingsParser

# -- teste
import shapely as sp

from altprint.printable.best_path import *


class FlexProcess():  # definição da classe responsável por controlar os parâmetros de impressão
    # método construtor da classe, aceita um número arbitrário de argumentos de palavra-chave
    def __init__(self, **kwargs):
        # dicionário criado que contém os valores padrão para vários parâmetros que serão usadas no processo de impressão
        prop_defaults = {
            "model_file": "",
            "flex_model_file": "",
            "slicer": STLSlicer(StandartHeightMethod()),
            "infill_method": RectilinearInfill,
            "infill_angle": 0,
            "offset": (0, 0, 0),
            "external_adjust": 0.5,
            "perimeter_num": 1,
            "perimeter_gap": 0.5,
            "raster_gap": 0.5,
            "overlap": 0.0,
            "skirt_distance": 10,
            "skirt_num": 3,
            "skirt_gap": 0.5,
            "first_layer_flow": 2,
            "flow": 1.2,
            "speed": 2400,
            "flex_flow": 0,
            "flex_speed": 2000,
            "retract_flow": 2,
            "retract_speed": 1200,
            "retract_ratio": 0.9,
            "gcode_exporter": GcodeExporter,
            "start_script": "",
            "end_script": "",
            "verbose": True,
        }
        # loop que percorre todos os itens do dicionário "prop_defaults". Para cada item, ele usa a função "setattr" para definir um atributo na instância atual com o nome "prop" e o valor correspondente de kwargs se ele existir, caso contrário, ele usa o valor padrão default.
        for (prop, default) in prop_defaults.items():
            setattr(self, prop, kwargs.get(prop, default))
        # Se "kwargs" contém uma chave "settings_file", um objeto "SettingsParser" é criado e usado para carregar as configurações de um arquivo yml, esse objeto tem a função de transformar as configurações de um arquivo yml em um dicionário em python. Em seguida, essas configurações são usadas para definir atributos adicionais na instância atual.
        if 'settings_file' in kwargs.keys():
            settings = SettingsParser().load_from_file(kwargs['settings_file'])
            for (setting, value) in settings.items():
                setattr(self, setting, value)


class FlexPrint(BasePrint):  # definição da classe responsável por implementar o fatiamento, geração de camadas e exportação do gcode de um arquivo de uma peça CAD em stl para ser enviado a impreesora 3D
    """The common print. Nothing special"""

    _height = float  # variável float que armazena altura da camada
    # dicionário que contém a altura de cada camada
    _layers_dict = dict[_height, Layer]

    # método construtor da classe, recebe um parâmetro "process" que é uma instância da classe "FlexProcess". O construtor inicializa três atributos de instância
    def __init__(self, process: FlexProcess):
        # atributo que recebe as configurações dos parâmetros de impressão fornecidado pela classe "FlexProcess"
        self.process = process
        # dicionário vazio que armazena as alturas referente a cada camada
        self.layers: _layers_dict = {}
        # lista vazia que armazena os valores das alturas como float
        self.heights: list[float] = []

    def slice(self):  # método que fatia modelo 3D e calcula as alturas das camadas
        if self.process.verbose is True:
            print("slicing {} ...".format(self.process.model_file))
        # atribui as configurações dos parâmetros de impressão como um objeto da classe STLSlicer
        slicer = self.process.slicer
        # método dentro da Classe STLSlicer que lê o arquivo do objeto 3D referente a região normal (em stl) determinado no arquivo yml
        slicer.load_model(self.process.model_file)
        # método dentro da Classe STLSlicer que translada o objeto no plano 3D para um offset determinado no arquivo yml
        slicer.translate_model(self.process.offset)
        # método dentro da Classe STLSlicer que fatia o objeto 3D em uma quantidade de planos igual ao numero de camadas
        self.sliced_planes = slicer.slice_model()
        # método da classe StandartHeightMethod, calcula e retorna uma lista com as alturas de cada camada
        self.heights = self.sliced_planes.get_heights()

        # método dentro da Classe STLSlicer que lê o arquivo do objeto 3D referente a região flexível (em stl) determinado no arquivo yml
        slicer.load_model(self.process.flex_model_file)
        # método dentro da Classe STLSlicer que translada o objeto no plano 3D para um offset determinado no arquivo yml
        slicer.translate_model(self.process.offset)
        # método dentro da Classe STLSlicer que fatia o objeto 3D em uma quantidade de planos igual ao numero de camadas (que é obtido através do tamanho do vetor que armazena as alturas de cada camada)
        self.flex_planes = slicer.slice_model(self.heights)

    def make_layers(self):  # método que gera as trajetórias das camadas, desde a saia inicial, e o perímetro/contorno e o preenchimento de cada camada

        if self.process.verbose is True:  # linha de verificação fornecida dentro das configurações do próprio arquivo yml

            # mensagem quando executa essa função do programa
            print("generating layers ...")

        # atribui as configurações dos parâmetros de impressão como um objeto da classe RectilinearInfill
        infill_method = self.process.infill_method()

        # lógica de construção da saia em volta da primeira camada da peça
        # cria uma instância "skirt" da classe "Layer" que recebe os parâmetros da saia fornecidos pelo arquivo yml
        skirt = Layer(self.sliced_planes.planes[self.heights[0]],
                      self.process.skirt_num,
                      self.process.skirt_gap,
                      - self.process.skirt_distance - self.process.skirt_gap * self.process.skirt_num,  # noqa: E501
                      self.process.overlap)

        # utiliza o método da classe "Layer" para criação do perímetro formado pela saia
        skirt.make_perimeter()

        print(len(self.heights))

        NextPerimeter_calculated = False
        optmizedPerimeterPath_perLayer = []

        # loop que percorre todas as alturas na lista "heights". A função enumerate é usada para obter tanto o índice (i) quanto o valor (height) de cada altura.
        for i, height in enumerate(self.heights):


            # para cada altura, é criado um novo objeto "Layer", que recebe os parãmetros referentes ao perímetro fornecidos pelo arquivo yml, e atribuído a "layer" que é referente a cada camada
            layer = Layer(self.sliced_planes.planes[height],
                          self.process.perimeter_num,
                          self.process.perimeter_gap,
                          self.process.external_adjust,
                          self.process.overlap)
            
            """
            # ------- BEGIN OF NEXT LAYER -------
            if (i+1) <= (len(self.heights)-1):
                nextLayer = Layer(self.sliced_planes.planes[self.heights[i+1]],
                            self.process.perimeter_num,
                            self.process.perimeter_gap,
                            self.process.external_adjust,
                            self.process.overlap)
                
                if nextLayer.shape == []:
                    self.layers[height] = nextLayer
                    continue

                nextLayer.make_perimeter()
                nextLayer.make_infill_border()

                nextFlex_regions = self.flex_planes.planes[self.heights[i+1]]

                # Se "flex_regions" não for uma lista, ele é convertido em uma lista
                if not type(nextFlex_regions) == list:  # noqa: E721
                    nextFlex_regions = list(nextFlex_regions.geoms)

                # Os caminhos do perímetro da camada são divididos pelas regiões flexíveis
                nextLayer.perimeter_paths = split_by_regions(nextLayer.perimeter_paths, nextFlex_regions)


                # percorre cada caminho no perímetro da camada. Se o caminho estiver dentro de uma região flexível, ele é dividido em um caminho flexível e um caminho de retração, que são adicionados ao perímetro da camada. Se o caminho não estiver dentro de uma região flexível, ele é adicionado ao perímetro da camada como está
                for j, path in enumerate(nextLayer.perimeter_paths.geoms):

                    # Merge the same layers LINESTRINGS
                    if j == 0:
                        nextRawList = RawList_Points(path, makeTuple=True)

                    else:
                        # Delete all redundancy from regions (repeated coords.)
                        nextRawList = RawList_Points(path, makeTuple=True)

                        if i == 1:
                            print("rawList antes:", nextRawList)

                        if nextRawList[0] == last_rawList[-1]:
                            nextRawList.pop(0)

                        if i == 1:
                            print("rawList depois:", nextRawList)
                            print()

                    perimeterPath_perLayer.append(nextRawList.copy())
                
                # Concatenates lists of tuples
                finalPerimeterPath_perLayer = [coord for sublist in perimeterPath_perLayer for coord in sublist]
                
                #Split perimeter
                List_perimeters = split_PerimeterPath(finalPerimeterPath_perLayer, nextLayer.perimeter_num)

                for n in range(len(List_perimeters)):
                    Linestring_perLayer = sp.LineString(List_perimeters[n])

                    nextLayer.perimeter.append(
                                Raster(Linestring_perLayer, self.process.first_layer_flow, self.process.speed))
                    
                #print(i, "NextPerimeter Path: ", finalPerimeterPath_perLayer)
                #print()
                print()
                        
                        
                # Reset Variables
                FlagFirstLayer = False
                perimeterPath_perLayer = []
                last_rawList = [0]



            # ---- END OF NEXT LAYER -----
            """


            # Se o atributo shape do objeto layer for uma lista vazia, o objeto layer é adicionado ao dicionário "layers" com a chave "height" e o loop continua para a próxima iteração.
            if layer.shape == []:
                self.layers[height] = layer
                continue
            # utiliza o método da classe "Layer" para criação do perímetro da camada atual
            layer.make_perimeter()
            # utiliza o método da classe "Layer" para criação dos limites do preenchimento da camada atual
            layer.make_infill_border()

            # gera os caminhos de preenchimento da camada atual baseado no método da classe "RectilinearInfill" que recebe os parãmetros referentes ao preenchimento fornecidos pelo arquivo yml
            infill_paths = infill_method.generate_infill(layer,
                                                         self.process.raster_gap,
                                                         self.process.infill_angle)
            # define a região flexível na camada atual baseado nos planos que compêm cada camada desta região já definida na função "slice"
            flex_regions = self.flex_planes.planes[height]

            # Se "flex_regions" não for uma lista, ele é convertido em uma lista
            if not type(flex_regions) == list:  # noqa: E721
                flex_regions = list(flex_regions.geoms)
            # Os caminhos do perímetro da camada são divididos pelas regiões flexíveis
            
            #******************
            #layer.perimeter_paths = split_by_regions(layer.perimeter_paths, flex_regions)  # noqa: E501
            
            # Os caminhos de preenchimento também são divididos pelas regiões flexíveis
            
            #******************
            #infill_paths = split_by_regions(infill_paths, flex_regions)

            # Se esta for a primeira iteração do loop (ou seja, se estamos na primeira camada), os caminhos do perímetro da saia são adicionados ao perímetro da camada
            if i == 0:  # skirt
                for path in skirt.perimeter_paths.geoms:
                    # com raster, faz a saia com os parâmetros fornecidos do arquivo yml
                    layer.perimeter.append(
                        Raster(path, self.process.first_layer_flow, self.process.speed))

            # ----- BEGIN OF PERIMETER ---------
            List_perimeters = []

            # percorre cada caminho no perímetro da camada. Se o caminho estiver dentro de uma região flexível, ele é dividido em um caminho flexível e um caminho de retração, que são adicionados ao perímetro da camada. Se o caminho não estiver dentro de uma região flexível, ele é adicionado ao perímetro da camada como está
            if i == 0:
                FlagPerimeterFirstLayer = True
                FlagInfillFirstLayer = True
            else:
                FlagPerimeterFirstLayer = False
                FlagInfillFirstLayer = False


            #CAST list of LINESTRINGS to list of Lists (tuples are coords.)
            for j in list(layer.perimeter_paths.geoms):
                List_perimeters.append(RawList_Points(j, makeTuple=True))


            #### --- APPLY FIRST LAYER PERIMETER TO RASTER ---
            if FlagPerimeterFirstLayer == True: # First layer, adjust the flow

                regularPerimeter = List_perimeters.copy() # --- For Regular Perimeters (The same along Z axis)

                #### Optimize path of each perimeter (e.g internal, external)
                for p in range(len(List_perimeters)-1):
                    List_perimeters[p+1] = bestPath_Infill2Perimeter(List_perimeters[p+1], List_perimeters[p])


                for n in range(len(List_perimeters)):
                    LinestringPerimeter_perLayer = sp.LineString(List_perimeters[n])

                    layer.perimeter.append(
                                Raster(LinestringPerimeter_perLayer, self.process.first_layer_flow, self.process.speed))
                    

            #### --- APPLY OTHER LAYERS PERIMETER TO RASTER ---
            if FlagPerimeterFirstLayer == False: ### Outras camadas do Perimetro
                
                ##### Optimize Path infill -> nextPerimeter
                if NextPerimeter_calculated == True:

                    if i in [6, 7, 8]:
                        print(i, "PERIMETRO::ANTES: ", List_perimeters)
                    List_perimeters[0] = optmizedPerimeterPath_perLayer

                    #### Optimize path of each perimeter (e.g internal, external)
                    #for p in range(len(List_perimeters)-1):
                        #List_perimeters[p+1] = bestPath_Infill2Perimeter(List_perimeters[p+1], List_perimeters[p])
                    
                    NextPerimeter_calculated = False
                
                if i in [6, 7, 8]:
                    print(i, "PERIMETRO::DEPOIS: ", List_perimeters)


                for n in range(len(List_perimeters)):

                    LinestringPerimeter_perLayer = sp.LineString(List_perimeters[n])
                    layer.perimeter.append(
                                Raster(LinestringPerimeter_perLayer, self.process.first_layer_flow, self.process.speed))


            # Reset Variables
            FlagPerimeterFirstLayer = False


            # Concatenates lists of tuples (INFILL)
            finalInfillPath_perLayer = RawList_Points(list(infill_paths.geoms)[0], makeTuple=True)

            #### Optimize Infill Path (same layer Perimeter->Infill)
            finalInfillPath_perLayer = bestPath_Perimeter2Infill(List_perimeters[-1], finalInfillPath_perLayer)

            LinestringInfill_perLayer = sp.LineString(finalInfillPath_perLayer)

            #### --- APPLY FIRST LAYER INFILL TO RASTER ---
            # Apply to Raster (adiciona ao perímetro da primeira camada como deve ser o fluxo e a velocidade do raster)
            if FlagInfillFirstLayer == True: # First layer, adjust the flow

                layer.infill.append(
                            Raster(LinestringInfill_perLayer, self.process.first_layer_flow, self.process.speed))
                
                optmizedPerimeterPath_perLayer = bestPath_Infill2Perimeter(regularPerimeter[0], finalInfillPath_perLayer)
                NextPerimeter_calculated = True


            

            #### --- APPLY OTHER LAYERS INFILL TO RASTER ---
            if FlagInfillFirstLayer == False:
                layer.infill.append(
                            Raster(LinestringInfill_perLayer, self.process.flow, self.process.speed))
                
                optmizedPerimeterPath_perLayer = bestPath_Infill2Perimeter(regularPerimeter[0], finalInfillPath_perLayer)
                NextPerimeter_calculated = True

                if i in [6, 7, 8]:
                    print(i, "for Flag FALSE Infill: ", finalInfillPath_perLayer)
                    print()
                    print()


            FlagInfillFirstLayer = False

            # a camada atual é adicionada ao dicionário "layers" com a chave "height" referente a altura desta camada
            self.layers[height] = layer

    # ----- END OF INFILL ----------

    def export_gcode(self, filename):
        if self.process.verbose is True:  # linha de verificação fornecida dentro das configurações do próprio arquivo yml
            # mensagem quando executa essa função do programa
            print("exporting gcode to {}".format(filename))

        # cria uma instância "gcode_exporter" da classe "GcodeExporter" que recebe os parãmetros referentes ao script cabeçalho inicial e final do modelo da impressora utilizada fornecido pelo arquivo yml
        gcode_exporter = self.process.gcode_exporter(start_script=self.process.start_script,
                                                     end_script=self.process.end_script)
        # utiliza o método "make_gcode" da classe "GcodeExporter" para gerar o gcode de todas as camadas da peça 3D
        gcode_exporter.make_gcode(self)
        # utiliza o método "export_gcode" da classe "GcodeExporter" para salvar todas as linhas do gcode gerado, fornecidas por uma lista, em um arquivo com o nome fornecido pelo usuário
        gcode_exporter.export_gcode(filename)
