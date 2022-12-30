from visualiser import Visualiser
from model import CellPatch
from model import ObstaclePatch
from model import Cell
import random
from random import shuffle, choices, choice
import numpy as np
from statistics import mean



age_deaths = 0
division_deaths = 0
poison_deaths = 0
total_cells = 0


def cell_life(cell:Cell,age_limit,division_limit):
    '''Uses tick function to age cells. if the age_limit or division_limit is exceeded, the cell will die.'''
    cell.tick()
    if cell.age() > age_limit:
        cell.died_by_age_limit()
        global age_deaths
        age_deaths += 1
    elif cell.divisions() > division_limit:
        cell.died_by_division_limit()
        global division_deaths
        division_deaths += 1
    else:
        if cell.patch().toxicity() - cell.resistance() >= random.randint(0,10):
            cell.died_by_poisoning()
            global poison_deaths
            poison_deaths += 1

def check_for_cells(patch_list):
    '''Iterates over the entire patch list for cells. Returns true if there is a cell on the patch.'''
    for patch in patch_list:
        if patch.has_cell() == True:
            return True
    return False

def create_board(row:int, col:int, grid:np.array):
    patch_list = []
    for i in range(row):
        for j in range(col):
            if grid[i][j] == '%':
                obstacle_patch = ObstaclePatch(i, j)
                patch_list.append(obstacle_patch)
            else:
                toxic = int(grid[i][j])
                cell_patch = CellPatch(i, j,toxic)
                patch_list.append(cell_patch)
    return patch_list

def free_neighbors(patches, patch, row:int, col:int):
    '''Checks neighboring patches of each cell for vacant patches. Returns false with a list of vacant patches, if there are, true if not.'''
    neighbor_patches = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]
    (x,y) = patch.row(), patch.col()
    if_vacants = []
    if_not = [(x,y)]
    for (z,w) in neighbor_patches:
        row_pos = z + x
        col_pos = w + y
        (a,b) = (row_pos%row,col_pos%col)
        if_not.append((a,b))
        if not isinstance(patches[a][b], ObstaclePatch):
            if not patches[a][b].has_cell():
                if_vacants.append((a,b))
    return (False,if_vacants) if len(if_vacants)>0 else (True,if_vacants)

def rand(prob):
    result = choices([1,0],[prob,1-prob],k=1)[0]
    if result == 1:
        return True
    else:
        return False

def spread_cells(patches,patch,row,col,divisions_probability,cd):
    '''Function for cell division. If the square is overcrowded a random cell from that square dies,
    if not, the random function runs and a cell divides if it is succesful and has no cooldown period.'''
    (x,y) = (patch.row(),patch.col())
    overcrowd, poss = free_neighbors(patches, patch, row, col)
    if (divisions_probability - patch.cell().resistance()/20) <= random.random() and poss:
        if rand(divisions_probability):
            x_r, y_r = choice(poss)
            cell = patch.cell()
            if cell._last_division >= cd:
                cell.divide(patches[x_r][y_r])
                global total_cells
                total_cells += 1
                #print(cell.generation())

def initial_pop(row:int,col:int,intial_population:int,grid):
    init_pop = initial_population * [1] + (row * col - initial_population)*[0]
    shuffle(init_pop)
    board = create_board(row,col,grid)
    cellpatches = list(filter(lambda x: isinstance(x, CellPatch), board))
    for patches in cellpatches:
        if init_pop[0] == 1:
            Cell(patches,random.randrange(10))
        init_pop = init_pop[1:]
    return board, cellpatches

def highest_generation(gen_list):
    counter = 0
    if len(gen_list) != 0:
        gen = gen_list[0]

        for i in gen_list:
            current = gen_list.count(i)
            if current > counter:
                counter = current
                gen = i        
        return gen


if __name__ == '__main__':
    grid = np.genfromtxt('grid_3.txt', dtype='str')
    row = len(grid)
    col = len(grid[0])
    initial_population = 2
    age_limit = 10
    division_limit = 7
    division_prob = 0.6
    division_cd = 1
    time_limit = 100
    tick = 0
    total_gens = 0
    gen_list = []
    res_list = []
    gen_res_list = []
    cell_list = []
    div_list = []
    init_pop,cell_patches = initial_pop(row,col,initial_population,grid)
    vis = Visualiser(init_pop,row,col)
    
    while check_for_cells(cell_patches) and tick<time_limit:
        for patch in cell_patches:
            if patch.has_cell():
                cell = patch.cell()
                cell_life(cell,age_limit,division_limit)
        for patch in cell_patches:
            if patch.has_cell():
                spread_cells(vis._patches,patch,row,col,division_prob,division_cd)
        for patch in cell_patches:
            if patch.has_cell():
                cell = patch.cell()
                if cell not in cell_list:
                    cell_list.append(cell)
                    div_list.append(cell.divisions())
                    gen_list.append(cell.generation())
                    res_list.append(cell.resistance())
                    gen_res_list.append((cell.generation(),cell.resistance()))
                if total_gens <= cell.generation():
                    total_gens = cell.generation() + 1 #Gen 0 still counts as 1

        vis.update()
        tick += 1
    
    highest_gen = highest_generation(gen_list)
            
    total_deaths = age_deaths + division_deaths + poison_deaths

    print(gen_list)
    print(len(gen_list))
    print(res_list)
    print(len(res_list))

    print(cell_list)
    print(len(cell_list))

    '''Test for list with generation + resistance '''
    print(gen_res_list)
    print(len(gen_res_list))
    
    '''Test for average resistance '''
    if len(res_list)!=0:
        res_avg = mean(res_list)
        print("Average resistance:", round(res_avg,2))

    '''New avg test'''
    if len(gen_res_list)!=0:
        res_sum = 0
        for cells in gen_res_list:
            cell_res = cells[1]
            res_sum += cell_res
        avg_test = res_sum/len(gen_res_list)
        print("Test avg", round(avg_test,2))

    print(div_list)

    
    print("")
    print("--- SIM STATS ---")
    print("")
    print("Time in ticks:", tick)
    print("")
    print("Number of generations:", total_gens)
    print("")
    print("Generation with most cells:", highest_gen)
    print("")
    print("Total number of cells:", total_cells + initial_population)
    print("")
    print("Deaths by age:", age_deaths)
    print("")
    print("Deaths by division:", division_deaths)
    print("")
    print("Deaths by poisoning:", poison_deaths)
    print("")
    print("Total deaths:", total_deaths)
        
