# Artificial Intelligence Nanodegree
## Introductory Project: Diagonal Sudoku Solver

# Question 1 (Naked Twins)
Q: How do we use constraint propagation to solve the naked twins problem? 

A: The goal of constraint propagation is to reduce the number of possibilities in a search space, by eliminating combinations that are not possible by the given rules/constraints. By repeateadly applying constraint propagation (till no reduction in search space is possible), we can propagate the effect of change in one box to other boxes. By reducing the search space, we can apply the Search technique - which otherwise (i.e. without reduction) can take eons to finish.

We have seen two such strategies:
 - Elimination: If a box has a single digit, by rules of sudoku, none of the peers can have the same digit. Hence we can eliminate that digit from all it's peers.
 - Only Choice: If a box has multiple digits, and if one among those happens to fit (eligible for) only that box among all it's peers - we can directly assign it to the box.

A further reduction technique is the naked twins problem. If within a set of peers, (a) a sequence of digits is repeating (b) and the length of the digits and the number of boxes where they are repeating is same (i.e. '27' repeating in two boxes, '387' repeating in three boxes etc.), we are sure that these 'n' digits can be set in those 'n' boxes only. Hence they can be eliminated from any other boxes within peers - if they appear. This helps further in optimizing for Search.


# Question 2 (Diagonal Sudoku)
Q: How do we use constraint propagation to solve the diagonal sudoku problem? 

A: Given that we already have the logic in place to solve normal sudoku, solving the diagonal sudoku problem is like adding one more extra constraing.

We already have three constraints in normal sudoku a) digits should be repeat in rows b) digits should not repeat in columns c) digits should not repeat in the sub 3x3 squares.

These constraints are expressed in the form of units (a group of boxes where digits should not repeat) and peers (all boxes of all units that a particular box is part of). The sudoku algorithm works on these constructs. New constraints can be introduced to the algorithm by adding them to the above constructs.

Hence by creating two more units for the two leading diagonals, and by adding them to the unitlist, peers and units data structures - we can apply the same Search and Constraint Propagation methods to find the solution. Since the methods look into a box's peers and units, they automatically take in the new constraint and make sure the uniqueness of digits is maintained within all units.




### Install

This project requires **Python 3**.

We recommend students install [Anaconda](https://www.continuum.io/downloads), a pre-packaged Python distribution that contains all of the necessary libraries and software for this project. 
Please try using the environment we provided in the Anaconda lesson of the Nanodegree.

##### Optional: Pygame

Optionally, you can also install pygame if you want to see your visualization. If you've followed our instructions for setting up our conda environment, you should be all set.

If not, please see how to download pygame [here](http://www.pygame.org/download.shtml).

### Code

* `solution.py` - You'll fill this in as part of your solution.
* `solution_test.py` - Do not modify this. You can test your solution by running `python solution_test.py`.
* `PySudoku.py` - Do not modify this. This is code for visualizing your solution.
* `visualize.py` - Do not modify this. This is code for visualizing your solution.

### Visualizing

To visualize your solution, please only assign values to the values_dict using the ```assign_values``` function provided in solution.py

### Submission
Before submitting your solution to a reviewer, you are required to submit your project to Udacity's Project Assistant, which will provide some initial feedback. 

The setup is simple.  If you have not installed the client tool already, then you may do so with the command `pip install udacity-pa`. 

To submit your code to the project assistant, run `udacity submit` from within the top-level directory of this project.  You will be prompted for a username and password.  If you login using google or facebook, visit [this link](https://project-assistant.udacity.com/auth_tokens/jwt_login for alternate login instructions.

This process will create a zipfile in your top-level directory named sudoku-<id>.zip.  This is the file that you should submit to the Udacity reviews system.

