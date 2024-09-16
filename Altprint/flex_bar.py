from altprint.printable.standart_infillSlicer import StandartPrint, StandartProcess
from altprint. printable.flex_copy import FlexProcess, FlexPrint

import os

# Para Ricas **
# os.chdir("D:\códigosVScode\Altprint")

# Para Stavo notebook
os.chdir("C:/Users/gusta/OneDrive/Documentos/GitHub/continuous_altprint/Altprint")

# Para Stavo PC
#os.chdir("C:/Users/Gustavo Mariano/Documents/Github/continuous_altprint/Altprint")


val = "flex"

if val == "flex":
    process = FlexProcess(settings_file='flex_bar.yml')
    part = FlexPrint(process)

if val == "std":
    process = StandartProcess(settings_file='cube.yml')
    part = StandartPrint(process)
    

part.slice()
part.make_layers()
part.export_gcode("flex_bar_meu.gcode")
