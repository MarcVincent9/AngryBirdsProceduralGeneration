from random import randint
from random import random
from random import uniform
from math import sqrt, ceil
from copy import deepcopy
import itertools

# blocks number and size
blocks = {'1':[0.84,0.84], '2':[0.85,0.43], '3':[0.43,0.85], '4':[0.43,0.43],
          '5':[0.22,0.22], '6':[0.43,0.22], '7':[0.22,0.43], '8':[0.85,0.22],
          '9':[0.22,0.85], '10':[1.68,0.22], '11':[0.22,1.68],
          '12':[2.06,0.22], '13':[0.22,2.06]}

# blocks number and name
# (blocks 3, 7, 9, 11 and 13) are their respective block names rotated 90 derees clockwise
block_names = {'1':"SquareHole", '2':"RectFat", '3':"RectFat", '4':"SquareSmall",
               '5':"SquareTiny", '6':"RectTiny", '7':"RectTiny", '8':"RectSmall",
               '9':"RectSmall",'10':"RectMedium",'11':"RectMedium",
               '12':"RectBig",'13':"RectBig"}

# additional objects number and name
additional_objects = {'1':"TriangleHole", '2':"Triangle", '3':"Circle", '4':"CircleSmall"}

# additional objects number and size
additional_object_sizes = {'1':[0.82,0.82],'2':[0.82,0.82],'3':[0.8,0.8],'4':[0.45,0.45]}

# blocks number and probability of being selected
probability_table_blocks = {'1':0.10, '2':0.10, '3':0.10, '4':0.05,
                            '5':0.02, '6':0.05, '7':0.05, '8':0.10,
                            '9':0.05, '10':0.16, '11':0.04,
                            '12':0.16, '13':0.02}

# materials that are available
materials = ["wood", "stone", "ice"]

# bird types number and name
bird_names = {'1':"BirdRed", '2':"BirdBlue", '3':"BirdYellow", '4':"BirdBlack", '5':"BirdWhite"}

# bird types number and probability of being selected
bird_probabilities = {'1':0.35, '2':0.2, '3':0.2, '4':0.15, '5':0.1}

TNT_block_probability = 0.3

pig_size = [0.5,0.5]    # size of pigs

platform_size = [0.62,0.62]     # size of platform sections

edge_buffer = 0.11      # buffer uesd to push edge blocks further into the structure center (increases stability)

absolute_ground = -3.5          # the position of ground within level


minimum_height_gap = 3.5        # y distance min between platforms
platform_distance_buffer = 0.4  # x_distance min between platforms / y_distance min between platforms and ground structures

# defines the levels area (ie. space within which structures/platforms can be placed)
level_width_min = -3.0
level_width_max = 9.0
level_height_min = -2.0         # only used by platforms, ground structures use absolute_ground to determine their lowest point
level_height_max = 6.0

pig_precision = 0.01                # how precise to check for possible pig positions on ground

min_ground_width = 2.5                      # minimum amount of space allocated to ground structure

max_attempts = 100                          # number of times to attempt to place a platform before abandoning it

emplacement = "Science-Birds-Windows\\ScienceBirds_Data\\StreamingAssets\\Levels\\"





# différentes marges
support_margin = 0.15 
overlap_margin = 0.01
edge_margin = 0.05

nb_essais_largeur = 4
max_peaks = 5           # maximum number of peaks a structure can have (up to 5)

building_bridges = True # favorise les blocs du dessous qui joignent les blocs du dessus
proba_building_bridges = .5

min_peak_split = 5     # minimum distance between two peak blocks of structure
max_peak_split = 100     # maximum distance between two peak blocks of structure

proba_inversion_UPi = .75
proba_inversion_PiU = .75

ground_structure_height_limit = level_height_max - absolute_ground #((level_height_max - minimum_height_gap) - absolute_ground)/1.5    # desired height limit of ground structures

# pour chaque hauteur, on stocke une distribution de probabilité sur les blocs de cette hauteur
blocks_by_height = {}
for item, size in blocks.items():
    height = round(size[1], 1)
    if height in blocks_by_height:
        blocks_by_height[height].append(item)
    else:
        blocks_by_height[height] = [item]
    
# probabilité de choisir une hauteur de bloc donnée
probability_table_heights = {}    
for height, items in blocks_by_height.items():
    tmp = sum(probability_table_blocks[item] for item in items)
    probability_table_heights[height] = tmp
    blocks_by_height[height] = {item:round(probability_table_blocks[item]/tmp, 2) for item in items}
    
    
prnt = False # active l'affiche détaillé (utilisé pour le débug)
        




# choose a random item/block from the blocks dictionary based on probability table

def choose_item(table):
    ran_num = uniform(0.0,1.0)
    keys = list(table.keys())
    selected_num = 0
    while ran_num > 0:
        ran_num = ran_num - table[keys[selected_num]]
        selected_num = selected_num + 1
    return keys[selected_num-1]




# finds the width of the given structure

def find_structure_width(structure):
    min_x = 999999.9
    max_x = -999999.9
    for block in structure:
        if round((block[1]-(blocks[str(block[0])][0]/2)),10) < min_x:
            min_x = round((block[1]-(blocks[str(block[0])][0]/2)),10)
        if round((block[1]+(blocks[str(block[0])][0]/2)),10) > max_x:
            max_x = round((block[1]+(blocks[str(block[0])][0]/2)),10)
    return (round(max_x - min_x,10))



   
# finds the height of the given structure

def find_structure_height(structure):
    min_y = 999999.9
    max_y = -999999.9
    for block in structure:
        if round((block[2]-(blocks[str(block[0])][1]/2)),10) < min_y:
            min_y = round((block[2]-(blocks[str(block[0])][1]/2)),10)
        if round((block[2]+(blocks[str(block[0])][1]/2)),10) > max_y:
            max_y = round((block[2]+(blocks[str(block[0])][1]/2)),10)
    return (round(max_y - min_y,10))




# renvoie la coordonnée X du bord gauche d'un bloc déjà placé
def left_edge(block):
    return round(block[1] - blocks[block[0]][0] / 2.0, 10)

   
    

# renvoie la coordonnée X du bord droit d'un bloc déjà placé
def right_edge(block):
    return round(block[1] + blocks[block[0]][0] / 2.0, 10)




# vérifie si un bloc du type choisi serait capable de supporter à lui seul un bloc de la ligne du dessus
def check_large_enough(chosen_type, upper_block):
    return blocks[chosen_type][0] >= blocks[upper_block[0]][0]




# vérifie si un bloc du type choisi serait trop large pour soutenir uniquement un bord du bloc de la ligne du dessus
# sachant qu'il ne doit pas y avoir de chevauchement et qu'il doit rester assez de place pour mettre un bloc sous l'autre bord
def check_too_large(chosen_type, upper_block, new_bottom, overlap_side):
    if overlap_side == "left":
        return right_edge(new_bottom[-1]) + overlap_margin + blocks[chosen_type][0] > right_edge(upper_block) - support_margin - overlap_margin
    return left_edge(new_bottom[0]) - overlap_margin - blocks[chosen_type][0] < left_edge(upper_block) + support_margin + overlap_margin




