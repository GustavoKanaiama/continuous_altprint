from altprint.printable.flex_continuous import FlexProcess, FlexPrint
from altprint.printable.multi import MultiPrint, MultiProcess

import os

# Para Ricas **
os.chdir("D:/códigosVScode/continuous_altprint/Altprint")

# Para Stavo notebook
# os.chdir("C:/Users/gusta/OneDrive/Documentos/GitHub/continuous_altprint/Altprint")

# Para Stavo PC
# os.chdir("C:/Users/Gustavo Mariano/Documents/Github/continuous_altprint/Altprint")

process1 = FlexProcess(settings_file='flex_parameters.yml')
process2 = FlexProcess(settings_file='flex_parameters2.yml')
process3 = FlexProcess(settings_file='flex_parameters3.yml')

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
    start_script="scripts/start_prusaMK3S.gcode",
    end_script="scripts/end_prusaMK3S.gcode")

multi_part = MultiPrint(multi_process)
multi_part.slice()
multi_part.make_layers()
multi_part.export_gcode("sliced_geometry.gcode")
