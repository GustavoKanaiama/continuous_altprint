

from Altprint.flex_continuous import FlexProcess, FlexPrint


process = FlexProcess(settings_file="slicing/parameters/flex_parameters.yml")
part = FlexPrint(process)


part.slice()
part.make_layers()
part.export_gcode("slicing/parameters/sliced_geometry.gcode")