# détermine l'intervalle dans lequel on peut placer un bloc dont le rôle est de supporter un bloc supérieur,
# entièrement ou sous le bord gauche ou droit (paramètre "part")
# sachant qu'il ne faut pas chevaucher les blocs existants sur un bord (paramètre "check_overlap")
def limits(upper_block, item_type, part, check_overlap, current_tree_bottom, new_bottom, max_width):
    half_width = blocks[item_type][0] / 2.0
    
    if part == "center":
        left_limit = right_edge(upper_block) - half_width
        right_limit = left_edge(upper_block) + half_width
        
    elif part == "left":
        left_limit = left_edge(upper_block) - half_width + support_margin 
        right_limit = left_edge(upper_block) + half_width + edge_margin 
        right_limit = min(right_limit, upper_block[1] - half_width) # pour ne pas mettre le bloc au centre...
        
    else : # part == "right"
        left_limit = right_edge(upper_block) - half_width - edge_margin 
        right_limit = right_edge(upper_block) + half_width - support_margin 
        left_limit = max(left_limit, upper_block[1] + half_width) # pour ne pas mettre le bloc au centre...
    
    if check_overlap == "left":
        left_limit = max(left_limit, right_edge(new_bottom[-1]) + half_width + overlap_margin) # overlap check
        right_limit = min(right_limit, left_edge(new_bottom[0]) + max_width - half_width) # on essaie de ne pas dépasser la largeur max
        right_limit = max(left_limit, right_limit)
        
    elif check_overlap == "right":
        right_limit = min(right_limit, left_edge(new_bottom[0]) - half_width - overlap_margin) # overlap check
        left_limit = max(left_limit, right_edge(current_tree_bottom[-1]) - max_width + half_width) # on essaie de ne pas dépasser la largeur max
        left_limit = min(left_limit, right_limit)
        
    elif check_overlap == "no":
        left_limit = max(left_limit, right_edge(current_tree_bottom[-1]) - max_width + half_width) # on essaie de ne pas dépasser la largeur max
        right_limit = min(right_limit, left_edge(current_tree_bottom[0]) + max_width - half_width) # on essaie de ne pas dépasser la largeur max
        left_limit = min(left_limit, right_limit) # au cas où left_limit > right_limit : échec en vue
        
    return (left_limit, right_limit)
    
    


# vérifie si un bloc inférieur donné supporte déjà un bloc supérieur donné
# au milieu, à gauche ou à droite selon le paramètre "part"
def new_check_support(upper_block, lower_block, part):
    if part == "center":
        return left_edge(lower_block) <= left_edge(upper_block) + edge_margin and right_edge(upper_block) - edge_margin <= right_edge(lower_block)
    if part == "left":
        return left_edge(lower_block) <= left_edge(upper_block) + edge_margin and left_edge(upper_block) + support_margin <= right_edge(lower_block)
    if part == "right":
        return left_edge(lower_block) <= right_edge(upper_block) - support_margin and right_edge(upper_block) - edge_margin <= right_edge(lower_block)
    



# ajoute un bloc d'un type donné pour soutenir au milieu, à gauche ou à droite un bloc de la ligne supérieure
def add_block(i, current_tree_bottom, chosen_type, new_bottom, max_width, part, check_overlap):
    upper_block = current_tree_bottom[i]
    
    # on détermine l'intervalle dans lequel peut être placé le nouveau bloc
    left_limit, right_limit = limits(upper_block, chosen_type, part, check_overlap, current_tree_bottom, new_bottom, max_width)
    position = None
    
    if prnt: print((left_limit, right_limit), end=" ")
    
    # quand cette option est activée, il existe une probabilité de placer le bloc à l'extrémité de l'intervalle
    # si cela lui permet de soutenir d'autres blocs
    if building_bridges:
        
        if check_overlap != "right" and i < len(current_tree_bottom)-1 \
        and new_check_support(current_tree_bottom[i+1], [chosen_type, right_limit], part = "left") \
        and random() < proba_building_bridges:
            position = right_limit
            
        if check_overlap != "left" and i > 0 \
        and new_check_support(current_tree_bottom[i-1], [chosen_type, left_limit], part = "right") \
        and random() < proba_building_bridges:
            position = left_limit
           
    # sinon l'emplacement est choisi de manière aléatoire uniforme dans l'intervalle
    if position == None:
        position = uniform(left_limit, right_limit)
    new_block = [chosen_type, round(position, 10), 0]
    
    # en construisant la nouvelle ligne, on fait en sorte de trier les blocs de la gauche vers la droite
    if check_overlap == "right": new_bottom.insert(0, new_block)
    else: new_bottom.append(new_block)
    
    
    

# vérifie si, étant donné un type de bloc, l'on est obligé de placer le nouveau bloc sous le milieu du bloc supérieur plutôt que sous les bords
def center_mandatory(chosen_type, upper_block, new_bottom, overlap_side):
    if overlap_side != "no" and check_too_large(chosen_type, upper_block, new_bottom, overlap_side):
        return True
    return blocks[upper_block[0]][0] == 0.22 and blocks[chosen_type][1] > 0.22

    
    
# vérifie si, étant donné un type de bloc, l'on est obligé de placer le nouveau bloc sous les bords du bloc supérieur plutôt que sous le milieu
def edges_mandatory(chosen_type, upper_block, new_bottom, overlap_side):
    return not(check_large_enough(chosen_type, upper_block))
    
    
    

# initialise une nouvelle ligne en supportant un bloc supérieur donné ("start") 
def initialize_line(current_tree_bottom, start, height, new_bottom, max_width):
    if prnt: print("\nA ", end="")
    upper_block = current_tree_bottom[start]
    chosen_type = choose_item(blocks_by_height[height]) # on choisit un bloc de la hauteur donnée
    
    if not(center_mandatory(chosen_type, upper_block, new_bottom, overlap_side = "no")) \
    and (edges_mandatory(chosen_type, upper_block, new_bottom, overlap_side = "no") or random() < .5):
        
        # un bloc sous chaque bord
        if prnt: print("edges ", end="")
        if random() < .5:
            add_block(start, current_tree_bottom, chosen_type, new_bottom, max_width, part = "left", check_overlap = "no")
            chosen_type = choose_item(blocks_by_height[height])
            add_block(start, current_tree_bottom, chosen_type, new_bottom, max_width, part = "right", check_overlap = "left")
        else:
            add_block(start, current_tree_bottom, chosen_type, new_bottom, max_width, part = "right", check_overlap = "no")
            chosen_type = choose_item(blocks_by_height[height])
            add_block(start, current_tree_bottom, chosen_type, new_bottom, max_width, part = "left", check_overlap = "right")
    
    else:
        # un seul bloc au milieu
        if prnt: print("center ", end="")
        add_block(start, current_tree_bottom, chosen_type, new_bottom, max_width, part = "center", check_overlap = "no")
        
    
    
    
# ajoute des blocs à droite ou à gauche du bloc supérieur "start" (selon "add_side") sur la nouvelle ligne
def add_side_blocks(current_tree_bottom, start, height, new_bottom, max_width, add_side, overlap_side):
    if add_side == "left":
        if prnt: print("\nB ", end=" ")
        i_upper_blocks = list(range(start-1, -1, -1))
    else:
        if prnt: print("\nC ", end="")
        i_upper_blocks = list(range(start+1, len(current_tree_bottom)))
        
    for i in i_upper_blocks:
        upper_block = current_tree_bottom[i]
        if add_side == "left": lower_block = new_bottom[0]
        else: lower_block = new_bottom[-1]
        
        if not new_check_support(upper_block, lower_block, "center"): # si le bloc du dessus est déjà supporté rien à faire
            
            if new_check_support(upper_block, lower_block, overlap_side):
                # un seul bloc à rajouter sous un bord
                if prnt: print(add_side + " edge ", end="")
                chosen_type = choose_item(blocks_by_height[height])
                add_block(i, current_tree_bottom, chosen_type, new_bottom, max_width, part = add_side, check_overlap = overlap_side)
                
            else:
                chosen_type = choose_item(blocks_by_height[height]) 
                
                if not(center_mandatory(chosen_type, upper_block, new_bottom, overlap_side)) \
                and (edges_mandatory(chosen_type, upper_block, new_bottom, overlap_side) or random() < .5):
                    # un bloc sous chaque bord
                    if prnt: print("edges ", end="")
                    add_block(i, current_tree_bottom, chosen_type, new_bottom, max_width, part = overlap_side, check_overlap = overlap_side)
                    chosen_type = choose_item(blocks_by_height[height])
                    add_block(i, current_tree_bottom, chosen_type, new_bottom, max_width, part = add_side, check_overlap = overlap_side)
                
                else:
                    # un seul bloc au milieu
                    if prnt: print("center ", end="")
                    add_block(i, current_tree_bottom, chosen_type, new_bottom, max_width, part = "center", check_overlap = overlap_side)
    



