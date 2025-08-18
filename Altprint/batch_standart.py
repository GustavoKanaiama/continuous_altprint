from altprint.printable.standart_infillSlicer import StandartProcess, StandartPrint
from altprint.printable.multi import MultiPrint, MultiProcess

import os

# Para Ricas **
os.chdir("D:/códigosVScode/continuous_altprint/Altprint")

# Para Stavo notebook
# os.chdir("C:/Users/gusta/OneDrive/Documentos/GitHub/continuous_altprint/Altprint")

# Para Stavo PC
# os.chdir("C:/Users/Gustavo Mariano/Documents/Github/continuous_altprint/Altprint")

# --------------------------------------------------------------------

process1 = StandartProcess(settings_file='cube.yml')
part1 = StandartPrint(process1)


part1.slice()
part1.make_layers()
part1.export_gcode("flex_bar.gcode")

# --------------------------------------------------------------------

process2 = StandartProcess(settings_file='standart2.yml')
part2 = StandartPrint(process2)


part2.slice()
part2.make_layers()
part2.export_gcode("flex_bar.gcode")

# --------------------------------------------------------------------

process3 = StandartProcess(settings_file='standart3.yml')
part3 = StandartPrint(process3)


part3.slice()
part3.make_layers()
part3.export_gcode("flex_bar.gcode")

# --------------------------------------------------------------------

multi_process = MultiProcess(
    parts=[part1, part2, part3],
    start_script="scripts/start_prusaMK3S.gcode",
    end_script="scripts/end_prusaMK3S.gcode")

multi_part = MultiPrint(multi_process)
multi_part.slice()
multi_part.make_layers()
multi_part.export_gcode("batch_flex.gcode")
