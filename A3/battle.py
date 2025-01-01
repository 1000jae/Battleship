from csp import Constraint, Variable, CSP
from constraints import *
from backtracking import bt_search
import sys
import argparse
import time

# # ./S/</>/v/^/M symbols for ship parts
ship_types = ['S', '<', '>', 'v', '^', 'M']


def get_coords(i, j, length, dir, solution):
    """
    Change the cells with the corresponding ship_type in solution
    length: the size of the ship
    dir: the orientation of the ship
    solution: representation of board in list
    """
    # ship oriented towards top
    if dir[0] == -1:
        # cell (i, j) = 'v'
        solution[i][j] = ship_types[3]
        # cell (i - (length - 1), j) = '^'
        solution[i + (dir[0] * (length - 1))][j] = ship_types[4]
        # other in between parts = 'M'
        for l in range(1, length - 1):
            solution[i + (dir[0] * l)][j] = ship_types[5]

    # ship oriented towards bottom
    elif dir[0] == 1:
        # cell (i, j) = '^'
        solution[i][j] = ship_types[4]
        # # cell (i + (length - 1), j) = 'v'
        solution[i + (dir[0] * (length - 1))][j] = ship_types[3]
        # other in between parts = 'M'
        for l in range(1, length - 1):
            solution[i + (dir[0] * l)][j] = ship_types[5]

    # ship oriented towards the right
    elif dir[1] == 1:
        # cell (i, j) = '<'
        solution[i][j] = ship_types[1]
        # cell (i, j + (length - 1)) = '>'
        solution[i][j + (dir[1] * (length - 1))] = ship_types[2]
        # other in between parts = 'M'
        for l in range(1, length - 1):
            solution[i][j + (dir[1] * l)] = ship_types[5]

    # ship oriented towards the left
    else:
        # cell (i, j) = '>'
        solution[i][j] = ship_types[2]
        # cell (i, j - (length - 1)) = '<'
        solution[i][j + (dir[1] * (length - 1))] = ship_types[1]
        # other in between parts = 'M'
        for l in range(1, length - 1):
            solution[i][j + (dir[1] * l)] = ship_types[5]


def print_sol(s, size, coord, orient):
    """
    Print the solution board
    s: solution
    size: the size of board
    coord: dictionary of each type of ship showing
    the top left cell each ship of that type starts at
    orient: the direction in each ship is oriented towards
    """
    # keep track of the number of each type of ship that has been looked at
    # index for dir
    index = [0, 0, 0, 0, 0]
    # dictionary to keep variable, value pairs
    s_ = {}
    # list representing the solution board
    sol = []

    for (var, val) in s:
        s_[int(var.name())] = val

    # create array to store the board
    for i in range(size):
        row = []
        for j in range(size):
            row.append('.')
        sol.append(row)

    # go through each cell on board
    for i in range(1, size - 1):
        for j in range(1, size - 1):
            # if 1x1 submarine
            if -1 - (i * size + j) in coord[0]:
                # cell (i, j) = 'S'
                sol[i][j] = ship_types[0]

            # if 1x2 destroyer
            elif -1 - (i * size + j) in coord[1]:
                # get orientation of ship
                dir = orient[1][index[1]]
                # update sol
                get_coords(i, j, 2, dir, sol)
                # increase count of destroyer ships
                index[1] += 1

            # if 1x3 cruiser
            elif -1 - (i * size + j) in coord[2]:
                # get orientation of ship
                dir = orient[2][index[2]]
                # update sol
                get_coords(i, j, 3, dir, sol)
                # increase count of cruiser ships
                index[2] += 1

            # if 1x4 battleship
            elif -1 - (i * size + j) in coord[3]:
                # get orientation of ship
                dir = orient[3][index[3]]
                # update sol
                get_coords(i, j, 4, dir, sol)
                # increase count of battleship ships
                index[3] += 1

            # if 1x5 carrier
            elif -1 - (i * size + j) in coord[4]:
                # get orientation of ship
                dir = orient[4][index[4]]
                # update sol
                get_coords(i, j, 5, dir, sol)
                # increase count of carrier ships
                index[4] += 1

    # iterate through list representation and print each cell of the board
    for i in range(1, size - 1):
        for j in range(1, size - 1):
            print(sol[i][j], end="")
        print('')