# ajoute une nouvelle ligne au bas de la structure
def add_new_row(current_tree_bottom, total_tree, max_width):
    start = randint(0, len(current_tree_bottom) - 1) # bloc de la ligne supérieure par lequel on commence 
    height = choose_item(probability_table_heights) # on choisit une hauteur pour toute la ligne
    new_bottom = []
    
    initialize_line(current_tree_bottom, start, height, new_bottom, max_width) # initialisation de la ligne
    add_side_blocks(current_tree_bottom, start, height, new_bottom, max_width, add_side = "left", overlap_side = "right") # ajout de blocs sur la gauche
    add_side_blocks(current_tree_bottom, start, height, new_bottom, max_width, add_side = "right", overlap_side = "left") # ajout de blocs sur la droite
                    
    total_tree.append(new_bottom)      # add new bottom row to the structure
    return total_tree, new_bottom      # return the new structure




# creates the peaks (first row) of the structure

def make_peaks(center_point):

    current_tree_bottom = []        # bottom blocks of structure
    number_peaks = randint(1,max_peaks)     # this is the number of peaks the structure will have
    height = choose_item(probability_table_heights)
    
    top_item = choose_item(blocks_by_height[height])
    current_tree_bottom.append([top_item,round(center_point,10)] )
    
    for _ in range(number_peaks - 1):
        height = choose_item(probability_table_heights) # UN BLOC DIFFERENT PAR PIC
        top_item = choose_item(blocks_by_height[height])
        distance_apart_extra = round(randint(min_peak_split,max_peak_split)/100.0,10)
        current_tree_bottom.append([top_item,round(current_tree_bottom[-1][1] + blocks[current_tree_bottom[-1][0]][0]/2.0 + blocks[str(top_item)][0]/2.0 + (distance_apart_extra),10), 0] )

    return current_tree_bottom




# replace la structure au centre de la zone qui lui est allouée
def adjust_center_point(complete_locations, center_point):
    leftest = min(complete_locations, key = (lambda item: item[1]))
    ajustement = - leftest[1] + center_point - (find_structure_width(complete_locations) / 2.0) + (blocks[leftest[0]][0] / 2.0)
    return [[item[0], round(item[1] + ajustement, 10), item[2]] for item in complete_locations]




# détermine les blocs qui supportent un bloc donné
def find_sons(total_tree, block, row):
    if row >= len(total_tree) - 1: return []
    return [potential for potential in total_tree[row+1] if not(right_edge(potential) < left_edge(block) or right_edge(block) < left_edge(potential))]
        
    
    
    
# détermine les blocs qui sont supportés par un bloc donné
def find_fathers(total_tree, block, row):
    if row <= 0: return []
    return [potential for potential in total_tree[row-1] if not(right_edge(potential) < left_edge(block) or right_edge(block) < left_edge(potential))]
        
            
            
         
# détermine le type de bloc de largeur minimale et de même hauteur que le bloc donné
def same_height_slim_type(block):
    h = round(blocks[block[0]][1], 1)
    if h == 0.2: # blocks 5 6 8 10 12
        return "5"
    if h == 0.4: # blocks 2 4 7
        return "7"
    if h <= 0.9: # blocks 1 3 9
        return "9"
    return block[0] # blocks 11 13




# dans le cadre d'une inversion PiU, détermine les coordonnées des points qui devront être soutenus une fois que
# le bloc donné aura été replacé à la ligne du dessous
def need_support(total_tree, block, row):
    sups = []
    fathers = find_fathers(total_tree, block, row)
    for father in fathers:
        
        # si le bloc supérieur dépasse sur la gauche, on ne le soutient qu'à droite
        if left_edge(father) + support_margin < left_edge(block):
            ideal = round(right_edge(father) - 0.11, 10)
            limite = round(left_edge(block) + 0.11, 10)
            sups.append(max(ideal, limite))
            
        # si le bloc supérieur dépasse sur la gauche, on ne le soutient qu'à droite
        elif right_edge(block) < right_edge(father) - support_margin:
            ideal = round(left_edge(father) + 0.11, 10)
            limite = round(right_edge(block) - 0.11, 10)
            sups.append(min(ideal, limite))
        
        # si le bloc supérieur est de largeur minimale, on ne le soutient qu'au milieu
        elif blocks[father[0]][0] == 0.22:
            sups.append(father[1])
            
        # sinon on le soutient sous chaque bord
        else:
            sups.append(round(left_edge(father) + 0.11, 10))
            sups.append(round(right_edge(father) - 0.11, 10))
            
    return sups





# dans le cadre d'une inversion PiU, vérifie que le bloc à descendre sera supporté
def bloc_supportable(total_tree, block, row):
    if row >= len(total_tree):
        return True
    left_support, right_support = False, False
    for lower in total_tree[row]:
        if left_edge(lower) - edge_margin < left_edge(block) < right_edge(lower) - support_margin:
            left_support = True
        if left_edge(lower) + support_margin < right_edge(block) < right_edge(lower) + edge_margin:
            right_support = True
    return left_support and right_support 

            
            
            
# réalise des inversions dans tout l'arbre, lorsque c'est possible
# on appelle fils d'un bloc B les blocs qui supportent B
# et pères de B les blocs qui sont supportés par B
def swap_heights(total_tree):
    nb_pics = len(total_tree[0])
    
    # on parcourt l'arbre de haut en bas
    for i, row in enumerate(total_tree):
        row = [i for i in row]
        for pivot in row:
            if pivot in total_tree[i]: # à vérifier en raison des inversions progressives
                sons = find_sons(total_tree, pivot, i)
                pivot_height = blocks[pivot[0]][1]
                pivot_width = blocks[pivot[0]][0]
                
                # si le bloc considéré n'a qu'un fils, on vérifie que les pères de ce fils n'ont pas d'autres fils
                # c'est la condition nécessaire pour réaliser l'inversion d'une forme en U à une forme en Pi
                if len(sons) == 1:
                    
                    son = sons[0]
                    fathers = find_fathers(total_tree, son, i+1)
                    flag = True
                    for father in fathers:
                        if len(find_sons(total_tree, father, i)) > 1 or blocks[father[0]][1] != pivot_height:
                            flag = False
                    if flag: 
                    
                        son_height = round(blocks[son[0]][1], 1)
                        son_width = blocks[son[0]][0]
                        
                        # fusion
                        if son_height == pivot_height:
                            if len(fathers) == 1 and son_height < 1:
                                pass # remplacer par des tiges aux emplacements des surpères et vérifier que les tiges sont center-supportées en-dessous
                                
                        # inversion de U vers Pi
                        elif random() < proba_inversion_UPi:
                            print(i, "UPi")
                            slim_type = same_height_slim_type(fathers[0])
                            
                            for father in fathers:
                                total_tree[i].remove(father)
                            total_tree[i+1].remove(son)
                            
                            total_tree[i].append(son)
                                   
                            # si on a seulement deux blocs de même largeur, on les inverse
                            if len(fathers) == 1 and son_width == pivot_width:
                                total_tree[i+1].append(pivot)
                              
                            # sinon on place un support sous chaque bord du bloc remonté
                            else:
                                total_tree[i+1].append([slim_type, left_edge(son) + .11, 0])
                                total_tree[i+1].append([slim_type, right_edge(son) - .11, 0])
                            
                   
                # si le bloc considéré a plusieurs fils, on vérifie que ces fils n'ont pas d'autres pères,
                # que le bloc considéré serait supporté s'il était descendu et que l'on n'a pas inversé tous les pics
                # ce sont les conditions nécessaires pour réaliser l'inversion d'une forme en Pi à une forme en U
                elif len(sons) > 1:
                    
                    flag = True
                    for son in sons:
                        if len(find_fathers(total_tree, son, i+1)) > 1:
                            flag = False
                    if flag and bloc_supportable(total_tree, pivot, i+2) and (i > 0 or nb_pics > 1)\
                    and random() < proba_inversion_PiU:
                        
                        print(i, "PiU")
                        #inversion de Pi vers U
                        slim_type = same_height_slim_type(sons[0])
                        sups = need_support(total_tree, pivot, i)
                        
                        total_tree[i].remove(pivot)
                        for son in sons:
                            total_tree[i+1].remove(son)
                            
                        total_tree[i+1].append(pivot)
                        for sup in sups:
                            total_tree[i].append([slim_type, sup, 0])
                            
                        nb_pics -= 1 # on conserve au moins un pic
                         
                        
                        
                    
                    


