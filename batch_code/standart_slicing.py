from altprint.printable.standart_infillSlicer import StandartProcess, StandartPrint

import os

# Para Ricas **
os.chdir("D:/códigosVScode/continuous_altprint/Altprint")

# Para Stavo notebook
# os.chdir("C:/Users/gusta/OneDrive/Documentos/GitHub/continuous_altprint/Altprint")

# Para Stavo PC
# os.chdir("C:/Users/Gustavo Mariano/Documents/Github/continuous_altprint/Altprint")

process = StandartProcess(settings_file='standart_parameters.yml')
part = StandartPrint(process)


part.slice()
part.make_layers()
part.export_gcode("sliced_geometry.gcode")
