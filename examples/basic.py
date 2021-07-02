from altprint.baseprints import BasePrint
import matplotlib.pyplot as plt
from altprint.flow import calculate


snapfit = BasePrint()
snapfit.model = 'models/snapfit.stl'
snapfit.flex_model = 'models/snapfit_flex.stl'
snapfit.complete_fill = True
snapfit.flow = calculate(adjust=1.2)

snapfit.slice()
snapfit.make_layers(0.5, 0, fill=rectilinear_optimal)
snapfit.output_gcode("snapfit")
