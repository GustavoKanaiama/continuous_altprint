

from Altprint.flex_continuous_copy import FlexProcess, FlexPrint


process = FlexProcess(settings_file="slicing/parameters/dev_flex_parameters.yml")
part = FlexPrint(process)


part.slice()
part.make_layers()
part.export_gcode("slicing/gcode/sliced_geometry.gcode")
