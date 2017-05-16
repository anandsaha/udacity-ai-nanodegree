assignments = []


rows = 'ABCDEFGHI'
cols = '123456789' 

def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [a+b for a in A for b in B]

all_boxes = [r+c for r in rows for c in cols]
row_units = [ [r+c for c in cols] for r in rows]    
col_units = [ [r+c for r in rows] for c in cols]
squ_units = [ cross(r, c) for r in ['ABC', 'DEF', 'GHI'] for c in ['123', '456', '789']]

diag_units= []
l1 = []
l2 = []
for i in range(9):
    l1.append(rows[i] + cols[i])
    l2.append(rows[i] + cols[8-i])

diag_units.append(l1)
diag_units.append(l2)

unitlist = row_units + col_units + squ_units + diag_units
units = dict((s, [u for u in unitlist if s in u]) for s in all_boxes)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in all_boxes)

def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """

    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values


def naked_twins_helper(values, units):
    for unit in units:
        count = {}
        for x in unit:
            if values[x] in count:
                count[values[x]] += 1
            else:
                count[values[x]] = 1

        for num in count:
            if len(num) > 1 and len(num) == count[num]: 
                for x in unit:
                    if values[x] != num:
                        for c in num:
                            assign_value(values, x, values[x].replace(c, ''))
    return values


def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """

    # Find all instances of naked twins
    # Eliminate the naked twins as possibilities for their peers

    # Eliminate naked twins from each of row, col and square units
    values = naked_twins_helper(values, row_units)
    values = naked_twins_helper(values, col_units)
    values = naked_twins_helper(values, squ_units)

    return values
 

def grid_values(values):
    """
    Convert values into a dict of {square: char} with '123456789' for empties.
    Args:
        values(string) - A grid in string form.
    Returns:
        A values in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    values = dict((rows[r] + cols[c], values[r * 9 + c])  for c in range(9) for r in range(9))

    for v in values:
        if values[v] == '.':
            values[v] = '123456789'

    return values


def display(values):
    """
    Display the values as a 2-D values.
    Args:
        values(dict): The sudoku in dictionary form
    """
    for r in rows:
        for c in cols:
            print('{0: <10}'.format(values[r + c]), end='')
        print('')


def eliminate(values):
    singles = []
    for b in values:
        if len(values[b]) == 1:
            singles.append(b)
                
    for s in singles:
        for p in peers[s]:
            #print("Eliminating {0} from {1} at location {2}".format(values[s], grid[p], p))
            values[p] = values[p].replace(values[s], '')
    return values


def only_choice(values):
    for unit in unitlist:
        for box in unit:
            v = values[box]
            if len(v) > 1:
                for d in '123456789':
                    if d in v:
                        update = True
                        for box1 in unit:
                            if box != box1 and d in values[box1]:
                                update = False
                        if update:
                            #print("Assigning {0} to {1}".format(d, values[box]))
                            values[box] = d
                                                
    return values
                                                    

def reduce_puzzle(values):
    stagnent = False
    while not stagnent:
        #print('.')
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        values = eliminate(values)
        values = only_choice(values)
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        
        if solved_values_before == solved_values_after:
            stagnent = True
            
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values


def search(values):
    values = reduce_puzzle(values)

    if values == False:
        return False
    
    index = None
    for b in values:
        if len(values[b]) > 1:
            index = b
            break
            
    if index is None:
        return values
    
    elements = values[index]
    
    for e in elements:
        values_copy = values.copy()
        values_copy[index] = e
        attempt = search(values_copy)
        if attempt:
            return attempt
        

def validate(grid):
    for unit in unitlist:
        s = set()
        for u in unit:
            if grid[u] in list('123456789'):
                s.add(grid[u])
        if len(s) != 9:
            return False
        
    return True


def solve(values):
    """
    Find the solution to a Sudoku values.
    Args:
        values(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku values. False if no solution exists.
    """
    values = grid_values(values)
    values = search(values)
    return values


if __name__ == '__main__':
#diag_sudoku_values = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
#diag_sudoku_values = '9.1....8.8.5.7..4.2.4....6...7......5..............83.3..6......9................' 
    diag_sudoku_values = '1..2......7..............7.8..5.1.2...43.85...6.4.2..9.3..............4......3..8'
    values = solve(diag_sudoku_values)
    display(values)

    print(validate(values))
    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
