from altprint.printable.base import BasePrint
from altprint.slicer import STLSlicer
from altprint.layer import Layer, Raster
from altprint.height_method import StandartHeightMethod
from altprint.infill.rectilinear_infill import RectilinearInfill
from altprint.gcode import GcodeExporter
from altprint.settingsparser import SettingsParser

##
from altprint.makeNewTest import trace_layer
import plotly.graph_objects as go
from altprint.printable.best_path import *

class StandartProcess():
    def __init__(self, **kwargs):
        prop_defaults = {
            "model_file": "",
            "slicer": STLSlicer(StandartHeightMethod()),
            "infill_method": RectilinearInfill,
            "infill_angle": [0, 90],
            "offset": (0, 0, 0),
            "external_adjust": 0.5,
            "perimeter_num": 2,
            "perimeter_gap": 0.5,
            "skirt_distance": 10,
            "skirt_num": 3,
            "skirt_gap": 0.5,
            "raster_gap": 0.5,
            "overlap": 0.0,
            "speed": 2400,
            "flow": 1.2,
            "gcode_exporter": GcodeExporter,
            "start_script": "",
            "end_script": "",
            "verbose": True,
        }


        for (prop, default) in prop_defaults.items():
            setattr(self, prop, kwargs.get(prop, default))

        if 'settings_file' in kwargs.keys():
            settings = SettingsParser().load_from_file(kwargs['settings_file'])
            for (setting, value) in settings.items():
                setattr(self, setting, value)

