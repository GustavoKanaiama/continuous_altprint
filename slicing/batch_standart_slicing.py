from Altprint.standart_infillSlicer import StandartProcess, StandartPrint
from Altprint.multi import MultiPrint, MultiProcess

# --------------------------------------------------------------------

process1 = StandartProcess(
    settings_file='slicing/parameters/standart_parameters.yml')
part1 = StandartPrint(process1)


part1.slice()
part1.make_layers()

# --------------------------------------------------------------------

process2 = StandartProcess(
    settings_file='slicing/parameters/standart_parameters2.yml')
part2 = StandartPrint(process2)


part2.slice()
part2.make_layers()

# --------------------------------------------------------------------

process3 = StandartProcess(
    settings_file='slicing/parameters/standart_parameters3.yml')
part3 = StandartPrint(process3)


part3.slice()
part3.make_layers()

# --------------------------------------------------------------------

multi_process = MultiProcess(
    parts=[part1, part2, part3],
    start_script="slicing/gcode/start_prusaMK3S.gcode",
    end_script="slicing/gcode/end_prusaMK3S.gcode")

multi_part = MultiPrint(multi_process)
multi_part.slice()
multi_part.make_layers()
multi_part.export_gcode("slicing/parameters/sliced_geometry.gcode")
