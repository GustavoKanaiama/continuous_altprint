from shapely import wkt
from shapely.geometry import LineString, Point
from shapely.ops import nearest_points  # Correção na importação
from itertools import permutations, product

from Altprint.altprint.printable.best_path import *
example = wkt.loads("MULTILINESTRING ((88.75 193.75, 88.75 101.25), (86.25 208.75, 86.25 101.25, 86.75 101.25, 86.75 208.75, 87.25 208.75, 87.25 101.25, 87.75 101.25, 87.75 208.75, 88.25 208.75, 88.25 101.25), (88.75 116.25, 89.25 116.25, 89.25 193.75, 89.75 193.75, 89.75 116.25, 90.25 116.25, 90.25 193.75, 90.75 193.75, 90.75 116.25, 91.25 116.25, 91.25 193.75, 91.75 193.75, 91.75 116.25, 92.25 116.25, 92.25 193.75, 92.75 193.75, 92.75 116.25, 93.25 116.25, 93.25 193.75, 93.75 193.75, 93.75 116.25, 94.25 116.25, 94.25 193.75, 94.75 193.75, 94.75 116.25, 95.25 116.25, 95.25 193.75, 95.75 193.75, 95.75 116.25, 96.25 116.25, 96.25 193.75, 96.75 193.75, 96.75 116.25, 97.25 116.25, 97.25 193.75, 97.75 193.75, 97.75 116.25, 98.25 116.25, 98.25 193.75, 98.75 193.75, 98.75 116.25, 99.25 116.25, 99.25 193.75, 99.75 193.75, 99.75 116.25, 100.25 116.25, 100.25 193.75, 100.75 193.75, 100.75 116.25, 101.25 116.25, 101.25 193.75, 101.75 193.75, 101.75 116.25, 102.25 116.25, 102.25 193.75, 102.75 193.75, 102.75 116.25, 103.25 116.25, 103.25 193.75, 103.75 193.75, 103.75 116.25, 104.25 116.25, 104.25 193.75, 104.75 193.75, 104.75 116.25, 105.25 116.25, 105.25 193.75, 105.75 193.75, 105.75 116.25, 106.25 116.25, 106.25 193.75, 106.75 193.75, 106.75 116.25, 107.25 116.25, 107.25 193.75, 107.75 193.75, 107.75 116.25, 108.25 116.25, 108.25 193.75, 108.75 193.75, 108.75 116.25, 109.25 116.25, 109.25 193.75, 109.75 193.75, 109.75 116.25, 110.25 116.25, 110.25 193.75, 110.75 193.75, 110.75 116.25, 111.25 116.25, 111.25 208.75, 111.75 208.75, 111.75 101.25, 112.25 101.25, 112.25 208.75, 112.75 208.75, 112.75 101.25, 113.25 101.25, 113.25 208.75, 113.75 208.75, 113.75 101.25), (111.25 193.75, 111.25 101.25))")
Raw_example = [RawList_Points(k, makeTuple=True) for k in example.geoms]


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

print(bruteForce_perm(Raw_example, sp.Point(110.75, 115,75)))