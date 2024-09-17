from altprint.printable.standart import StandartPrint, StandartProcess

import os

# Para Ricas **
os.chdir("D:\códigosVScode\continuous_altprint\Altprint")

process = StandartProcess(settings_file='cube.yml')

part = StandartPrint(process)
part.slice()
part.make_layers()
part.export_gcode("cube.gcode")
