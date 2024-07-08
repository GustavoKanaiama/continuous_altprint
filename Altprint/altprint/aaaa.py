from printable.best_path import *
import shapely as sp
import matplotlib.pyplot as plt
import networkx as nx


list1 = [[(90.25, 139.75), (100.25, 139.75), (119.75, 139.75),  (109.75, 110.25), (109.75, 100.25), (100.25, 100.25)],
         [(90.75, 139.25), (100.75, 139.25), (100.75, 149.25),  (119.25, 139.25), (119.25, 130.75), (109.25, 130.75)]]
print(list1[0])
print()
print(list1[1])
print()
print()
print(searchAndSplit(list1, (90.75, 139.25)))
print()
#print(sp.LineString([(109.25, 130.75)]))


"""
list2 = [(108.75, 118.75), (108.75, 111.25), (109.25, 111.25)]
list3 = [(109.25, 118.75), (109.75, 118.75), (109.75, 111.25)]

edge_list = [("Pi", "P1'", 1), ("Pi", "P1''", 1),
             ("P", "P1'", 1), ("P", "P1''", 1), ("P", "P2", 5), ("P", "P2'", 12),
             ("P1'", "P1''", 4), ("P1'", "P2", 5), ("P1'", "P2'", 10),
             ("P1''", "P2", 10), ("P1''", "P2'", 12),
             ("P2", "P2'", 1)]

G = nx.Graph()
G.add_weighted_edges_from(edge_list)

pos = nx.shell_layout(G)
nx.draw_networkx(G,pos, node_size=600)

labels = nx.get_edge_attributes(G,'weight')

nx.draw_networkx_edge_labels(G,pos,edge_labels=labels)

path = nx.single_source_shortest_path(G, "Pi")
print(path)

plt.show()

"""