class StandartPrint(BasePrint):
    """The common print. Nothing special"""

    _height = float
    _layers_dict = dict[_height, Layer]

    def __init__(self, process: StandartProcess):
        self.process = process
        self.layers: _layers_dict = {} #noqa: F821
        self.heights: list[float] = []

    def slice(self):
        if self.process.verbose is True:
            print("slicing {} ...".format(self.process.model_file))
        slicer = self.process.slicer
        slicer.load_model(self.process.model_file)
        slicer.translate_model(self.process.offset)
        self.sliced_planes = slicer.slice_model()
        self.heights = self.sliced_planes.get_heights()

    def make_layers(self):  # método que gera as trajetórias das camadas, desde a saia inicial, e o perímetro/contorno e o preenchimento de cada camada
        fig = go.Figure()

        visualizing_layers = [9]


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
        
        ####
        ###    
        

        # loop que percorre todas as alturas na lista "heights". A função enumerate é usada para obter tanto o índice (i) quanto o valor (height) de cada altura.
        for i, height in enumerate(self.heights):


            # para cada altura, é criado um novo objeto "Layer", que recebe os parãmetros referentes ao perímetro fornecidos pelo arquivo yml, e atribuído a "layer" que é referente a cada camada
            layer = Layer(self.sliced_planes.planes[height],
                          self.process.perimeter_num,
                          self.process.perimeter_gap,
                          self.process.external_adjust,
                          self.process.overlap)

            # Se o atributo shape do objeto layer for uma lista vazia, o objeto layer é adicionado ao dicionário "layers" com a chave "height" e o loop continua para a próxima iteração.
            if layer.shape == []:
                self.layers[height] = layer
                continue
            # utiliza o método da classe "Layer" para criação do perímetro da camada atual
            layer.make_perimeter()
            # utiliza o método da classe "Layer" para criação dos limites do preenchimento da camada atual
            layer.make_infill_border()



            # define a região flexível na camada atual baseado nos planos que compêm cada camada desta região já definida na função "slice"

            # Os caminhos do perímetro da camada são divididos pelas regiões flexíveis
            
            #******************
            #layer.perimeter_paths = split_by_regions(layer.perimeter_paths, flex_regions)  # noqa: E501
            
            # Os caminhos de preenchimento também são divididos pelas regiões flexíveis
            
            #******************
            #infill_paths = split_by_regions(infill_paths, flex_regions)

            # Se esta for a primeira iteração do loop (ou seja, se estamos na primeira camada), os caminhos do perímetro da saia são adicionados ao perímetro da camada
            List_skirt = []
            if i == 0:  # skirt
                for path in skirt.perimeter_paths.geoms:
                    # com raster, faz a saia com os parâmetros fornecidos do arquivo yml
                    layer.perimeter.append(
                        Raster(path, self.process.first_layer_flow, self.process.speed))
                    
                    List_skirt.append(RawList_Points(path, makeTuple=True))
            
                lastLoop_skirt = List_skirt[-1]
                    

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
            for path in list(layer.perimeter_paths.geoms):
                if i ==0:
                    print()
                    print(path)
                List_perimeters.append(RawList_Points(path, makeTuple=True))

            # List_perimeters[0] -> externo
            # List_perimeters[1] -> interno
            lastPointPerimeter = 0

            #### --- APPLY FIRST LAYER PERIMETER TO RASTER ---
            if FlagPerimeterFirstLayer == True: # First layer, adjust the flow

                for p in range(len(List_perimeters)):
                    List_perimeters[p] = bestPath_Infill2Perimeter(List_perimeters[p], lastLoop_skirt)

                for n in range(len(List_perimeters)):
                    LinestringPerimeter_perLayer = sp.LineString(List_perimeters[n])

                    layer.perimeter.append(
                                Raster(LinestringPerimeter_perLayer, self.process.first_layer_flow, self.process.speed))
                    
                    
            #### --- APPLY OTHER LAYERS PERIMETER TO RASTER ---
            if FlagPerimeterFirstLayer == False: ### Outras camadas do Perimetro

                for p in range(len(List_perimeters)):
                    List_perimeters[p] = bestPath_Infill2Perimeter(List_perimeters[p], Last_infillList_previousLayer)
                

                for n in range(len(List_perimeters)):

                    LinestringPerimeter_perLayer = sp.LineString(List_perimeters[n])
                    layer.perimeter.append(
                                Raster(LinestringPerimeter_perLayer, self.process.first_layer_flow, self.process.speed))
            


            lastPointPerimeter = List_perimeters[-1][-1]


            ## ---- VISUALIZE perimeter layer ----
            if i in visualizing_layers:
                trace_layer(fig, List_perimeters[0], z=i)
                trace_layer(fig, List_perimeters[1], z=i)


            # Reset Variables
            FlagPerimeterFirstLayer = False
            List_Infills = []


            if type(self.process.infill_angle) == list:
                infill_angle = self.process.infill_angle[i%len(self.process.infill_angle)]
            else:
                infill_angle = self.process.infill_angle

            infill_paths = infill_method.generate_infill(layer,
                                                         self.process.raster_gap,
                                                         infill_angle)
            

            #### --- APPLY FIRST LAYER INFILL TO RASTER ---
            
            if FlagInfillFirstLayer == True: # First layer, adjust the flow

                # Apply to Raster (adiciona ao perímetro da primeira camada como deve ser o fluxo e a velocidade do raster)


                for InfillPath in list(infill_paths.geoms):
                    List_Infills.append(RawList_Points(InfillPath, makeTuple=True))

                #Fazer a lista de linestrings do infill virar uma listas Raw
                Infill_RawList, cp = searchAndSplit_alt(List_Infills, lastPointPerimeter)


                for raw_infillPath in Infill_RawList:
                    LinestringInfill_perLayer = sp.LineString(raw_infillPath)
                    layer.infill.append(
                            Raster(LinestringInfill_perLayer, self.process.first_layer_flow, self.process.speed))
                    if i in visualizing_layers:
                        trace_layer(fig, raw_infillPath, z=i+0.3)

                        


            #### --- APPLY OTHER LAYERS INFILL TO RASTER ---
            if FlagInfillFirstLayer == False:

                for InfillPath in list(infill_paths.geoms):
                    List_Infills.append(RawList_Points(InfillPath, makeTuple=True))


                Infill_RawList, cp = searchAndSplit_alt(List_Infills, lastPointPerimeter)

                for raw_infillPath in Infill_RawList:
                    LinestringInfill_perLayer = sp.LineString(raw_infillPath)
                    layer.infill.append(
                            Raster(LinestringInfill_perLayer, self.process.first_layer_flow, self.process.speed))
                    if i in visualizing_layers:
                        trace_layer(fig, raw_infillPath, z=i+0.5)


            Last_infillList_previousLayer = raw_infillPath.copy()

            FlagInfillFirstLayer = False

            # a camada atual é adicionada ao dicionário "layers" com a chave "height" referente a altura desta camada
            self.layers[height] = layer
        
        #fig.show()

    # ----- END OF INFILL ----------
    

    def export_gcode(self, filename):
        if self.process.verbose is True:
            print("exporting gcode to {}".format(filename))
        gcode_exporter = self.process.gcode_exporter(start_script=self.process.start_script, # noqa: E501
                                                     end_script=self.process.end_script)
        gcode_exporter.make_gcode(self)
        gcode_exporter.export_gcode(filename)
