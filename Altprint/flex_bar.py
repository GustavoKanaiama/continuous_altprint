from altprint.printable.flex_copy_copy import FlexPrint, FlexProcess
#from altprint.printable.standart import StandartPrint, StandartProcess
from altprint.printable.standart_copy_copy import StandartPrint, StandartProcess

import os

# Para Ricas **
# os.chdir("D:\códigosVScode\Altprint")

# Para Stavo notebook
os.chdir("C:/Users/gusta/OneDrive/Documentos/GitHub/continuous_altprint-1/Altprint")

# Para Stavo PC
#os.chdir("C:/Users/Gustavo Mariano/Documents/Github/continuous_altprint/Altprint")


process = FlexProcess(settings_file='flex_bar.yml')
#process = StandartProcess(settings_file='flex_bar.yml')


part = FlexPrint(process)
#part = StandartPrint(process)
part.slice()
part.make_layers()
part.export_gcode("flex_bar.gcode")
