from csp import Constraint, Variable


class TableConstraint(Constraint):
    '''General type of constraint that can be used to implement any type of
       constraint. But might require a lot of space to do so.

       A table constraint explicitly stores the set of satisfying
       tuples of assignments.'''

    def __init__(self, name, scope, satisfyingAssignments):
        '''Init by specifying a name and a set variables the constraint is over.
           Along with a list of satisfying assignments.
           Each satisfying assignment is itself a list, of length equal to
           the number of variables in the constraints scope.
           If sa is a single satisfying assignment, e.g, sa=satisfyingAssignments[0]
           then sa[i] is the value that will be assigned to the variable scope[i].


           Example, say you want to specify a constraint alldiff(A,B,C,D) for
           three variables A, B, C each with domain [1,2,3,4]
           Then you would create this constraint using the call
           c = TableConstraint('example', [A,B,C,D],
                               [[1, 2, 3, 4], [1, 2, 4, 3], [1, 3, 2, 4],
                                [1, 3, 4, 2], [1, 4, 2, 3], [1, 4, 3, 2],
                                [2, 1, 3, 4], [2, 1, 4, 3], [2, 3, 1, 4],
                                [2, 3, 4, 1], [2, 4, 1, 3], [2, 4, 3, 1],
                                [3, 1, 2, 4], [3, 1, 4, 2], [3, 2, 1, 4],
                                [3, 2, 4, 1], [3, 4, 1, 2], [3, 4, 2, 1],
                                [4, 1, 2, 3], [4, 1, 3, 2], [4, 2, 1, 3],
                                [4, 2, 3, 1], [4, 3, 1, 2], [4, 3, 2, 1]])
          as these are the only assignments to A,B,C respectively that
          satisfy alldiff(A,B,C,D)
        '''

        Constraint.__init__(self,name, scope)
        self._name = "TableCnstr_" + name
        self.satAssignments = satisfyingAssignments

    def check(self):
        '''check if current variable assignments are in the satisfying set'''
        assignments = []
        for v in self.scope():
            if v.isAssigned():
                assignments.append(v.getValue())
            else:
                return True
        return assignments in self.satAssignments

    def hasSupport(self, var,val):
        '''check if var=val has an extension to an assignment of all variables in
           constraint's scope that satisfies the constraint. Important only to
           examine values in the variable's current domain as possible extensions'''
        if var not in self.scope():
            return True   #var=val has support on any constraint it does not participate in
        # index of the variable in the scope
        vindex = self.scope().index(var)
        found = False

        for assignment in self.satAssignments:
            if assignment[vindex] != val:
                continue   #this assignment can't work it doesn't make var=val
            found = True   #Otherwise it has potential. Assume found until shown otherwise
            for i, v in enumerate(self.scope()):
                if i != vindex and not v.inCurDomain(assignment[i]):
                    found = False  #Bummer...this assignment didn't work it assigns
                    break          #a value to v that is not in v's curDomain
                                   #note we skip checking if val in in var's curDomain
            if found:     #if found still true the assigment worked. We can stop
                break
        return found     #either way found has the right truth value

def findvals(remainingVars, assignment, finalTestfn, partialTestfn=lambda x: True):
    '''Helper function for finding an assignment to the variables of a constraint
       that together with var=val satisfy the constraint. That is, this
       function looks for a supporting tuple.

       findvals uses recursion to build up a complete assignment, one value
       from every variable's current domain, along with var=val.

       It tries all ways of constructing such an assignment (using
       a recursive depth-first search).

       If partialTestfn is supplied, it will use this function to test
       all partial assignments---if the function returns False
       it will terminate trying to grow that assignment.

       It will test all full assignments to "allVars" using finalTestfn
       returning once it finds a full assignment that passes this test.

       returns True if it finds a suitable full assignment, False if none
       exist. (yes we are using an algorithm that is exactly like backtracking!)'''

    # print "==>findvars([",
    # for v in remainingVars: print v.name(), " ",
    # print "], [",
    # for x,y in assignment: print "({}={}) ".format(x.name(),y),
    # print ""

    #sort the variables call the internal version with the variables sorted
    remainingVars.sort(reverse=True, key=lambda v: v.curDomainSize())
    return findvals_(remainingVars, assignment, finalTestfn, partialTestfn)

def findvals_(remainingVars, assignment, finalTestfn, partialTestfn):
    '''findvals_ internal function with remainingVars sorted by the size of
       their current domain'''
    if len(remainingVars) == 0:
        return finalTestfn(assignment)
    var = remainingVars.pop()
    for val in var.curDomain():
        assignment.append((var, val))
        if partialTestfn(assignment):
            if findvals_(remainingVars, assignment, finalTestfn, partialTestfn):
                return True
        assignment.pop()   #(var,val) didn't work since we didn't do the return
    remainingVars.append(var)
    return False


