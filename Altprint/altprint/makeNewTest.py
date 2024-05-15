# A dedicated entire script only for validate/visualize tests (the printing path, initial location, etc.)
'''
### --- How to use ---

#0- import makeNewTest.py functions
# 0- import plotly.graph_objects as go

#1- Create a 'fig' object
fig = go.Figure()

# 2- call 'trace_line' function
trace_layer(infill, z=1)
trace_layer(perimeter, z=4)

# 3- plot the results
fig.show()

'''
import plotly.graph_objects as go


def trace_layer(fig_obj, data, z=1):

    #Define initial Point
    x_initial = [data[0][0]]
    y_initial = [data[0][1]]
    z_initial = [z]

    #Define last Point
    x_last = [data[-1][0]]
    y_last = [data[-1][1]]
    z_last = [z]

    #Define 'trace line' data
    x_data = [x for x,y in data]
    y_data = [y for x,y in data]
    z_data = [z for i in range(len(data))]

    #Add trace line
    fig_obj.add_trace(go.Scatter3d(x=x_data, y=y_data, z=z_data, marker=dict(color='Blue',size=1)))
    
    #Add initial point
    fig_obj.add_trace(go.Scatter3d(x=x_initial, y=y_initial, z=z_initial, marker=dict(color='Green',size=5)))

    #Add last point
    fig_obj.add_trace(go.Scatter3d(x=x_last, y=y_last, z=z_last, marker=dict(color='Red',size=5)))

    return 0

'''
fig = go.Figure()

trace_layer(fig, data, 2)

fig.show()
'''