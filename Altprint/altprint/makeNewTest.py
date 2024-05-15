# A dedicated entire script only for validate/visualize tests (the printing path, initial location, etc.)
'''
### --- How to use ---

#0- import makeNewTest.py functions

#1- Create a 'axes' object
ax = plt.axes(projection="3d")

# 2- call 'trace_line' function
trace_layer(infill, z=1)
trace_layer(perimeter, z=4)

# 3- plot the results
plt.show()

'''
import numpy as np
import matplotlib.pyplot as plt

#Function to trace a "line" (array with linspace) between two coordinates (x, y):
def trace_line(axes_obj, coord1, coord2, n_pts=50, first=False, last=False, z=1):
    #n_pts: number of points between two coordinates
    
    # Initial Point -> Green
    # Last Point -> Red

    x1, y1 = coord1
    x2, y2 = coord2
    if first ==True:
        #print initial values
        axes_obj.scatter(x1, y1, z, s=7, c='green')

        x_lin = np.linspace(x1+(abs(x1-x2)/n_pts), x2, n_pts)
        y_lin = np.linspace(y1+(abs(y1-y2)/n_pts), y2, n_pts)
    
    else:
        x_lin = np.linspace(x1, x2, n_pts)
        y_lin = np.linspace(y1, y2, n_pts)

    if last == True:
        #print last values
        axes_obj.scatter(x2, y2, z, s=7, c='red')

    axes_obj.scatter(x_lin, y_lin, z, s=0.4, c='blue')

    return 0

def trace_layer(axes_obj, layer_array, n_pts=50, z=1):

    for i in range(len(layer_array)-1):

        if i == 0:
            trace_line(axes_obj, layer_array[i], layer_array[i+1], first=True, n_pts=n_pts, z=z)

        elif i == len(layer_array)-2:
            trace_line(axes_obj, layer_array[i], layer_array[i+1], last=True, n_pts=n_pts, z=z)
        
        else:
            trace_line(axes_obj, layer_array[i], layer_array[i+1], n_pts=n_pts, z=z)
    
    return 0