# recursively adds rows to base of strucutre until max_width or max_height is passed
# once this happens the last row added is removed and the structure is returned

def make_structure(absolute_ground, center_point, max_width, max_height):
    
    print("_"*20)
    
    total_tree = []                 # all blocks of structure (so far)

    # creates the first row (peaks) for the structure, ensuring that max_width restriction is satisfied
    current_tree_bottom = make_peaks(center_point)
    if max_width > 0.0:
        while find_structure_width(current_tree_bottom) > max_width:
            current_tree_bottom = make_peaks(center_point)

    total_tree.append(current_tree_bottom)

    # recursively add more rows of blocks to the level structure
    structure_width = find_structure_width(current_tree_bottom)
    structure_height = (blocks[str(current_tree_bottom[0][0])][1])/2
    limite = 0 # ON ESSAIE UN CERTAIN NOMBRE DE FOIS DE RESPECTER LA LARGEUR
    if max_height > 0.0 or max_width > 0.0:
        pre_total_tree = [current_tree_bottom]
        pre_current_tree_bottom = deepcopy(current_tree_bottom)
        while structure_height < max_height and limite < nb_essais_largeur:# and structure_width < max_width:
            total_tree, current_tree_bottom = add_new_row(current_tree_bottom, total_tree, max_width)
            complete_locations = []
            ground = absolute_ground
            for row in reversed(total_tree):
                for item in row:
                    complete_locations.append([item[0],item[1],round((((blocks[str(item[0])][1])/2)+ground),10)])
                ground = ground + (blocks[str(item[0])][1])
            structure_height = find_structure_height(complete_locations)
            structure_width = find_structure_width(complete_locations)
            if structure_height > max_height or structure_width > max_width:
                total_tree = deepcopy(pre_total_tree)
                current_tree_bottom = deepcopy(pre_current_tree_bottom)
                limite += 1
            else:
                pre_total_tree = deepcopy(total_tree)
                pre_current_tree_bottom = deepcopy(current_tree_bottom)
                limite = 0
                
    print() 
    for row in total_tree:
        print(row)
     
    # on crée des inversions
    swap_heights(total_tree)
        
    print("\n")      
    for row in total_tree:
        print(row)
                
    # make structure vertically correct (add y position to blocks)
    # HAUTEUR DEFINIE PAR RAPPORT AU FILS 
    complete_locations = []
    for i, row in enumerate(reversed(total_tree)):
        for j, item in enumerate(row):
            sons = find_sons(total_tree, item, len(total_tree) - 1 - i)
            if sons == []:
                height = round((((blocks[str(item[0])][1])/2)+absolute_ground),10)
            else:
                lowest_son = min(sons, key = (lambda son: son[-1]))
                height = round((((blocks[str(item[0])][1])/2) + ((blocks[str(lowest_son[0])][1])/2) + lowest_son[-1]),10)
            complete_locations.append([item[0], item[1], height])
            total_tree[len(total_tree) - 1 - i][j] = item + [height]
        
    # on replace la structure entière au centre de sa zone
    complete_locations = adjust_center_point(complete_locations, center_point)

    print("Width:",find_structure_width(complete_locations))
    print("Height:",find_structure_height(complete_locations))
    print("Block number:" , len(complete_locations))      # number blocks present in the structure


    # identify all possible pig positions on top of blocks (maximum 2 pigs per block, checks center before sides)
    possible_pig_positions = []
    for block in complete_locations:
        block_width = round(blocks[str(block[0])][0],10)
        block_height = round(blocks[str(block[0])][1],10)
        pig_width = pig_size[0]
        pig_height = pig_size[1]

        if blocks[str(block[0])][0] < pig_width:      # dont place block on edge if block too thin
            test_positions = [[round(block[1],10),round(block[2] + (pig_height/2) + (block_height/2),10)]]
        else:
            test_positions = [ [round(block[1],10),round(block[2] + (pig_height/2) + (block_height/2),10)],
                               [round(block[1] + (block_width/3),10),round(block[2] + (pig_height/2) + (block_height/2),10)],
                               [round(block[1] - (block_width/3),10),round(block[2] + (pig_height/2) + (block_height/2),10)]]     #check above centre of block
        for test_position in test_positions:
            valid_pig = True
            for i in complete_locations:
                if ( round((test_position[0] - pig_width/2),10) < round((i[1] + (blocks[str(i[0])][0])/2),10) and
                     round((test_position[0] + pig_width/2),10) > round((i[1] - (blocks[str(i[0])][0])/2),10) and
                     round((test_position[1] + pig_height/2),10) > round((i[2] - (blocks[str(i[0])][1])/2),10) and
                     round((test_position[1] - pig_height/2),10) < round((i[2] + (blocks[str(i[0])][1])/2),10)):
                    valid_pig = False
            if valid_pig == True:
                possible_pig_positions.append(test_position)


    #identify all possible pig positions on ground within structure
    left_bottom = total_tree[-1][0]
    right_bottom = total_tree[-1][-1]
    test_positions = []
    x_pos = left_bottom[1]

    while x_pos < right_bottom[1]:
        test_positions.append([round(x_pos,10),round(absolute_ground + (pig_height/2),10)])
        x_pos = x_pos + pig_precision

    for test_position in test_positions:
        valid_pig = True
        for i in complete_locations:
            if ( round((test_position[0] - pig_width/2),10) < round((i[1] + (blocks[str(i[0])][0])/2),10) and
                 round((test_position[0] + pig_width/2),10) > round((i[1] - (blocks[str(i[0])][0])/2),10) and
                 round((test_position[1] + pig_height/2),10) > round((i[2] - (blocks[str(i[0])][1])/2),10) and
                 round((test_position[1] - pig_height/2),10) < round((i[2] + (blocks[str(i[0])][1])/2),10)):
                valid_pig = False
        if valid_pig == True:
            possible_pig_positions.append(test_position)


    #randomly choose a pig position and remove those that overlap it, repeat until no more valid positions
    final_pig_positions = []
    while len(possible_pig_positions) > 0:
        pig_choice = possible_pig_positions.pop(randint(1,len(possible_pig_positions))-1)
        final_pig_positions.append(pig_choice)
        new_pig_positions = []
        for i in possible_pig_positions:
            if ( round((pig_choice[0] - pig_width/2),10) >= round((i[0] + pig_width/2),10) or
                 round((pig_choice[0] + pig_width/2),10) <= round((i[0] - pig_width/2),10) or
                 round((pig_choice[1] + pig_height/2),10) <= round((i[1] - pig_height/2),10) or
                 round((pig_choice[1] - pig_height/2),10) >= round((i[1] + pig_height/2),10)):
                new_pig_positions.append(i)
        possible_pig_positions = new_pig_positions

    print("Pig number:", len(final_pig_positions))     # number of pigs present in the structure
    print("")

    return complete_locations, final_pig_positions




# divide the available ground space between the chosen number of ground structures