# parse board and ships info
parser = argparse.ArgumentParser()
parser.add_argument(
    "--inputfile",
    type=str,
    required=True,
    help="The input file that contains the puzzles."
)
parser.add_argument(
    "--outputfile",
    type=str,
    required=True,
    help="The output file that contains the solution."
)
args = parser.parse_args()
file = open(args.inputfile, 'r')

# t0 = time.time()

b = file.read()
b2 = b.split()
size = len(b2[0])
size = size + 2
b3 = []
b3 += ['0' + b2[0] + '0']
b3 += ['0' + b2[1] + '0']
b3 += [b2[2] + ('0' if len(b2[2]) == 3 else '')]
b3 += ['0' * size]
for i in range(3, len(b2)):
    b3 += ['0' + b2[i] + '0']
b3 += ['0' * size]
board = "\n".join(b3)

varlist = []
varn = {}
conslist = []

# make 1/0 variables
for i in range(0, size):
    for j in range(0, size):
        v = None
        if i == 0 or i == size - 1 or j == 0 or j == size - 1:
            v = Variable(str(-1 - (i * size + j)), [0])
        else:
            v = Variable(str(-1 - (i * size + j)), [0, 1])
        varlist.append(v)
        varn[str(-1 - (i * size + j))] = v

# make 1/0 variables match board info
ii = 0
for i in board.split()[3:]:
    jj = 0
    for j in i:
        # if not padding or water
        if j != '0' and j != '.':
            conslist.append(TableConstraint('boolean_match',
                                            [varn[str(-1 - (ii * size + jj))]],
                                            [[1]]))
            # add constraints for given ship parts in input
            # 'S'
            if j == ship_types[0]:
                # constraint to make sure that only 'S' is a ship part
                scope = [varn[str(-1 - (ii * size + jj))],
                         varn[str(-1 - ((ii + 1) * size + jj))],
                         varn[str(-1 - ((ii - 1) * size + jj))],
                         varn[str(-1 - (ii * size + (jj - 1)))],
                         varn[str(-1 - (ii * size + (jj + 1)))]
                         ]
                conslist.append(NValuesConstraint('S', scope, [1], 1, 1))
                # constraint to make sure that all cells surrounding 'S' is water
                scope = [varn[str(-1 - (ii * size + jj))],
                         varn[str(-1 - ((ii + 1) * size + jj))],
                         varn[str(-1 - ((ii - 1) * size + jj))],
                         varn[str(-1 - (ii * size + (jj - 1)))],
                         varn[str(-1 - (ii * size + (jj + 1)))]
                         ]
                conslist.append(NValuesConstraint('S', scope, [0], 4, 4))

            # '<'
            if j == ship_types[1]:
                # constraint to make sure that cell on right of '<' is a ship part
                scope = [varn[str(-1 - (ii * size + jj))],
                         varn[str(-1 - (ii * size + (jj + 1)))],
                         ]
                conslist.append(NValuesConstraint('<', scope, [1], 2, 2))
                # constraint to make sure that cell on left of '<' is water
                scope = [varn[str(-1 - (ii * size + jj))],
                         varn[str(-1 - (ii * size + (jj - 1)))],
                         ]
                conslist.append(NValuesConstraint('<', scope, [0], 1, 1))

            # '>'
            elif j == ship_types[2]:
                # constraint to make sure that cell on left of '>' is a ship part
                scope = [varn[str(-1 - (ii * size + jj))],
                         varn[str(-1 - (ii * size + (jj - 1)))],
                         ]
                conslist.append(NValuesConstraint('>', scope, [1], 2, 2))
                # constraint to make sure that cell on right of '>' is water
                scope = [varn[str(-1 - (ii * size + jj))],
                         varn[str(-1 - (ii * size + (jj + 1)))],
                         ]
                conslist.append(NValuesConstraint('>', scope, [0], 1, 1))

            # 'v'
            elif j == ship_types[3]:
                # constraint to make sure that cell above 'v' is a ship part
                scope = [varn[str(-1 - (ii * size + jj))],
                         varn[str(-1 - ((ii - 1) * size + jj))]
                         ]
                conslist.append(NValuesConstraint('^', scope, [1], 2, 2))
                # constraint to make sure that cell below 'v' is water
                scope = [varn[str(-1 - (ii * size + jj))],
                         varn[str(-1 - ((ii + 1) * size + jj))]
                         ]
                conslist.append(NValuesConstraint('^', scope, [0], 1, 1))

            # '^'
            elif j == ship_types[4]:
                # constraint to make sure that cell below of '^' is a ship part
                scope = [varn[str(-1 - (ii * size + jj))],
                         varn[str(-1 - ((ii + 1) * size + jj))]
                         ]
                conslist.append(NValuesConstraint('v', scope, [1], 2, 2))
                # constraint to make sure that cell above of '^' is water
                scope = [varn[str(-1 - (ii * size + jj))],
                         varn[str(-1 - ((ii - 1) * size + jj))]
                         ]
                conslist.append(NValuesConstraint('v', scope, [0], 1, 1))
            # 'M'
            elif j == ship_types[5]:
                # constraint to make sure either top and bottom or left and right
                # are ship parts from 'M'
                scope = [varn[str(-1 - (ii * size + jj))],
                         varn[str(-1 - ((ii + 1) * size + jj))],
                         varn[str(-1 - ((ii - 1) * size + jj))],
                         varn[str(-1 - (ii * size + (jj - 1)))],
                         varn[str(-1 - (ii * size + (jj + 1)))]
                         ]
                conslist.append(NValuesConstraint('M', scope, [1], 3, 3))
                # constraint to make sure either top and bottom or left and right
                # of 'M' are water
                scope = [varn[str(-1 - (ii * size + jj))],
                         varn[str(-1 - ((ii + 1) * size + jj))],
                         varn[str(-1 - ((ii - 1) * size + jj))],
                         varn[str(-1 - (ii * size + (jj - 1)))],
                         varn[str(-1 - (ii * size + (jj + 1)))]
                         ]
                conslist.append(NValuesConstraint('M', scope, [0], 2, 2))

        # if the cell is water
        elif j == '.':
            conslist.append(TableConstraint('boolean_match',
                                            [varn[str(-1 - (ii * size + jj))]],
                                            [[0]]))
        jj += 1
    ii += 1

