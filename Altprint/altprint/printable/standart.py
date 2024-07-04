from altprint.printable.base import BasePrint
from altprint.slicer import STLSlicer
from altprint.layer import Layer, Raster
from altprint.height_method import StandartHeightMethod
from altprint.infill.rectilinear_infill import RectilinearInfill
from altprint.gcode import GcodeExporter
from altprint.settingsparser import SettingsParser

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

    def make_layers(self):
        fig = go.Figure()

        if self.process.verbose is True:
            print("generating layers ...")
        infill_method = self.process.infill_method()

        skirt = Layer(self.sliced_planes.planes[self.heights[0]],
                      self.process.skirt_num,
                      self.process.skirt_gap,
                      - self.process.skirt_distance - self.process.skirt_gap * self.process.skirt_num, #noqa: E501
                      self.process.overlap)
        skirt.make_perimeter()

        for i, height in enumerate(self.heights):
            layer = Layer(self.sliced_planes.planes[height],
                          self.process.perimeter_num,
                          self.process.perimeter_gap,
                          self.process.external_adjust,
                          self.process.overlap)
            layer.make_perimeter()
            layer.make_infill_border()
            if type(self.process.infill_angle) == list: # noqa: E721
                infill_angle = self.process.infill_angle[i%len(self.process.infill_angle)] # noqa: E501
            else:
                infill_angle = self.process.infill_angle
            infill_paths = infill_method.generate_infill(layer,
                                                         self.process.raster_gap,
                                                         infill_angle)

            if i==0: #skirt
                for path in skirt.perimeter_paths.geoms:
                    layer.perimeter.append(Raster(path, self.process.flow, self.process.speed)) # noqa: E501

            for path in layer.perimeter_paths.geoms:
                layer.perimeter.append(Raster(path, self.process.flow, self.process.speed)) # noqa: E501
            for path in infill_paths.geoms:               
                layer.infill.append(Raster(path, self.process.flow, self.process.speed))


            if i == 0 or i == 1:
                for perimeterLinestr in list(layer.perimeter_paths.geoms):

                    raw_perimeterPath = RawList_Points(perimeterLinestr, makeTuple=True)
                    trace_layer(fig, raw_perimeterPath, z=i+0.25)
                    


                for infillLinestr in list(infill_paths.geoms):

                    raw_infillPath = RawList_Points(infillLinestr, makeTuple=True)
                    print(raw_infillPath)
                    trace_layer(fig, raw_infillPath, z=i+0.5)
                    

            self.layers[height] = layer
        fig.show()

    def export_gcode(self, filename):
        if self.process.verbose is True:
            print("exporting gcode to {}".format(filename))
        gcode_exporter = self.process.gcode_exporter(start_script=self.process.start_script, # noqa: E501
                                                     end_script=self.process.end_script)
        gcode_exporter.make_gcode(self)
        gcode_exporter.export_gcode(filename)