def create_ground_structures():
    valid = False
    while valid == False:
        ground_divides = []
        if number_ground_structures > 0:
            ground_divides = [level_width_min, level_width_max]
        for i in range(number_ground_structures-1):
            ground_divides.insert(i+1,uniform(level_width_min, level_width_max))
        valid = True
        for j in range(len(ground_divides)-1):
            if (ground_divides[j+1] - ground_divides[j]) < min_ground_width:
                valid = False
                
    # determine the area available to each ground structure
    ground_positions = []
    ground_widths = []
    for j in range(len(ground_divides)-1):
        ground_positions.append(ground_divides[j]+((ground_divides[j+1] - ground_divides[j])/2))
        ground_widths.append(ground_divides[j+1] - ground_divides[j])

    print("number ground structures:", len(ground_positions))
    print("")

    # creates a ground structure for each defined area 
    complete_locations = []
    final_pig_positions = []
    for i in range(len(ground_positions)):
        max_width = ground_widths[i]
        max_height = ground_structure_height_limit
        center_point = ground_positions[i]
        complete_locations2, final_pig_positions2 = make_structure(absolute_ground, center_point, max_width, max_height)
        complete_locations = complete_locations + complete_locations2
        final_pig_positions = final_pig_positions + final_pig_positions2

    return len(ground_positions), complete_locations, final_pig_positions




# creates a set number of platforms within the level
# automatically reduced if space not found after set number of attempts

def create_platforms(number_platforms, complete_locations, final_pig_positions):

    platform_centers = []
    attempts = 0            # number of attempts so far to find space for platform
    final_platforms = []
    while len(final_platforms) < number_platforms:
        platform_width = randint(4,7)
        platform_position = [uniform(level_width_min+((platform_width*platform_size[0])/2.0), level_width_max-((platform_width*platform_size[0])/2.0)),
                             uniform(level_height_min, (level_height_max - minimum_height_gap))]
        temp_platform = []

        if platform_width == 1:
            temp_platform.append(platform_position)     

        if platform_width == 2:
            temp_platform.append([platform_position[0] - (platform_size[0]*0.5),platform_position[1]])
            temp_platform.append([platform_position[0] + (platform_size[0]*0.5),platform_position[1]])

        if platform_width == 3:
            temp_platform.append([platform_position[0] - (platform_size[0]),platform_position[1]])
            temp_platform.append(platform_position) 
            temp_platform.append([platform_position[0] + (platform_size[0]),platform_position[1]])

        if platform_width == 4:
            temp_platform.append([platform_position[0] - (platform_size[0]*1.5),platform_position[1]])
            temp_platform.append([platform_position[0] - (platform_size[0]*0.5),platform_position[1]])
            temp_platform.append([platform_position[0] + (platform_size[0]*0.5),platform_position[1]])
            temp_platform.append([platform_position[0] + (platform_size[0]*1.5),platform_position[1]])

        if platform_width == 5:
            temp_platform.append([platform_position[0] - (platform_size[0]*2.0),platform_position[1]])
            temp_platform.append([platform_position[0] - (platform_size[0]),platform_position[1]])
            temp_platform.append(platform_position) 
            temp_platform.append([platform_position[0] + (platform_size[0]),platform_position[1]])
            temp_platform.append([platform_position[0] + (platform_size[0]*2.0),platform_position[1]])

        if platform_width == 6:
            temp_platform.append([platform_position[0] - (platform_size[0]*2.5),platform_position[1]])
            temp_platform.append([platform_position[0] - (platform_size[0]*1.5),platform_position[1]])
            temp_platform.append([platform_position[0] - (platform_size[0]*0.5),platform_position[1]])
            temp_platform.append([platform_position[0] + (platform_size[0]*0.5),platform_position[1]])
            temp_platform.append([platform_position[0] + (platform_size[0]*1.5),platform_position[1]])
            temp_platform.append([platform_position[0] + (platform_size[0]*2.5),platform_position[1]])

        if platform_width == 7:
            temp_platform.append([platform_position[0] - (platform_size[0]*3.0),platform_position[1]])
            temp_platform.append([platform_position[0] - (platform_size[0]*2.0),platform_position[1]])
            temp_platform.append([platform_position[0] - (platform_size[0]),platform_position[1]])
            temp_platform.append(platform_position) 
            temp_platform.append([platform_position[0] + (platform_size[0]),platform_position[1]])
            temp_platform.append([platform_position[0] + (platform_size[0]*2.0),platform_position[1]])
            temp_platform.append([platform_position[0] + (platform_size[0]*3.0),platform_position[1]])
            
        overlap = False
        for platform in temp_platform:

            if (((platform[0]-(platform_size[0]/2)) < level_width_min) or ((platform[0]+(platform_size[0])/2) > level_width_max)):
                overlap = True
            
            for block in complete_locations:
                if ( round((platform[0] - platform_distance_buffer - platform_size[0]/2),10) <= round((block[1] + blocks[str(block[0])][0]/2),10) and
                     round((platform[0] + platform_distance_buffer + platform_size[0]/2),10) >= round((block[1] - blocks[str(block[0])][0]/2),10) and
                     round((platform[1] + platform_distance_buffer + platform_size[1]/2),10) >= round((block[2] - blocks[str(block[0])][1]/2),10) and
                     round((platform[1] - platform_distance_buffer - platform_size[1]/2),10) <= round((block[2] + blocks[str(block[0])][1]/2),10)):
                    overlap = True
                    
            for pig in final_pig_positions:
                if ( round((platform[0] - platform_distance_buffer - platform_size[0]/2),10) <= round((pig[0] + pig_size[0]/2),10) and
                     round((platform[0] + platform_distance_buffer + platform_size[0]/2),10) >= round((pig[0] - pig_size[0]/2),10) and
                     round((platform[1] + platform_distance_buffer + platform_size[1]/2),10) >= round((pig[1] - pig_size[1]/2),10) and
                     round((platform[1] - platform_distance_buffer - platform_size[1]/2),10) <= round((pig[1] + pig_size[1]/2),10)):
                    overlap = True

            for platform_set in final_platforms:
                for platform2 in platform_set:
                    if ( round((platform[0] - platform_distance_buffer - platform_size[0]/2),10) <= round((platform2[0] + platform_size[0]/2),10) and
                         round((platform[0] + platform_distance_buffer + platform_size[0]/2),10) >= round((platform2[0] - platform_size[0]/2),10) and
                         round((platform[1] + platform_distance_buffer + platform_size[1]/2),10) >= round((platform2[1] - platform_size[1]/2),10) and
                         round((platform[1] - platform_distance_buffer - platform_size[1]/2),10) <= round((platform2[1] + platform_size[1]/2),10)):
                        overlap = True

            for platform_set2 in final_platforms:
                for i in platform_set2:
                    if i[0]+platform_size[0] > platform[0] and i[0]-platform_size[0] < platform[0]:
                        if i[1]+minimum_height_gap > platform[1] and i[1]-minimum_height_gap < platform[1]:
                            overlap = True
                            
        if overlap == False:
            final_platforms.append(temp_platform)
            platform_centers.append(platform_position)

        attempts = attempts + 1
        if attempts > max_attempts:
            attempts = 0
            number_platforms = number_platforms - 1
            
    print("number platforms:", number_platforms)
    print("")

    return number_platforms, final_platforms, platform_centers




# create sutiable structures for each platform

def create_platform_structures(final_platforms, platform_centers, complete_locations, final_pig_positions):
    current_platform = 0
    for platform_set in final_platforms:
        platform_set_width = len(platform_set)*platform_size[0]

        above_blocks = []
        for platform_set2 in final_platforms:
            if platform_set2 != platform_set:
                for i in platform_set2:
                    if i[0]+platform_size[0] > platform_set[0][0] and i[0]-platform_size[0] < platform_set[-1][0] and i[1] > platform_set[0][1]:
                        above_blocks.append(i)

        min_above = level_height_max
        for j in above_blocks:
            if j[1] < min_above:
                min_above = j[1]

        center_point = platform_centers[current_platform][0]
        absolute_ground = platform_centers[current_platform][1] + (platform_size[1]/2)

        max_width = platform_set_width
        max_height = (min_above - absolute_ground)- pig_size[1] - platform_size[1]
        
        complete_locations2, final_pig_positions2 = make_structure(absolute_ground, center_point, max_width, max_height)
        complete_locations = complete_locations + complete_locations2
        final_pig_positions = final_pig_positions + final_pig_positions2

        current_platform = current_platform + 1

    return complete_locations, final_pig_positions




# remove random pigs until number equals the desired amount

