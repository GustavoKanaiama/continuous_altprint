from altprint.printable.flex import FlexPrint, FlexProcess
import os

os.chdir("D:\códigosVScode\continuous_altprint\Altprint")

process = FlexProcess(settings_file='flex_bar.yml')

part = FlexPrint(process)
part.slice()
part.make_layers()
part.export_gcode("flex_bar(daniel).gcode")
