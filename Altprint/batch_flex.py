from altprint.printable.flex_continuous import FlexProcess, FlexPrint
from altprint.printable.multi import MultiPrint, MultiProcess

import os

# Para Ricas **
os.chdir("D:/códigosVScode/continuous_altprint/Altprint")

# Para Stavo notebook
# os.chdir("C:/Users/gusta/OneDrive/Documentos/GitHub/continuous_altprint/Altprint")

# Para Stavo PC
# os.chdir("C:/Users/Gustavo Mariano/Documents/Github/continuous_altprint/Altprint")

process1 = FlexProcess(settings_file='flex_bar.yml')
process2 = FlexProcess(settings_file='flex_bar2.yml')
process3 = FlexProcess(settings_file='flex_bar3.yml')

part1 = FlexPrint(process1)
part1.slice()
part1.make_layers()
part1.export_gcode("flex_bar.gcode")

part2 = FlexPrint(process2)
part2.slice()
part2.make_layers()
part2.export_gcode("flex_bar.gcode")

part3 = FlexPrint(process3)
part3.slice()
part3.make_layers()
part3.export_gcode("flex_bar.gcode")

multi_process = MultiProcess(
    parts=[part1, part2, part3],
    start_script="scripts/start_gtmax.gcode",
    end_script="scripts/end_gtmax.gcode")

multi_part = MultiPrint(multi_process)
multi_part.slice()
multi_part.make_layers()
multi_part.export_gcode("batch_flex.gcode")
