#   Look for #IMPLEMENT tags in this file. These tags indicate what has
#   to be implemented to complete the warehouse domain.

#   You may add only standard python imports
#   You may not remove any imports.
#   You may not import or otherwise source any of your own files

import os  # for time functions
import math  # for infinity
from search import *  # for search engines
from sokoban import sokoban_goal_state, SokobanState, Direction, \
    PROBLEMS  # for Sokoban specific classes and problems


# SOKOBAN HEURISTICS
def heur_alternate(state):
    '''a better heuristic'''
    '''INPUT: a sokoban state'''
    '''OUTPUT: a numeric value that serves as an estimate of the distance of the state to the goal.'''
    # heur_manhattan_distance has flaws.
    # Write a heuristic function that improves upon heur_manhattan_distance to estimate distance between the current state and the goal.
    # Your function should return a numeric value for the estimate of the distance to the goal.
    # EXPLAIN YOUR HEURISTIC IN THE COMMENTS. Please leave this function (and your explanation) at the top of your solution file, to facilitate marking.
    """Alternate heuristic using a two-layer Hungarian assignment."""
    """Alternate heuristic using a two-layer Hungarian assignment without external imports."""
    robots = list(state.robots)
    boxes = list(state.boxes)
    goals = list(state.storage)

    if not robots or not boxes or not goals:
        return 0
    INF=999
    def manhattan_distance(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Deadlock detection function
    def is_deadlock(box, goals, obstacles):
        """
        Check if a box is in a deadlock position (e.g., corner without a goal).
        """
        x, y = box
        # Check if the box is in a corner
        if ((x - 1, y) in obstacles and (x, y - 1) in obstacles) or \
                ((x + 1, y) in obstacles and (x, y - 1) in obstacles) or \
                ((x - 1, y) in obstacles and (x, y + 1) in obstacles) or \
                ((x + 1, y) in obstacles and (x, y + 1) in obstacles):
            return box not in goals
        return False

    # Hungarian algorithm for optimal assignment
    def hungarian_algorithm(cost_matrix):
        n = len(cost_matrix)
        min_cost = float('inf')
        best_assignment = []

        def permute(arr, l, r):
            nonlocal min_cost, best_assignment
            if l == r:
                cost = sum(cost_matrix[i][arr[i]] for i in range(n))
                if cost < min_cost:
                    min_cost = cost
                    best_assignment = list(enumerate(arr))
            else:
                for i in range(l, r + 1):
                    arr[l], arr[i] = arr[i], arr[l]
                    permute(arr, l + 1, r)
                    arr[l], arr[i] = arr[i], arr[l]

        permute(list(range(n)), 0, n - 1)
        return best_assignment

    # First assignment: Robots to boxes
    size = max(len(robots), len(boxes))
    robot_box_cost = [[INF] * size for _ in range(size)]
    for i in range(len(robots)):
        for j in range(len(boxes)):
            robot_box_cost[i][j] = manhattan_distance(robots[i], boxes[j])

    robot_box_assignment = hungarian_algorithm(robot_box_cost)
    robot_box_cost_total = sum(robot_box_cost[i][j] for i, j in robot_box_assignment if i < len(robots) and j < len(boxes))

    # Second assignment: Boxes to goals
    size = max(len(boxes), len(goals))
    box_goal_cost = [[INF] * size for _ in range(size)]
    for i in range(len(boxes)):
        for j in range(len(goals)):
            box_goal_cost[i][j] = manhattan_distance(boxes[i], goals[j])

    box_goal_assignment = hungarian_algorithm(box_goal_cost)
    box_goal_cost_total = sum(box_goal_cost[i][j] for i, j in box_goal_assignment if i < len(boxes) and j < len(goals))

    # Deadlock detection: Penalize deadlock positions
    deadlock_penalty = 0
    for box in boxes:
        if is_deadlock(box, goals, state.obstacles):
            deadlock_penalty += 1000  # Large penalty for deadlocks

    return robot_box_cost_total + box_goal_cost_total + deadlock_penalty


def heur_zero(state):
    '''Zero Heuristic can be used to make A* search perform uniform cost search'''
    return 0


def heur_manhattan_distance(state):
    '''admissible sokoban puzzle heuristic: manhattan distance'''
    '''INPUT: a sokoban state'''
    '''OUTPUT: a numeric value that serves as an estimate of the distance of the state to the goal.'''
    # We want an admissible heuristic, which is an optimistic heuristic.
    # It must never overestimate the cost to get from the current state to the goal.
    # The sum of the Manhattan distances between each box that has yet to be stored and the storage point nearest to it is such a heuristic.
    # When calculating distances, assume there are no obstacles on the grid.
    # You should implement this heuristic function exactly, even if it is tempting to improve it.
    # Your function should return a numeric value; this is the estimate of the distance to the goal.
    boxes = state.boxes
    storage = state.storage
    total_distance = 0

    # Iterate through each box and find the Manhattan distance to the closest storage point
    for box in boxes:
        min_distance = min(
            abs(box[0] - goal[0]) + abs(box[1] - goal[1])  # Manhattan distance
            for goal in storage
        )
        total_distance += min_distance
    return total_distance


def fval_function(sN, weight):
    """
    Provide a custom formula for f-value computation for Anytime Weighted A star.
    Returns the fval of the state contained in the sNode.

    @param sNode sN: A search node (containing a SokobanState)
    @param float weight: Weight given by Anytime Weighted A star
    @rtype: float
    """
    return sN.gval + (weight * sN.hval)


# SEARCH ALGORITHMS
def weighted_astar(initial_state, heur_fn, weight, timebound):
    """Provides an implementation of weighted a-star, as described in the HW1 handout"""
    '''INPUT: a sokoban state that represents the start state and a time-bound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of weighted astar algorithm'''
    search = SearchEngine(strategy='custom',cc_level='full')
    search.init_search(initial_state, sokoban_goal_state, heur_fn, lambda s: fval_function(s, weight))
    return search.search(timebound)


def iterative_astar(initial_state, heur_fn, weight=1,
                    timebound=5):  # uses f(n), see how autograder initializes a search line 88
    '''Provides an implementation of realtime a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of iterative astar algorithm'''
    best_solution = None
    best_stats = None
    remaining_time = timebound
    weight_step = 0.5  # Decrease weight in steps
    best_cost = float('inf')

    while weight >= 1 and remaining_time > 0:
        se = SearchEngine(strategy='custom', cc_level='full')
        se.init_search(initial_state, sokoban_goal_state, heur_fn, lambda s: fval_function(s, weight))
        solution, stats = se.search(remaining_time, costbound=(best_cost, float('inf'), float('inf')) if best_solution else None)

        if solution:
            best_solution, best_stats = solution, stats
            best_cost = solution.gval  # Update cost bound with new best solution

        weight -= weight_step  # Reduce weight for next iteration
        remaining_time -= stats.total_time if stats else 0

    return best_solution, best_stats


def iterative_gbfs(initial_state, heur_fn, timebound=5):  # only use h(n)
    '''Provides an implementation of anytime greedy best-first search, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False'''
    '''implementation of iterative gbfs algorithm'''
    best_solution = None
    best_stats = None
    remaining_time = timebound

    while remaining_time > 0:
        se = SearchEngine(strategy='best_first', cc_level='full')
        se.init_search(initial_state, sokoban_goal_state, heur_fn)
        solution, stats = se.search(remaining_time)

        if solution:
            best_solution, best_stats = solution, stats

        remaining_time -= stats.total_time if stats else 0

    return best_solution, best_stats
