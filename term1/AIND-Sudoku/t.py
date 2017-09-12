assignments = []

# Utility code

def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [a+b for a in A for b in B]


rows = 'ABCDEFGHI'
cols = '123456789' 

all_boxes = [r+c for r in rows for c in cols]
row_units = [ [r+c for c in cols] for r in rows]    
col_units = [ [r+c for r in rows] for c in cols]
squ_units = [ cross(r, c) for r in ['ABC', 'DEF', 'GHI'] for c in ['123', '456', '789']]

# Add additional constraint of the leading diagonals. These will get added to unitlist, 
# units and peers data structures.
diag_units= []
l1 = []
l2 = []
for i in range(9):
    l1.append(rows[i] + cols[i])
    l2.append(rows[i] + cols[8-i])

diag_units.append(l1)
diag_units.append(l2)

unitlist = row_units + col_units + squ_units # + diag_units
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
    """Helper function, given a set of units (row wise, col wise or squares),
       applies the naked twin approach to the individual unit.

       First we scan the boxes in the unit for repeats of same sequence of digits.
       If the length of the digit sequence matches the number of occurances (e.g.
       '27' should repeat twice, '539' should repeat thrice), then we visit all
       the boxes in the unit other than the ones containing this digit sequence,
       and remove the digits.
       
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}
        units(list of lists): list of units
        
    Returns:
        The modified 'values' data structure after application of naked twins strategy.
    """
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
                            values[x] = values[x].replace(c, '')
    return values


