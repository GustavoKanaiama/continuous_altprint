from shapely import wkt
from shapely.geometry import LineString, Point
from shapely.ops import nearest_points  # Correção na importação
from itertools import permutations, product

import matplotlib.pyplot as plt
import geopandas as gpd
from Altprint.altprint.printable.best_path import *


#Raw_example = [RawList_Points(k, makeTuple=True) for k in example.geoms]


def order_list(list, best_path, best_directions):

    result = []

    for i in range(len(list)):
        # Inverte se tiver -1 no best directions
        if best_directions[i] == -1:
            list[i] = list[i][::-1]


    for i in range(len(list)):
        result.append(list[best_path[i]].copy())
    
    return result

# Função para calcular o custo total de um caminho
def path_cost(start_point, lines, path, directions):
    total_cost = 0
    current_point = start_point
    
    for i, line_index in enumerate(path):
        line_coords = lines[line_index]
        
        # Se a linha estiver invertida, inverte as coordenadas
        if directions[i] == -1:
            line_coords = line_coords[::-1]
        
        line = LineString(line_coords)
        
        # Adiciona a distância até o ponto mais próximo
        total_cost += current_point.distance(Point(line.coords[0]))  # Distância ao primeiro ponto da linha
        
        # Atualiza o ponto atual para o final da linha (respeitando a inversão)
        current_point = Point(line.coords[1])

    return total_cost

def bruteForce_perm(n_lists, start_point):
    # Define as linhas
    lines = n_lists

    # Gera todas as permutações possíveis de linhas
    line_permutations = list(permutations(range(len(lines))))

    # Gera todas as combinações de direções (1 = normal, -1 = invertida)
    directions = list(product([1, -1], repeat=len(lines)))

    # Inicializa a melhor solução
    best_path = None
    best_directions = None
    min_cost = float('inf')

    # Testa cada permutação e cada combinação de direções
    for perm in line_permutations:
        for dir_comb in directions:
            current_cost = path_cost(start_point, lines, perm, dir_comb)
            if current_cost < min_cost:
                min_cost = current_cost
                best_path = perm
                best_directions = dir_comb
    
    return best_path, best_directions


flex_regions = wkt.loads("MULTIPOLYGON (((170 75, 189.6 75, 190 75, 190 111.25999999999999, 190 112, 170.4 112, 170 112, 170 75.74000000000001, 170 75)))")