def remove_unnecessary_pigs(number_pigs, final_pig_positions):
    removed_pigs = []
    while len(final_pig_positions) > number_pigs:
              remove_pos = randint(0,len(final_pig_positions)-1)
              removed_pigs.append(final_pig_positions[remove_pos])
              final_pig_positions.pop(remove_pos)
    return final_pig_positions, removed_pigs




# add pigs on the ground until number equals the desired amount

def add_necessary_pigs(number_pigs, final_pig_positions):
    while len(final_pig_positions) < number_pigs:
        test_position = [uniform(level_width_min, level_width_max),absolute_ground]
        pig_width = pig_size[0]
        pig_height = pig_size[1]
        valid_pig = True
        for i in complete_locations:
            if ( round((test_position[0] - pig_width/2),10) < round((i[1] + (blocks[str(i[0])][0])/2),10) and
                 round((test_position[0] + pig_width/2),10) > round((i[1] - (blocks[str(i[0])][0])/2),10) and
                 round((test_position[1] + pig_height/2),10) > round((i[2] - (blocks[str(i[0])][1])/2),10) and
                 round((test_position[1] - pig_height/2),10) < round((i[2] + (blocks[str(i[0])][1])/2),10)):
                valid_pig = False
        for i in final_pig_positions:
            if ( round((test_position[0] - pig_width/2),10) < round((i[0] + (pig_width/2)),10) and
                 round((test_position[0] + pig_width/2),10) > round((i[0] - (pig_width/2)),10) and
                 round((test_position[1] + pig_height/2),10) > round((i[1] - (pig_height/2)),10) and
                 round((test_position[1] - pig_height/2),10) < round((i[1] + (pig_height/2)),10)):
                valid_pig = False
        if valid_pig == True:
            final_pig_positions.append(test_position)
    return final_pig_positions




# choose the number of birds based on the number of pigs and structures present within level

def choose_number_birds(final_pig_positions,number_ground_structures,number_platforms):
    number_birds = int(ceil(len(final_pig_positions)/2))
    if (number_ground_structures + number_platforms) >= number_birds:
        number_birds = number_birds + 1
    number_birds = number_birds + 1         # adjust based on desired difficulty        
    return number_birds




# identify all possible triangleHole positions on top of blocks

def find_trihole_positions(complete_locations):
    possible_trihole_positions = []
    for block in complete_locations:
        block_width = round(blocks[str(block[0])][0],10)
        block_height = round(blocks[str(block[0])][1],10)
        trihole_width = additional_object_sizes['1'][0]
        trihole_height = additional_object_sizes['1'][1]

        # don't place block on edge if block too thin
        if blocks[str(block[0])][0] < trihole_width:
            test_positions = [ [round(block[1],10),round(block[2] + (trihole_height/2) + (block_height/2),10)]]
        else:
            test_positions = [ [round(block[1],10),round(block[2] + (trihole_height/2) + (block_height/2),10)],
                               [round(block[1] + (block_width/3),10),round(block[2] + (trihole_height/2) + (block_height/2),10)],
                               [round(block[1] - (block_width/3),10),round(block[2] + (trihole_height/2) + (block_height/2),10)] ]
        
        for test_position in test_positions:
            valid_position = True
            for i in complete_locations:
                if ( round((test_position[0] - trihole_width/2),10) < round((i[1] + (blocks[str(i[0])][0])/2),10) and
                     round((test_position[0] + trihole_width/2),10) > round((i[1] - (blocks[str(i[0])][0])/2),10) and
                     round((test_position[1] + trihole_height/2),10) > round((i[2] - (blocks[str(i[0])][1])/2),10) and
                     round((test_position[1] - trihole_height/2),10) < round((i[2] + (blocks[str(i[0])][1])/2),10)):
                    valid_position = False
            for j in final_pig_positions:
                if ( round((test_position[0] - trihole_width/2),10) < round((j[0] + (pig_size[0]/2)),10) and
                     round((test_position[0] + trihole_width/2),10) > round((j[0] - (pig_size[0]/2)),10) and
                     round((test_position[1] + trihole_height/2),10) > round((j[1] - (pig_size[1]/2)),10) and
                     round((test_position[1] - trihole_height/2),10) < round((j[1] + (pig_size[1]/2)),10)):
                    valid_position = False
            for j in final_TNT_positions:
                if ( round((test_position[0] - trihole_width/2),10) < round((j[0] + (pig_size[0]/2)),10) and
                     round((test_position[0] + trihole_width/2),10) > round((j[0] - (pig_size[0]/2)),10) and
                     round((test_position[1] + trihole_height/2),10) > round((j[1] - (pig_size[1]/2)),10) and
                     round((test_position[1] - trihole_height/2),10) < round((j[1] + (pig_size[1]/2)),10)):
                    valid_position = False
            for i in final_platforms:
                for j in i:
                    if ( round((test_position[0] - trihole_width/2),10) < round((j[0] + (platform_size[0]/2)),10) and
                         round((test_position[0] + trihole_width/2),10) > round((j[0] - (platform_size[0]/2)),10) and
                         round((test_position[1] + platform_distance_buffer + trihole_height/2),10) > round((j[1] - (platform_size[1]/2)),10) and
                         round((test_position[1] - platform_distance_buffer - trihole_height/2),10) < round((j[1] + (platform_size[1]/2)),10)):
                        valid_position = False
            if valid_position == True:
                possible_trihole_positions.append(test_position)
                        
    return possible_trihole_positions




# identify all possible triangle positions on top of blocks

def find_tri_positions(complete_locations):
    possible_tri_positions = []
    for block in complete_locations:
        block_width = round(blocks[str(block[0])][0],10)
        block_height = round(blocks[str(block[0])][1],10)
        tri_width = additional_object_sizes['2'][0]
        tri_height = additional_object_sizes['2'][1]
        
        # don't place block on edge if block too thin
        if blocks[str(block[0])][0] < tri_width:
            test_positions = [ [round(block[1],10),round(block[2] + (tri_height/2) + (block_height/2),10)]]
        else:
            test_positions = [ [round(block[1],10),round(block[2] + (tri_height/2) + (block_height/2),10)],
                               [round(block[1] + (block_width/3),10),round(block[2] + (tri_height/2) + (block_height/2),10)],
                               [round(block[1] - (block_width/3),10),round(block[2] + (tri_height/2) + (block_height/2),10)] ]
        
        for test_position in test_positions:
            valid_position = True
            for i in complete_locations:
                if ( round((test_position[0] - tri_width/2),10) < round((i[1] + (blocks[str(i[0])][0])/2),10) and
                     round((test_position[0] + tri_width/2),10) > round((i[1] - (blocks[str(i[0])][0])/2),10) and
                     round((test_position[1] + tri_height/2),10) > round((i[2] - (blocks[str(i[0])][1])/2),10) and
                     round((test_position[1] - tri_height/2),10) < round((i[2] + (blocks[str(i[0])][1])/2),10)):
                    valid_position = False
            for j in final_pig_positions:
                if ( round((test_position[0] - tri_width/2),10) < round((j[0] + (pig_size[0]/2)),10) and
                     round((test_position[0] + tri_width/2),10) > round((j[0] - (pig_size[0]/2)),10) and
                     round((test_position[1] + tri_height/2),10) > round((j[1] - (pig_size[1]/2)),10) and
                     round((test_position[1] - tri_height/2),10) < round((j[1] + (pig_size[1]/2)),10)):
                    valid_position = False
            for j in final_TNT_positions:
                if ( round((test_position[0] - tri_width/2),10) < round((j[0] + (pig_size[0]/2)),10) and
                     round((test_position[0] + tri_width/2),10) > round((j[0] - (pig_size[0]/2)),10) and
                     round((test_position[1] + tri_height/2),10) > round((j[1] - (pig_size[1]/2)),10) and
                     round((test_position[1] - tri_height/2),10) < round((j[1] + (pig_size[1]/2)),10)):
                    valid_position = False
            for i in final_platforms:
                for j in i:
                    if ( round((test_position[0] - tri_width/2),10) < round((j[0] + (platform_size[0]/2)),10) and
                         round((test_position[0] + tri_width/2),10) > round((j[0] - (platform_size[0]/2)),10) and
                         round((test_position[1] + platform_distance_buffer + tri_height/2),10) > round((j[1] - (platform_size[1]/2)),10) and
                         round((test_position[1] - platform_distance_buffer - tri_height/2),10) < round((j[1] + (platform_size[1]/2)),10)):
                        valid_position = False
                        
            if blocks[str(block[0])][0] < tri_width:      # as block not symmetrical need to check for support
                valid_position = False
            if valid_position == True:
                possible_tri_positions.append(test_position)

    return possible_tri_positions