def naked_twins(values):
    """Eliminate values using the naked twins strategy. Uses helper function.

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
    """We inspect boxes with one element. We know that that element will not repeat 
    in any of the peers boxes. So we eliminate that element from all peer boxes.
    
    Args:
        values(dict): The sudoku in dictionary form
    Returns:
        values(dict): The sudoku in dictionary form after applying elimination strategy
    """
    singles = []
    for b in values:
        if len(values[b]) == 1:
            singles.append(b)
                
    for s in singles:
        for p in peers[s]:
            #print("Eliminating {0} from {1} at location {2}".format(values[s], grid[p], p))
            values[p] = values[p].replace(values[s], '')
    display(values)
    print('------------------')
    return values


def only_choice(values):
    """In this we look at boxes with multiple options, and inspect if there is one 
    out of the multiple options which only that box can be assigned to. If so - we do 
    the assignment.
    
    Args:
        values(dict): The sudoku in dictionary form
    Returns:
        values(dict): The sudoku in dictionary form after applying only-choice strategy
    """
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
    """This is the Constraint Propagation step where we try to eliminate as many scenarios
    as possible by holding to the constraints on each box. We keep applying elimination and 
    only-choice strategy till there is no further reduction in scenarios.
    
    Args:
        values(dict): The sudoku in dictionary form
    Returns:
        values(dict): The sudoku in dictionary form after applying constraint propagation
    """
    stagnent = False
    while not stagnent:
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
    """This is a recursive function applying the Search method. For a given grid, we first apply 
    constraint propagation to reduce the search space. Then we apply search in DFS pattern to try 
    out various combinations of the possible digits.
    
    Args:
        values(dict): The sudoku in dictionary form
    Returns:
        values(dict): The sudoku in dictionary form after applying constraint propagation and search
    """
    values = reduce_puzzle(values)

    if values == False:
        return False

    if all(len(values[s]) == 1 for s in all_boxes): 
        # Ok we have a grid will all single digits. Is it a valid grid?
        if validate(values):
            return values
        else:
            return False

    n,index = min((len(values[s]), s) for s in all_boxes if len(values[s]) > 1)

    if index is None:
        return False # Should not happen

    elements = values[index]
    
    for e in elements:
        values_copy = values.copy()
        values_copy[index] = e
        attempt = search(values_copy)
        if attempt:
            return attempt

    return False


def validate(grid):
    """Helper function to validate a given grid (in dict form)
    
    Args:
        grid(dict): The solved sudoku
        
    Returns:
        True if all rules are met. False otherwise.
    """
    if grid == False:
        return False 

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

# Note: The hard problems are normal sudoku problems, not diagonal.
hard_problems = ['4.....8.5.3..........7......2.....6.....8.4......1.......6.3.7.5..2.....1.4......', 
    '52...6.........7.13...........4..8..6......5...........418.........3..2...87.....', 
    '6.....8.3.4.7.................5.4.7.3..2.....1.6.......2.....5.....8.6......1....', 
    '48.3............71.2.......7.5....6....2..8.............1.76...3.....4......5....', 
    '....14....3....2...7..........9...3.6.1.............8.2.....1.4....5.6.....7.8...', 
    '......52..8.4......3...9...5.1...6..2..7........3.....6...1..........7.4.......3.', 
    '6.2.5.........3.4..........43...8....1....2........7..5..27...........81...6.....', 
    '.524.........7.1..............8.2...3.....6...9.5.....1.6.3...........897........', 
    '6.2.5.........4.3..........43...8....1....2........7..5..27...........81...6.....', 
    '.923.........8.1...........1.7.4...........658.........6.5.2...4.....7.....9.....', 
    '6..3.2....5.....1..........7.26............543.........8.15........4.2........7..', 
    '.6.5.1.9.1...9..539....7....4.8...7.......5.8.817.5.3.....5.2............76..8...', 
    '..5...987.4..5...1..7......2...48....9.1.....6..2.....3..6..2.......9.7.......5..', 
    '3.6.7...........518.........1.4.5...7.....6.....2......2.....4.....8.3.....5.....', 
    '1.....3.8.7.4..............2.3.1...........958.........5.6...7.....8.2...4.......', 
    '6..3.2....4.....1..........7.26............543.........8.15........4.2........7..', 
    '....3..9....2....1.5.9..............1.2.8.4.6.8.5...2..75......4.1..6..3.....4.6.', 
    '45.....3....8.1....9...........5..9.2..7.....8.........1..4..........7.2...6..8..', 
    '.237....68...6.59.9.....7......4.97.3.7.96..2.........5..47.........2....8.......', 
    '..84...3....3.....9....157479...8........7..514.....2...9.6...2.5....4......9..56', 
    '.98.1....2......6.............3.2.5..84.........6.........4.8.93..5...........1..', 
    '..247..58..............1.4.....2...9528.9.4....9...1.........3.3....75..685..2...', 
    '4.....8.5.3..........7......2.....6.....5.4......1.......6.3.7.5..2.....1.9......', 
    '.2.3......63.....58.......15....9.3....7........1....8.879..26......6.7...6..7..4', 
    '1.....7.9.4...72..8.........7..1..6.3.......5.6..4..2.........8..53...7.7.2....46', 
    '4.....3.....8.2......7........1...8734.......6........5...6........1.4...82......', 
    '.......71.2.8........4.3...7...6..5....2..3..9........6...7.....8....4......5....', 
    '6..3.2....4.....8..........7.26............543.........8.15........8.2........7..', 
    '.47.8...1............6..7..6....357......5....1..6....28..4.....9.1...4.....2.69.', 
    '......8.17..2........5.6......7...5..1....3...8.......5......2..4..8....6...3....', 
    '38.6.......9.......2..3.51......5....3..1..6....4......17.5..8.......9.......7.32', 
    '...5...........5.697.....2...48.2...25.1...3..8..3.........4.7..13.5..9..2...31..', 
    '.2.......3.5.62..9.68...3...5..........64.8.2..47..9....3.....1.....6...17.43....', 
    '.8..4....3......1........2...5...4.69..1..8..2...........3.9....6....5.....2.....', 
    '..8.9.1...6.5...2......6....3.1.7.5.........9..4...3...5....2...7...3.8.2..7....4', 
    '4.....5.8.3..........7......2.....6.....5.8......1.......6.3.7.5..2.....1.8......', 
    '1.....3.8.6.4..............2.3.1...........958.........5.6...7.....8.2...4.......', 
    '1....6.8..64..........4...7....9.6...7.4..5..5...7.1...5....32.3....8...4........', 
    '249.6...3.3....2..8.......5.....6......2......1..4.82..9.5..7....4.....1.7...3...', 
    '...8....9.873...4.6..7.......85..97...........43..75.......3....3...145.4....2..1', 
    '...5.1....9....8...6.......4.1..........7..9........3.8.....1.5...2..4.....36....', 
    '......8.16..2........7.5......6...2..1....3...8.......2......7..3..8....5...4....', 
    '.476...5.8.3.....2.....9......8.5..6...1.....6.24......78...51...6....4..9...4..7', 
    '.....7.95.....1...86..2.....2..73..85......6...3..49..3.5...41724................', 
    '.4.5.....8...9..3..76.2.....146..........9..7.....36....1..4.5..6......3..71..2..', 
    '.834.........7..5...........4.1.8..........27...3.....2.6.5....5.....8........1..', 
    '..9.....3.....9...7.....5.6..65..4.....3......28......3..75.6..6...........12.3.8', 
    '.26.39......6....19.....7.......4..9.5....2....85.....3..2..9..4....762.........4', 
    '2.3.8....8..7...........1...6.5.7...4......3....1............82.5....6...1.......', 
    '6..3.2....1.....5..........7.26............843.........8.15........8.2........7..', 
    '1.....9...64..1.7..7..4.......3.....3.89..5....7....2.....6.7.9.....4.1....129.3.', 
    '.........9......84.623...5....6...453...1...6...9...7....1.....4.5..2....3.8....9', 
    '.2....5938..5..46.94..6...8..2.3.....6..8.73.7..2.........4.38..7....6..........5', 
    '9.4..5...25.6..1..31......8.7...9...4..26......147....7.......2...3..8.6.4.....9.', 
    '...52.....9...3..4......7...1.....4..8..453..6...1...87.2........8....32.4..8..1.', 
    '53..2.9...24.3..5...9..........1.827...7.........981.............64....91.2.5.43.', 
    '1....786...7..8.1.8..2....9........24...1......9..5...6.8..........5.9.......93.4', 
    '....5...11......7..6.....8......4.....9.1.3.....596.2..8..62..7..7......3.5.7.2..', 
    '.47.2....8....1....3....9.2.....5...6..81..5.....4.....7....3.4...9...1.4..27.8..', 
    '......94.....9...53....5.7..8.4..1..463...........7.8.8..7.....7......28.5.26....', 
    '.2......6....41.....78....1......7....37.....6..412....1..74..5..8.5..7......39..', 
    '1.....3.8.6.4..............2.3.1...........758.........7.5...6.....8.2...4.......', 
    '2....1.9..1..3.7..9..8...2.......85..6.4.........7...3.2.3...6....5.....1.9...2.5', 
    '..7..8.....6.2.3...3......9.1..5..6.....1.....7.9....2........4.83..4...26....51.', 
    '...36....85.......9.4..8........68.........17..9..45...1.5...6.4....9..2.....3...', 
    '34.6.......7.......2..8.57......5....7..1..2....4......36.2..1.......9.......7.82', 
    '......4.18..2........6.7......8...6..4....3...1.......6......2..5..1....7...3....', 
    '.4..5..67...1...4....2.....1..8..3........2...6...........4..5.3.....8..2........', 
    '.......4...2..4..1.7..5..9...3..7....4..6....6..1..8...2....1..85.9...6.....8...3', 
    '8..7....4.5....6............3.97...8....43..5....2.9....6......2...6...7.71..83.2', 
    '.8...4.5....7..3............1..85...6.....2......4....3.26............417........', 
    '....7..8...6...5...2...3.61.1...7..2..8..534.2..9.......2......58...6.3.4...1....', 
    '......8.16..2........7.5......6...2..1....3...8.......2......7..4..8....5...3....', 
    '.2..........6....3.74.8.........3..2.8..4..1.6..5.........1.78.5....9..........4.', 
    '.52..68.......7.2.......6....48..9..2..41......1.....8..61..38.....9...63..6..1.9', 
    '....1.78.5....9..........4..2..........6....3.74.8.........3..2.8..4..1.6..5.....', 
    '1.......3.6.3..7...7...5..121.7...9...7........8.1..2....8.64....9.2..6....4.....', 
    '4...7.1....19.46.5.....1......7....2..2.3....847..6....14...8.6.2....3..6...9....', 
    '......8.17..2........5.6......7...5..1....3...8.......5......2..3..8....6...4....', 
    '963......1....8......2.5....4.8......1....7......3..257......3...9.2.4.7......9..', 
    '15.3......7..4.2....4.72.....8.........9..1.8.1..8.79......38...........6....7423', 
    '..........5724...98....947...9..3...5..9..12...3.1.9...6....25....56.....7......6', 
    '....75....1..2.....4...3...5.....3.2...8...1.......6.....1..48.2........7........', 
    '6.....7.3.4.8.................5.4.8.7..2.....1.3.......2.....5.....7.9......1....', 
    '....6...4..6.3....1..4..5.77.....8.5...8.....6.8....9...2.9....4....32....97..1..', 
    '.32.....58..3.....9.428...1...4...39...6...5.....1.....2...67.8.....4....95....6.', 
    '...5.3.......6.7..5.8....1636..2.......4.1.......3...567....2.8..4.7.......2..5..', 
    '.5.3.7.4.1.........3.......5.8.3.61....8..5.9.6..1........4...6...6927....2...9..', 
    '..5..8..18......9.......78....4.....64....9......53..2.6.........138..5....9.714.', 
    '..........72.6.1....51...82.8...13..4.........37.9..1.....238..5.4..9.........79.', 
    '...658.....4......12............96.7...3..5....2.8...3..19..8..3.6.....4....473..', 
    '.2.3.......6..8.9.83.5........2...8.7.9..5........6..4.......1...1...4.22..7..8.9', 
    '.5..9....1.....6.....3.8.....8.4...9514.......3....2..........4.8...6..77..15..6.', 
    '.....2.......7...17..3...9.8..7......2.89.6...13..6....9..5.824.....891..........', 
    '3...8.......7....51..............36...2..4....7...........6.13..452...........8..']


misc_problems = ['2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3',
    '9.1....8.8.5.7..4.2.4....6...7......5..............83.3..6......9................',
    '1..2......7..............7.8..5.1.2...43.85...6.4.2..9.3..............4......3..8',
    '9.1....8.8.5.7..4.2.4....6...7......5..............83.3..6......9................',
    '4.......3..9.........1...7.....1.8.....5.9.....1.2.....3...5.........7..7.......8',
    '......3.......12..71..9......36...................56......4..67..95.......8......',
    '....3...1..6..........9...5.......6..1.7.8.2..8.......3...1..........7..9...2....',
    '...47..........8.........5.9..2.1...4.......6...3.6..1.7.........4..........89...',
    '...4.....37.5............89....9......2...7......3....43............2.45.....6...',
    '..7........5.4...........18...3.6....1.....7....8.2...62...........9.6........4..',
    '....29.......7......3...8..........735.....161..........6...4......6.......83....',
    '7.......8.....14...4........7..1.......4.3.......6..2........3...35.....5.......4',
    '5.......7......2.....3...1...8.4.......7.8.......2.9...8...5.....1......6.......9',
    '..682...........69..7.......2..........9.4..........8.......5..58...........521..',
    '13824657965913724827495836174569281391358462782671395449132578636287149558746.132',
    '138246579659137248274958361745692813913584627826713954491325786362.7149558746.132']


if __name__ == '__main__':

    values = '..3.2.6..9..3.5..1..18.64....81.29..7.......8..67.82....26.95..8..2.3..9..5.1.3..'
    values = grid_values(values)
    display(values)
    values = eliminate(values)

    display(values)

#values = solve('..3.2.6..9..3.5..1...8.64....81.29..7.......8..67.82....26.95..8..2.3..9..5.1.3..')
#   print("Solved? " + str(validate(values)))


    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
