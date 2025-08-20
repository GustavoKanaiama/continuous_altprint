from Altprint.standart_infillSlicer import StandartProcess, StandartPrint

process = StandartProcess(
    settings_file='slicing/parameters/standart_parameters.yml')
part = StandartPrint(process)


part.slice()
part.make_layers()
part.export_gcode("slicing/parameters/sliced_geometry.gcode")