infill_path = wkt.loads("""MULTILINESTRING ((183.75 66.25, 184.25 66.25, 184.25 75), (184.25 75, 184.25 112), (184.25 112, 184.25 120.75, 184.75 120.75, 184.75 112), (184.75 112, 184.75 75), (184.75 75, 184.75 66.25, 185.25 66.25, 185.25 75), (185.25 75, 185.25 112), (185.25 112, 185.25 120.75, 185.75 120.75, 185.75 112), (185.75 112, 185.75 75), (185.75 75, 185.75 66.25, 186.25 66.25, 186.25 75), (186.25 75, 186.25 112), (186.25 112, 186.25 120.75, 186.75 120.75, 186.75 112), (186.75 112, 186.75 75), (186.75 75, 186.75 66.25, 187.25 66.25, 187.25 75), (187.25 75, 187.25 112), (187.25 112, 187.25 120.75, 187.75 120.75, 187.75 112), (187.75 112, 187.75 75), (187.75 75, 187.75 66.25, 188.25 66.25, 188.25 75), (188.25 75, 188.25 112), (188.25 112, 188.25 120.75, 188.75 120.75, 188.75 112), (188.75 112, 188.75 75), (188.75 75, 188.75 66.25), (171.25 66.25, 171.25 75), (171.25 75, 171.25 112), (171.25 112, 171.25 120.75, 171.75 120.75, 171.75 112), (171.75 112, 171.75 75), (171.75 75, 171.75 66.25, 172.25 66.25, 172.25 75), (172.25 75, 172.25 112), (172.25 112, 172.25 120.75, 172.75 120.75, 172.75 112), (172.75 112, 172.75 75), (172.75 75, 172.75 66.25, 173.25 66.25, 173.25 75), (173.25 75, 173.25 112), (173.25 112, 173.25 120.75, 173.75 120.75, 173.75 112), (173.75 112, 173.75 75), (173.75 75, 173.75 66.25, 174.25 66.25, 174.25 75), (174.25 75, 174.25 112), (174.25 112, 174.25 120.75, 174.75 120.75, 174.75 112), (174.75 112, 174.75 75), (174.75 75, 174.75 66.25, 175.25 66.25, 175.25 75), (175.25 75, 175.25 112), (175.25 112, 175.25 120.75, 175.75 120.75, 175.75 112), (175.75 112, 175.75 75), (175.75 75, 175.75 66.25, 176.25 66.25, 176.25 75), (176.25 75, 176.25 112), (176.25 112, 176.25 135.75, 176.75 135.75, 176.75 112), (176.75 112, 176.75 75), (176.75 75, 176.75 51.25, 177.25 51.25, 177.25 75), (177.25 75, 177.25 112), (177.25 112, 177.25 135.75, 177.75 135.75, 177.75 112), (177.75 112, 177.75 75), (177.75 75, 177.75 51.25, 178.25 51.25, 178.25 75), (178.25 75, 178.25 112), (178.25 112, 178.25 135.75, 178.75 135.75, 178.75 112), (178.75 112, 178.75 75), (178.75 75, 178.75 51.25, 179.25 51.25, 179.25 75), (179.25 75, 179.25 112), (179.25 112, 179.25 135.75, 179.75 135.75, 179.75 112), (179.75 112, 179.75 75), (179.75 75, 179.75 51.25, 180.25 51.25, 180.25 75), (180.25 75, 180.25 112), (180.25 112, 180.25 135.75, 180.75 135.75, 180.75 112), (180.75 112, 180.75 75), (180.75 75, 180.75 51.25, 181.25 51.25, 181.25 75), (181.25 75, 181.25 112), (181.25 112, 181.25 135.75, 181.75 135.75, 181.75 112), (181.75 112, 181.75 75), (181.75 75, 181.75 51.25, 182.25 51.25, 182.25 75), (182.25 75, 182.25 112), (182.25 112, 182.25 135.75, 182.75 135.75, 182.75 112), (182.75 112, 182.75 75), (182.75 75, 182.75 51.25, 183.25 51.25, 183.25 75), (183.25 75, 183.25 112), (183.25 112, 183.25 135.75, 183.75 135.75, 183.75 112), (183.75 112, 183.75 75), (183.75 75, 183.75 51.25))""")

def create_gaps(multipolygon, num_gap, perc_gap):

    mask = multipolygon
    xmin, ymin, xmax, ymax = mask.bounds

    distx_total = xmax - xmin

    dist_x = (distx_total - (1-perc_gap)*distx_total)/num_gap
    util_gap = (distx_total - (num_gap*dist_x))/(num_gap+1)

    x_pointer_min = xmin + util_gap
    x_pointer_max = xmin + util_gap + dist_x

    for i in range(num_gap):

        # Generate box and append to the box_list
        box = sp.geometry.box(x_pointer_min, ymin, x_pointer_max, ymax)
        
        # Refresh the x_pointer
        x_pointer_min = x_pointer_min + dist_x + util_gap
        x_pointer_max = x_pointer_max + dist_x + util_gap

        mask = mask.difference(box)

    final = multipolygon.difference(mask)

    return final

gap_regions = create_gaps(flex_regions, 5, 0.6)

for path in infill_path.geoms:
    path_printed = False

    for region in flex_regions.geoms:

        its_flex = path.within(region.buffer(0.05, join_style=2))

        if its_flex:
            #vejo se tem gap ou nn
            for gap in gap_regions.geoms:
                
                its_gap = path.within(gap.buffer(0.05, join_style=2))

                if not its_gap:
                    print("PRINTED REGIAO FLEXIVEL!, ", path)
                    path_printed = True
                    break

                if its_gap:
                    print("É GAPPPP, ", path)

            if path_printed:
                break



        if not its_flex and not path_printed:
            print("PRINTED REGIAO NORMAL!, ", path)

p = gpd.GeoSeries(gap_regions)
p.plot()
plt.show()