# row and column constraints on 1/0 variables
row_constraint = []
for i in board.split()[0]:
    row_constraint += [int(i)]

for row in range(0, size):
    conslist.append(NValuesConstraint('row',
                                      [varn[str(-1 - (row * size + col))] for
                                       col in range(0, size)], [1],
                                      row_constraint[row], row_constraint[row]))

col_constraint = []
for i in board.split()[1]:
    col_constraint += [int(i)]

for col in range(0, size):
    conslist.append(NValuesConstraint('col',
                                      [varn[str(-1 - (col + row * size))] for
                                       row in range(0, size)], [1],
                                      col_constraint[col], col_constraint[col]))

# diagonal constraints on 1/0 variables
for i in range(1, size - 1):
    for j in range(1, size - 1):
        for k in range(9):
            conslist.append(NValuesConstraint('diag',
                                              [varn[str(-1 - (i * size + j))],
                                               varn[str(-1 - ((i - 1) * size + (
                                                       j - 1)))]], [1], 0,
                                              1))
            conslist.append(NValuesConstraint('diag',
                                              [varn[str(-1 - (i * size + j))],
                                               varn[str(-1 - ((i - 1) * size + (
                                                       j + 1)))]], [1], 0,
                                              1))

# ship count constraint
ship_count = []
# iterate through the line containing the number of each type of ships
for i in board.split()[2]:
    # save it as an integer value
    ship_count += [int(i)]
# initialize ship count constraint
ship_count = ShipCountConstraint(ship_count, size)

# find all solutions and check which one has right ship #'s
csp = CSP('battleship', varlist, conslist, ship_count)
solutions, num_nodes = bt_search('GAC', csp, 'mrv', False, False)
sys.stdout = open(args.outputfile, 'w')
# print the solutions
for i in range(len(solutions)):
    print_sol(solutions[i][0], size, solutions[i][1], solutions[i][2])

# t1 = time.time()
# print(f"{t1 - t0} seconds")
