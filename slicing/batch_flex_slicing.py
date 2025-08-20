from Altprint.flex_continuous import FlexProcess, FlexPrint
from Altprint.multi import MultiPrint, MultiProcess

process1 = FlexProcess(settings_file="slicing/parameters/flex_parameters.yml")
process2 = FlexProcess(settings_file="slicing/parameters/flex_parameters2.yml")
process3 = FlexProcess(settings_file="slicing/parameters/flex_parameters3.yml")

part1 = FlexPrint(process1)
part1.slice()
part1.make_layers()

part2 = FlexPrint(process2)
part2.slice()
part2.make_layers()

part3 = FlexPrint(process3)
part3.slice()
part3.make_layers()

multi_process = MultiProcess(
    parts=[part1, part2, part3],
    start_script="slicing/gcode/start_prusaMK3S.gcode",
    end_script="slicing/gcode/end_prusaMK3S.gcode")

multi_part = MultiPrint(multi_process)
multi_part.slice()
multi_part.make_layers()
multi_part.export_gcode("slicing/parameters/sliced_geometry.gcode")
