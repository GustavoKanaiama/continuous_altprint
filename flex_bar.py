from altprint.printable.flex_copy import FlexPrint, FlexProcess
import os

# Para Ricas **
# os.chdir("D:\códigosVScode\Altprint")

# Para Stavo
os.chdir("C:/Users/gusta/OneDrive/Documentos/OtherThings_Python/Altprint")

process = FlexProcess(settings_file='flex_bar.yml')

part = FlexPrint(process)
part.slice()
part.make_layers()
part.export_gcode("flex_bar.gcode")