# identify all possible circle positions on top of blocks (can only be placed in middle of block)

def find_cir_positions(complete_locations):
    possible_cir_positions = []
    for block in complete_locations:
        block_width = round(blocks[str(block[0])][0],10)
        block_height = round(blocks[str(block[0])][1],10)
        cir_width = additional_object_sizes['3'][0]
        cir_height = additional_object_sizes['3'][1]

        # only checks above block's center
        test_positions = [ [round(block[1],10),round(block[2] + (cir_height/2) + (block_height/2),10)]]
        
        for test_position in test_positions:
            valid_position = True
            for i in complete_locations:
                if ( round((test_position[0] - cir_width/2),10) < round((i[1] + (blocks[str(i[0])][0])/2),10) and
                     round((test_position[0] + cir_width/2),10) > round((i[1] - (blocks[str(i[0])][0])/2),10) and
                     round((test_position[1] + cir_height/2),10) > round((i[2] - (blocks[str(i[0])][1])/2),10) and
                     round((test_position[1] - cir_height/2),10) < round((i[2] + (blocks[str(i[0])][1])/2),10)):
                    valid_position = False
            for j in final_pig_positions:
                if ( round((test_position[0] - cir_width/2),10) < round((j[0] + (pig_size[0]/2)),10) and
                     round((test_position[0] + cir_width/2),10) > round((j[0] - (pig_size[0]/2)),10) and
                     round((test_position[1] + cir_height/2),10) > round((j[1] - (pig_size[1]/2)),10) and
                     round((test_position[1] - cir_height/2),10) < round((j[1] + (pig_size[1]/2)),10)):
                    valid_position = False
            for j in final_TNT_positions:
                if ( round((test_position[0] - cir_width/2),10) < round((j[0] + (pig_size[0]/2)),10) and
                     round((test_position[0] + cir_width/2),10) > round((j[0] - (pig_size[0]/2)),10) and
                     round((test_position[1] + cir_height/2),10) > round((j[1] - (pig_size[1]/2)),10) and
                     round((test_position[1] - cir_height/2),10) < round((j[1] + (pig_size[1]/2)),10)):
                    valid_position = False
            for i in final_platforms:
                for j in i:
                    if ( round((test_position[0] - cir_width/2),10) < round((j[0] + (platform_size[0]/2)),10) and
                         round((test_position[0] + cir_width/2),10) > round((j[0] - (platform_size[0]/2)),10) and
                         round((test_position[1] + platform_distance_buffer + cir_height/2),10) > round((j[1] - (platform_size[1]/2)),10) and
                         round((test_position[1] - platform_distance_buffer - cir_height/2),10) < round((j[1] + (platform_size[1]/2)),10)):
                        valid_position = False
            if valid_position == True:
                possible_cir_positions.append(test_position)

    return possible_cir_positions




# identify all possible circleSmall positions on top of blocks

def find_cirsmall_positions(complete_locations):
    possible_cirsmall_positions = []
    for block in complete_locations:
        block_width = round(blocks[str(block[0])][0],10)
        block_height = round(blocks[str(block[0])][1],10)
        cirsmall_width = additional_object_sizes['4'][0]
        cirsmall_height = additional_object_sizes['4'][1]

        # don't place block on edge if block too thin
        if blocks[str(block[0])][0] < cirsmall_width:
            test_positions = [ [round(block[1],10),round(block[2] + (cirsmall_height/2) + (block_height/2),10)]]
        else:
            test_positions = [ [round(block[1],10),round(block[2] + (cirsmall_height/2) + (block_height/2),10)],
                               [round(block[1] + (block_width/3),10),round(block[2] + (cirsmall_height/2) + (block_height/2),10)],
                               [round(block[1] - (block_width/3),10),round(block[2] + (cirsmall_height/2) + (block_height/2),10)] ]
        
        for test_position in test_positions:
            valid_position = True
            for i in complete_locations:
                if ( round((test_position[0] - cirsmall_width/2),10) < round((i[1] + (blocks[str(i[0])][0])/2),10) and
                     round((test_position[0] + cirsmall_width/2),10) > round((i[1] - (blocks[str(i[0])][0])/2),10) and
                     round((test_position[1] + cirsmall_height/2),10) > round((i[2] - (blocks[str(i[0])][1])/2),10) and
                     round((test_position[1] - cirsmall_height/2),10) < round((i[2] + (blocks[str(i[0])][1])/2),10)):
                    valid_position = False
            for j in final_pig_positions:
                if ( round((test_position[0] - cirsmall_width/2),10) < round((j[0] + (pig_size[0]/2)),10) and
                     round((test_position[0] + cirsmall_width/2),10) > round((j[0] - (pig_size[0]/2)),10) and
                     round((test_position[1] + cirsmall_height/2),10) > round((j[1] - (pig_size[1]/2)),10) and
                     round((test_position[1] - cirsmall_height/2),10) < round((j[1] + (pig_size[1]/2)),10)):
                    valid_position = False
            for j in final_TNT_positions:
                if ( round((test_position[0] - cirsmall_width/2),10) < round((j[0] + (pig_size[0]/2)),10) and
                     round((test_position[0] + cirsmall_width/2),10) > round((j[0] - (pig_size[0]/2)),10) and
                     round((test_position[1] + cirsmall_height/2),10) > round((j[1] - (pig_size[1]/2)),10) and
                     round((test_position[1] - cirsmall_height/2),10) < round((j[1] + (pig_size[1]/2)),10)):
                    valid_position = False
            for i in final_platforms:
                for j in i:
                    if ( round((test_position[0] - cirsmall_width/2),10) < round((j[0] + (platform_size[0]/2)),10) and
                         round((test_position[0] + cirsmall_width/2),10) > round((j[0] - (platform_size[0]/2)),10) and
                         round((test_position[1] + platform_distance_buffer + cirsmall_height/2),10) > round((j[1] - (platform_size[1]/2)),10) and
                         round((test_position[1] - platform_distance_buffer - cirsmall_height/2),10) < round((j[1] + (platform_size[1]/2)),10)):
                        valid_position = False
            if valid_position == True:
                possible_cirsmall_positions.append(test_position)

    return possible_cirsmall_positions




# finds possible positions for valid additional block types

def find_additional_block_positions(complete_locations):
    possible_trihole_positions = []
    possible_tri_positions = []
    possible_cir_positions = []
    possible_cirsmall_positions = []
    if trihole_allowed == True:
        possible_trihole_positions = find_trihole_positions(complete_locations)
    if tri_allowed == True:
        possible_tri_positions = find_tri_positions(complete_locations)
    if cir_allowed == True:
        possible_cir_positions = find_cir_positions(complete_locations)
    if cirsmall_allowed == True:
        possible_cirsmall_positions = find_cirsmall_positions(complete_locations)
    return possible_trihole_positions, possible_tri_positions, possible_cir_positions, possible_cirsmall_positions




# combine all possible additonal block positions into one set