class NValuesConstraint(Constraint):
    '''NValues constraint over a set of variables.  Among the variables in
       the constraint's scope the number that have been assigned
       values in the set 'required_values' is in the range
       [lower_bound, upper_bound] (lower_bound <= #of variables
       assigned 'required_value' <= upper_bound)

       For example, if we have 4 variables V1, V2, V3, V4, each with
       domain [1, 2, 3, 4], then the call
       NValuesConstraint('test_nvalues', [V1, V2, V3, V4], [1,4], 2,
       3) will only be satisfied by assignments such that at least 2
       the V1, V2, V3, V4 are assigned the value 1 or 4, and at most 3
       of them have been assigned the value 1 or 4.

    '''

    def __init__(self, name, scope, required_values, lower_bound, upper_bound):
        Constraint.__init__(self,name, scope)
        self._name = "NValues_" + name
        self._required = required_values
        self._lb = lower_bound
        self._ub = upper_bound

    def check(self):
        assignments = []
        for v in self.scope():
            if v.isAssigned():
                assignments.append(v.getValue())
            else:
                return True
        rv_count = 0

        #print "Checking {} with assignments = {}".format(self.name(), assignments)

        for v in assignments:
            if v in self._required:
                rv_count += 1

        #print "rv_count = {} test = {}".format(rv_count, self._lb <= rv_count and self._ub >= rv_count)


        return self._lb <= rv_count and self._ub >= rv_count

    def hasSupport(self, var, val):
        '''check if var=val has an extension to an assignment of the
           other variable in the constraint that satisfies the constraint

           HINT: check the implementation of AllDiffConstraint.hasSupport
                 a similar approach is applicable here (but of course
                 there are other ways as well)
        '''
        if var not in self.scope():
            return True   #var=val has support on any constraint it does not participate in

        #define the test functions for findvals
        def valsOK(l):
            '''tests a list of assignments which are pairs (var,val)
               to see if they can satisfy this sum constraint'''
            rv_count = 0
            vals = [val for (var, val) in l]
            for v in vals:
                if v in self._required:
                    rv_count += 1
            least = rv_count + self.arity() - len(vals)
            most =  rv_count
            return self._lb <= least and self._ub >= most
        varsToAssign = self.scope()
        varsToAssign.remove(var)
        x = findvals(varsToAssign, [(var, val)], valsOK, valsOK)
        return x


class IfAllThenOneConstraint(Constraint):
    '''if each variable in left_side equals each value in left_values
    then one of the variables in right side has to equal one of the values in right_values.
    hasSupport tested only, check() untested.'''
    def __init__(self, name, left_side, right_side, left_values, right_values):
        Constraint.__init__(self,name, left_side+right_side)
        self._name = "IfAllThenOne_" + name
        self._ls = left_side
        self._rs = right_side
        self._lv = left_values
        self._rv = right_values


def get_orientation(orientation):
    """
    Get the direction the ship would be oriented in
    """
    dir = (0,0)
    # oriented towards top
    if orientation[0] == 1:
        dir = (-1, 0)
    # oriented towards bottom
    if orientation[1] == 1:
        dir = (1, 0)
    # oriented towards right
    if orientation[2] == 1:
        dir = (0, 1)
    # oriented towards left
    if orientation[3] == 1:
        dir = (0, -1)
    return dir


