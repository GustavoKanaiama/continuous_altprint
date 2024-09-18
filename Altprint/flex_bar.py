from altprint. printable.flex_copy import FlexProcess, FlexPrint

import os

# Para Ricas **
os.chdir("D:/códigosVScode/continuous_altprint/Altprint")

# Para Stavo notebook
# os.chdir("C:/Users/gusta/OneDrive/Documentos/GitHub/continuous_altprint/Altprint")

# Para Stavo PC
# os.chdir("C:/Users/Gustavo Mariano/Documents/Github/continuous_altprint/Altprint")

process = FlexProcess(settings_file='flex_bar.yml')
part = FlexPrint(process)


part.slice()
part.make_layers()
part.export_gcode("flex_bar.gcode")