def add_additional_blocks(possible_trihole_positions, possible_tri_positions, possible_cir_positions, possible_cirsmall_positions):
    all_other = []
    for i in possible_trihole_positions:
        all_other.append(['1',i[0],i[1]])
    for i in possible_tri_positions:
        all_other.append(['2',i[0],i[1]])
    for i in possible_cir_positions:
        all_other.append(['3',i[0],i[1]])
    for i in possible_cirsmall_positions:
        all_other.append(['4',i[0],i[1]])

    #randomly choose an additional block position and remove those that overlap it
    #repeat untill no more valid position

    selected_other = []
    while (len(all_other) > 0):
        chosen = all_other.pop(randint(0,len(all_other)-1))
        selected_other.append(chosen)
        new_all_other = []
        for i in all_other:
            if ( round((chosen[1] - (additional_object_sizes[chosen[0]][0]/2)),10) >= round((i[1] + (additional_object_sizes[i[0]][0]/2)),10) or
                 round((chosen[1] + (additional_object_sizes[chosen[0]][0]/2)),10) <= round((i[1] - (additional_object_sizes[i[0]][0]/2)),10) or
                 round((chosen[2] + (additional_object_sizes[chosen[0]][1]/2)),10) <= round((i[2] - (additional_object_sizes[i[0]][1]/2)),10) or
                 round((chosen[2] - (additional_object_sizes[chosen[0]][1]/2)),10) >= round((i[2] + (additional_object_sizes[i[0]][1]/2)),10)):
                new_all_other.append(i)
        all_other = new_all_other

    return selected_other




# remove restricted block types from the available selection

def remove_blocks(restricted_blocks):
    total_prob_removed = 0.0
    new_prob_table = deepcopy(probability_table_blocks)
    for block_name in restricted_blocks:
        for key,value in block_names.items():
            if value == block_name:
                total_prob_removed = total_prob_removed + probability_table_blocks[key]
                new_prob_table[key] = 0.0
    new_total = 1.0 - total_prob_removed
    for key, value in new_prob_table.items():
        new_prob_table[key] = value/new_total
    return new_prob_table




# add TNT blocks based on removed pig positions

def add_TNT(potential_positions):
    final_TNT_positions = []
    for position in potential_positions:
        if (uniform(0.0,1.0) < TNT_block_probability):
            final_TNT_positions.append(position)
    return final_TNT_positions




# write level out in desired xml format

def write_level_xml(complete_locations, selected_other, final_pig_positions, final_TNT_positions, final_platforms, number_birds, current_level, restricted_combinations):

    f = open(emplacement + "level-%s.xml" % current_level, "w")

    f.write('<?xml version="1.0" encoding="utf-16"?>\n')
    f.write('<Level width ="2">\n')
    f.write('<Camera x="0" y="2" minWidth="20" maxWidth="30">\n')
    f.write('<Birds>\n')
    for i in range(number_birds):   # bird type is chosen using probability table
        f.write('<Bird type="%s"/>\n' % bird_names[str(choose_item(bird_probabilities))])
    f.write('</Birds>\n')
    f.write('<Slingshot x="-8" y="-2.5">\n')
    f.write('<GameObjects>\n')

    for i in complete_locations:
        material = materials[randint(0,len(materials)-1)]       # material is chosen randomly
        while [material,block_names[str(i[0])]] in restricted_combinations:     # if material if not allowed for block type then pick again
            material = materials[randint(0,len(materials)-1)]
        rotation = 0
        if (i[0] in ("3","7","9","11","13")):
            rotation = 90
        f.write('<Block type="%s" material="%s" x="%s" y="%s" rotation="%s" />\n' % (block_names[str(i[0])], material, str(i[1]), str(i[2]), str(rotation)))

    for i in selected_other:
        material = materials[randint(0,len(materials)-1)]       # material is chosen randomly
        while [material,additional_objects[str(i[0])]] in restricted_combinations:      # if material if not allowed for block type then pick again
            material = materials[randint(0,len(materials)-1)]
        if i[0] == '2':
            facing = randint(0,1)
            f.write('<Block type="%s" material="%s" x="%s" y="%s" rotation="%s" />\n' % (additional_objects[i[0]], material, str(i[1]), str(i[2]), str(facing*90.0)))
        else:
            f.write('<Block type="%s" material="%s" x="%s" y="%s" rotation="0" />\n' % (additional_objects[i[0]], material, str(i[1]), str(i[2])))

    for i in final_pig_positions:
        f.write('<Pig type="BasicSmall" material="" x="%s" y="%s" rotation="0" />\n' % (str(i[0]),str(i[1])))

    for i in final_platforms:
        for j in i:
            f.write('<Platform type="Platform" material="" x="%s" y="%s" />\n' % (str(j[0]),str(j[1])))

    for i in final_TNT_positions:
        f.write('<TNT type="" material="" x="%s" y="%s" rotation="0" />\n' % (str(i[0]),str(i[1])))
        
    f.write('</GameObjects>\n')
    f.write('</Level>\n')

    f.close()




# generate levels using input parameters

backup_probability_table_blocks = deepcopy(probability_table_blocks)
backup_materials = deepcopy(materials)

FILE = open("parameters.txt", 'r')
checker = FILE.readline()
finished_levels = 0
while (checker != ""):
    if checker == "\n":
        checker = FILE.readline()
    else:
        number_levels = int(deepcopy(checker))              # the number of levels to generate
        restricted_combinations = FILE.readline().split(',')      # block type and material combination that are banned from the level
        for i in range(len(restricted_combinations)):
            restricted_combinations[i] = restricted_combinations[i].split()     # if all materials are baned for a block type then do not use that block type
        pig_range = FILE.readline().split(',')
        time_limit = int(FILE.readline())                   # time limit to create the levels, shouldn't be an issue for most generators (approximately an hour for 10 levels)
        checker = FILE.readline()

        restricted_blocks = []                              # block types that cannot be used with any materials
        for key,value in block_names.items():
            completely_restricted = True
            for material in materials:
                if [material,value] not in restricted_combinations:
                    completely_restricted = False
            if completely_restricted == True:
                restricted_blocks.append(value)

        probability_table_blocks = deepcopy(backup_probability_table_blocks)
        trihole_allowed = False
        tri_allowed = False
        cir_allowed = False
        cirsmall_allowed = False
        TNT_allowed = False

        probability_table_blocks = remove_blocks(restricted_blocks)     # remove restricted block types from the structure generation process
        if "TriangleHole" in restricted_blocks:
            trihole_allowed = False
        if "Triangle" in restricted_blocks:
            tri_allowed = False
        if "Circle" in restricted_blocks:
            cir_allowed = False
        if "CircleSmall" in restricted_blocks:
            cirsmall_allowed = False

        for current_level in range(number_levels):

            number_ground_structures = randint(2,3) #randint(2,4)                     # number of ground structures
            number_platforms = randint(1,2) #randint(1,3)                             # number of platforms (reduced automatically if not enough space)
            number_pigs = randint(int(pig_range[0]),int(pig_range[1]))  # number of pigs (if set too large then can cause program to infinitely loop)

            if (current_level+finished_levels+4) < 10:
                level_name = "0"+str(current_level+finished_levels+4)
            else:
                level_name = str(current_level+finished_levels+4)
            
            number_ground_structures, complete_locations, final_pig_positions = create_ground_structures()
            number_platforms, final_platforms, platform_centers = create_platforms(number_platforms,complete_locations,final_pig_positions)
            complete_locations, final_pig_positions = create_platform_structures(final_platforms, platform_centers, complete_locations, final_pig_positions)
            final_pig_positions, removed_pigs = remove_unnecessary_pigs(number_pigs, final_pig_positions)
            final_pig_positions = add_necessary_pigs(number_pigs, final_pig_positions)
            final_TNT_positions = add_TNT(removed_pigs)
            number_birds = choose_number_birds(final_pig_positions,number_ground_structures,number_platforms)
            possible_trihole_positions, possible_tri_positions, possible_cir_positions, possible_cirsmall_positions = find_additional_block_positions(complete_locations)
            selected_other = add_additional_blocks(possible_trihole_positions, possible_tri_positions, possible_cir_positions, possible_cirsmall_positions)
            
            #final_pig_positions = []
            final_TNT_positions = []
            
            write_level_xml(complete_locations, selected_other, final_pig_positions, final_TNT_positions, final_platforms, number_birds, level_name, restricted_combinations)
        finished_levels = finished_levels + number_levels



    