class ShipCountConstraint:
    """
    Constraints on the number of each type of ship on the board.
    Check whether the board has the correct number of each type of ship.
    """

    def __init__(self, ship_count, size):
        # a list of the total number of each type of ship on the board
        self.ship_count = ship_count
        # size of the board
        self.size = size

    def check_val(self, var, board):
        """
        Check whether the variable given is a ship part
        """
        # if the cell has a ship part
        if board[var] == 1:
            return True
        else:
            return False

    def check_carrier(self, i, j, board, orient):
        """
        Check whether the cell (i, j) is part of a 1 x 5 ship
        """
        check_vars = []
        # vertical: check value of i
        if orient[0] == 1 or orient[0] == -1:
            if (i + (orient[0] * 4)) > self.size - 1 \
                    or (i + (orient[0] * 4)) < 1 \
                    or board[-1 - ((i + (orient[0] * 4)) * self.size + j)] == 0:
                return []
            # if cell 5 above or below i is in the board and not water
            else:
                # check 5 cells to the direction to see if they are all ship parts
                # use variable names to check
                check_vars.append(-1 - (i * self.size + j))
                check_vars.append(-1 - ((i + (orient[0] * 1)) * self.size + j))
                check_vars.append(-1 - ((i + (orient[0] * 2)) * self.size + j))
                check_vars.append(-1 - ((i + (orient[0] * 3)) * self.size + j))
                check_vars.append(-1 - ((i + (orient[0] * 4)) * self.size + j))

        # horizontal: check value of j
        else:
            if (j + (orient[1] * 4)) > self.size - 1 or (j + (orient[1] * 4)) < 1 or board[-1 - (i * self.size + j + (orient[1] * 4))] == 0:
                return []
            # if cell 5 right or left of j is in the board and not water
            else:
                # check all 5 cells to the direction to see if they are all ship parts
                # use variable names to check
                check_vars.append(-1 - (i * self.size + j))
                check_vars.append(-1 - (i * self.size + j + (orient[1] * 1)))
                check_vars.append(-1 - (i * self.size + j + (orient[1] * 2)))
                check_vars.append(-1 - (i * self.size + j + (orient[1] * 3)))
                check_vars.append(-1 - (i * self.size + j + (orient[1] * 4)))

        # if all consecutive cells are ship parts, return list of checked variable names
        if self.check_val(check_vars[0], board) and self.check_val(check_vars[1], board) and self.check_val(check_vars[2], board) and self.check_val(check_vars[3], board) and self.check_val(check_vars[4], board):
            return check_vars
        else:
            return []

    def check_battleship(self, i, j, board, orient):
        """
        Check whether the cell is part of a 1 x 4 ship
        """
        check_vals = []
        # vertical: check value of i
        if orient[0] == 1 or orient[0] == -1:
            if (i + (orient[0] * 3)) > self.size - 1 or (i + (orient[0] * 3)) < 1 or board[-1 - ((i + (orient[0] * 3)) * self.size + j)] == 0:
                return []
            # if cell 4 above or below i is in the board and not water
            else:
                # check all 4 cells to the direction to see if they are all ship parts
                # use variable names to check
                check_vals.append(-1 - (i * self.size + j))
                check_vals.append(-1 - ((i + (orient[0] * 1)) * self.size + j))
                check_vals.append(-1 - ((i + (orient[0] * 2)) * self.size + j))
                check_vals.append(-1 - ((i + (orient[0] * 3)) * self.size + j))

        # horizontal: check value of j
        else:
            if (j + (orient[1] * 3)) > self.size - 1 or (j + (orient[1] * 3)) < 1 or board[-1 - (i * self.size + j + (orient[1] * 3))] == 0:
                return []
            # if cell 4 right or left of j is in the board and not water
            else:
                # check all 4 cells to the direction to see if they are all ship parts
                # use variable names to check
                check_vals.append(-1 - (i * self.size + j))
                check_vals.append(-1 - (i * self.size + j + (orient[1] * 1)))
                check_vals.append(-1 - (i * self.size + j + (orient[1] * 2)))
                check_vals.append(-1 - (i * self.size + j + (orient[1] * 3)))

        # if all consecutive cells are ship parts, return list of checked variables names
        if self.check_val(check_vals[0], board) and self.check_val(check_vals[1], board) and self.check_val(check_vals[2], board) and self.check_val(check_vals[3], board):
            return check_vals
        else:
            return []

    def check_cruiser(self, i, j, board, orient):
        """
        Check whether the cell is part of a 1 x 3 cruiser ship
        """
        check_vals = []
        # vertical: check value of i
        if orient[0] == 1 or orient[0] == -1:
            if (i + (orient[0] * 2)) > self.size - 1 or (i + (orient[0] * 2)) < 1 or board[-1 - ((i + (orient[0] * 2)) * self.size + j)] == 0:
                return []
            # if cell 3 above or below i is in the board and not water
            else:
                # check all 3 cells to the direction to see if they are all ship parts
                # use variable names to check
                check_vals.append(-1 - (i * self.size + j))
                check_vals.append(-1 - ((i + (orient[0] * 1)) * self.size + j))
                check_vals.append(-1 - ((i + (orient[0] * 2)) * self.size + j))

        # horizontal: check value of j
        else:
            if (j + (orient[1] * 2)) > self.size - 1 or (j + (orient[1] * 2)) < 1 or board[-1 - (i * self.size + j + (orient[1] * 2))] == 0:
                return []
            # if cell 3 right or left of j is in the board and not water
            else:
                # check all 3 cells to the direction to see if they are all ship parts
                check_vals.append(-1 - (i * self.size + j))
                check_vals.append(-1 - (i * self.size + j + (orient[1] * 1)))
                check_vals.append(-1 - (i * self.size + j + (orient[1] * 2)))

        # if all consecutive cells are ship parts, return list of checked variable names
        if self.check_val(check_vals[0], board) and self.check_val(check_vals[1], board) and self.check_val(check_vals[2], board):
            return check_vals
        else:
            return []

    def check_destroyer(self, i, j, board, orient):
        """
        Check whether the cell is part of a 1 x 2 destroyer ship
        """
        check_vals = []
        # vertical: check value of i
        if orient[0] == 1 or orient[0] == -1:
            # if cell 2 above or below i is in the board and not water
            if (i + (orient[0] * 1)) > self.size - 1 or (i + (orient[0] * 1)) < 1 or board[-1 - ((i + (orient[0] * 1)) * self.size + j)] == 0:
                return []
            else:
                # check all 2 cells to the direction to see if they are all ship parts
                # use variable names to check
                check_vals.append(-1 - (i * self.size + j))
                check_vals.append(-1 - ((i + (orient[0] * 1)) * self.size + j))

        # horizontal: check value of j
        else:
            if (j + (orient[1] * 1)) > self.size - 1 or (j + (orient[1] * 1)) < 1 or board[-1 - (i * self.size + j + (orient[1] * 1))] == 0:
                return []
            # if cell 2 right or left of j is in the board and not water
            else:
                # check all 2 cells to the direction to see if they are all ship parts
                # use variable names to check
                check_vals.append(-1 - (i * self.size + j))
                check_vals.append(-1 - (i * self.size + j + (orient[1] * 1)))

        # if all consecutive cells are ship parts, return list of checked variable names
        if self.check_val(check_vals[0], board) and self.check_val(check_vals[1], board):
            return check_vals
        else:
            return []

    def get_type(self, i, j, board):
        """
        Get the type of ship the current cell is part of
        Return the list of variables that are part of the ship,
        the type number, and orientation of the ship
        """
        # up, down, right, left
        orientation = [1, 1, 1, 1]

        # find the possible orientation
        # check up
        if i - 1 < 1 or board[-1 - ((i-1) * self.size + j)] == 0:
            orientation[0] = 0
        # check down
        if i + 1 > self.size - 1 or board[-1 - ((i+1) * self.size + j)] == 0:
            orientation[1] = 0
        # check right
        if j + 1 > self.size - 1 or board[-1 - (i * self.size + (j+1))] == 0:
            orientation[2] = 0
        # check left
        if j - 1 < 1 or board[-1 - (i * self.size + (j-1))] == 0:
            orientation[3] = 0

        # get the orientation of the ship
        dir = get_orientation(orientation)
        # if there is no direction the ship is facing, 1 x 1 submarine
        if dir == (0, 0):
            return [-1 - (i * self.size + j)], 0, dir
        # check if the ship are any of the other types
        else:
            # check if carrier
            type = self.check_carrier(i, j, board, dir)
            if type:
                return type, 4, dir
            # check if battleship
            type = self.check_battleship(i, j, board, dir)
            if type:
                return type, 3, dir
            # check if cruiser
            type = self.check_cruiser(i, j, board, dir)
            if type:
                return type, 2, dir
            # check if destroyer
            type = self.check_destroyer(i, j, board, dir)
            if type:
                return type, 1, dir
        return [], -1

    def check(self, solution):
        """
        Check whether the given solution is a valid board
        given the number of ships the board should have
        """
        # dictionary containing values of each variable
        board = {}
        # contain variable names that have already been checked
        checked = []
        # keep track of the number of each type of ships
        # submarine, destroyer, cruiser, battleship, carrier
        count = [0, 0, 0, 0, 0]

        # store possible solution and the direction each ship is oriented
        # 0 = submarine, 1 = destroyer, 2 = cruiser, 3 = battleship, 4 = carrier
        pos_sol = {0: [], 1: [], 2: [], 3: [], 4: []}
        sol_dir = {0: [], 1: [], 2: [], 3: [], 4: []}

        # store the value of each variable in dictionary
        for var, val in solution:
            board[int(var.name())] = val

        # iterate through the board
        for i in range(1, self.size - 1):
            for j in range(1, self.size - 1):
                # if the cell contains a part of the ship that has not been checked yet
                if board[-1 - (i * self.size + j)] == 1 and -1 - (i * self.size + j) not in checked:
                    # check the neighbouring cells to find the type of ship
                    checked_vars, type, dir = self.get_type(i, j, board)
                    # store the variable names that have already been checked
                    checked.extend(checked_vars)
                    # increase the number of ships of type
                    count[type] += 1
                    # store the top left variable name of the ship
                    pos_sol[type].append(checked_vars[0])
                    # store the orientation of the ship
                    sol_dir[type].append(dir)

        # if the number of each ship matches the given amount,
        # return true, the top left variable names for each ship, orientation of each ship
        if count[0] == self.ship_count[0] and count[1] == self.ship_count[1] and count[2] == self.ship_count[2] and count[3] == self.ship_count[3] and count[4] == self.ship_count[4]:
            return True, pos_sol, sol_dir
        else:
            return False, pos_sol, sol_dir

