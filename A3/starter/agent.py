"""
An AI player for Othello. 
"""

import random
import sys
import time

# You can use the functions in othello_shared to write your AI
from othello_shared import find_lines, get_possible_moves, get_score, play_move
min_dict = dict()
max_dict = dict()
alpha_dict = dict()
beta_dict = dict()

def eprint(*args, **kwargs): #you can use this for debugging, as it will print to sterr and not stdout
    print(*args, file=sys.stderr, **kwargs)

# Method to compute utility value of terminal state
def compute_utility(board, color):
    #IMPLEMENT
    final_score = get_score(board)
    if color == 1:
        return final_score[0] - final_score[1]

    return final_score[1] - final_score[0]

# Better heuristic value of board
def compute_heuristic(board, color): #not implemented, optional
    opponent_color = 1 if color == 2 else 2

    # Constants for weighting heuristic components
    WEIGHT_PIECE_COUNT = 2
    WEIGHT_CORNERS = 10
    WEIGHT_STABILITY = 5
    WEIGHT_MOBILITY = 5
    WEIGHT_FRONTIER = -2

    # Helper functions
    def get_corners():
        rows = len(board)
        cols = len(board[0]) if rows > 0 else 0
        corners = [(0, 0), (0, cols - 1), (rows - 1, 0), (rows - 1, cols - 1)]
        return corners

    def count_corners(board, color):
        corners = get_corners()
        return sum(1 for (i, j) in corners if board[i][j] == color)

    def count_stable_disks(board, color):
        # Count stable disks (corners and edges that cannot be flipped)
        stable = 0
        corners = get_corners()
        for (i, j) in corners:
            if board[i][j] == color:
                stable += 1
                # Check edges adjacent to corners
                for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    ni, nj = i + di, j + dj
                    if 0 <= ni < len(board) and 0 <= nj < len(board[0]) and board[ni][nj] == color:
                        stable += 1
        return stable

    def count_frontier_disks(board, color):
        frontier = 0
        for i in range(len(board)):
            for j in range(len(board[0])):
                if board[i][j] == color:
                    for di, dj in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
                        ni, nj = i + di, j + dj
                        if 0 <= ni < len(board) and 0 <= nj < len(board[0]) and board[ni][nj] == 0:
                            frontier += 1
                            break
        return frontier

    # Calculate heuristic components
    my_pieces = sum(row.count(color) for row in board)
    opp_pieces = sum(row.count(opponent_color) for row in board)
    piece_diff = my_pieces - opp_pieces

    my_corners = count_corners(board, color)
    opp_corners = count_corners(board, opponent_color)
    corner_diff = my_corners - opp_corners

    my_stable = count_stable_disks(board, color)
    opp_stable = count_stable_disks(board, opponent_color)
    stable_diff = my_stable - opp_stable

    my_mobility = len(get_possible_moves(board, color))
    opp_mobility = len(get_possible_moves(board, opponent_color))
    mobility_diff = my_mobility - opp_mobility

    my_frontier = count_frontier_disks(board, color)
    opp_frontier = count_frontier_disks(board, opponent_color)
    frontier_diff = opp_frontier - my_frontier  # Fewer frontier disks are better

    # Combine components with weights
    heuristic_value = (
            WEIGHT_PIECE_COUNT * piece_diff +
            WEIGHT_CORNERS * corner_diff +
            WEIGHT_STABILITY * stable_diff +
            WEIGHT_MOBILITY * mobility_diff +
            WEIGHT_FRONTIER * frontier_diff
    )

    return heuristic_value
def opponent(player):
    if player == 1:
        return 2
    return 1


############ MINIMAX ###############################
def minimax_min_node(board, color, limit, caching = 0):
    #IMPLEMENT
    if caching:
        if (board, color) in min_dict:
            return min_dict[(board, color)]

    moves = get_possible_moves(board, color)
    if moves == [] or limit == 0:
        result = (None, (-1) * compute_utility(board, color))
        if caching:
            min_dict[(board, color)] = result
        return result

    min_uti = float("inf")
    bst_move = moves[0]

    for move in moves:
        new_board = play_move(board, color, move[0], move[1])
        uti = minimax_max_node(new_board, opponent(color), limit-1, caching)[1]
        if uti < min_uti:
            bst_move = move
            min_uti = uti

    if caching:
        min_dict[(board, color)] = (bst_move, min_uti)

    return (bst_move, min_uti)

def minimax_max_node(board, color, limit, caching = 0): #returns highest possible utility
    #IMPLEMENT
    if caching:
        if (board, color) in max_dict:
            return max_dict[(board, color)]

    moves = get_possible_moves(board, color)
    if moves == [] or limit == 0:
        result = (None, compute_utility(board, color))
        if caching:
            max_dict[(board, color)] = result
        return result

    max_uti = float("-inf")
    bst_move = moves[0]

    for move in moves:
        new_board = play_move(board, color, move[0], move[1])
        uti = minimax_min_node(new_board,  opponent(color), limit-1, caching)[1]
        if uti > max_uti:
            bst_move = move
            max_uti = uti

    if caching:
        max_dict[(board, color)] = (bst_move, max_uti)

    return (bst_move, max_uti)

def select_move_minimax(board, color, limit, caching = 0):
    """
    Given a board and a player color, decide on a move.
    The return value is a tuple of integers (i,j), where
    i is the column and j is the row on the board.

    Note that other parameters are accepted by this function:
    If limit is a positive integer, your code should enfoce a depth limit that is equal to the value of the parameter.
    Search only to nodes at a depth-limit equal to the limit.  If nodes at this level are non-terminal return a heuristic
    value (see compute_utility)
    If caching is ON (i.e. 1), use state caching to reduce the number of state evaluations.
    If caching is OFF (i.e. 0), do NOT use state caching to reduce the number of state evaluations.
    """
    #IMPLEMENT
    return minimax_max_node(board, color, limit, caching)[0] #change this!

############ ALPHA-BETA PRUNING #####################
def alphabeta_min_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    if caching:
        if (board, color) in beta_dict:
            return beta_dict[(board, color)]

    moves = get_possible_moves(board, color)
    if moves == [] or limit == 0:
        result = (None, (-1) * compute_heuristic(board, color))
        if caching:
            beta_dict[(board, color)] = result
        return result

    min_uti = float("inf")
    bst_move = moves[0]
    new_boards = []

    for move in moves:
        new_board = play_move(board, color, move[0], move[1])
        new_boards.append(new_board)

    if ordering:
        new_boards.sort(key=lambda board: compute_heuristic(board, color),reverse=True)

    for new_board in new_boards:
        uti = alphabeta_max_node(new_board, opponent(color),alpha, beta, limit-1, caching, ordering)[1]
        if uti < min_uti:
            bst_move = move
            min_uti = uti
        beta = min(beta, min_uti)
        if beta <= alpha:
            break

    if caching:
        beta_dict[(board, color)] = (bst_move, min_uti)

    return (bst_move, min_uti)

def alphabeta_max_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    if caching:
        if (board, color) in alpha_dict:
            return alpha_dict[(board, color)]

    moves = get_possible_moves(board, color)
    if moves == [] or limit == 0:
        result = (None, compute_heuristic(board, color))
        if caching:
            alpha_dict[(board, color)] = result
        return result

    max_uti = float("-inf")
    bst_move = moves[0]
    new_boards = []
    for move in moves:
        new_board = play_move(board, color, move[0], move[1])
        new_boards.append(new_board)

    if ordering:
        new_boards.sort(key=lambda board: compute_heuristic(board, color),reverse=True)

    for new_board in new_boards:
        uti = alphabeta_min_node(new_board, opponent(color),alpha, beta, limit-1, caching, ordering)[1]
        if uti > max_uti:
            bst_move = move
            max_uti = uti
        alpha = max(alpha, max_uti)
        if beta <= alpha:
            break

    if caching:
        alpha_dict[(board, color)] = (bst_move, max_uti)

    return (bst_move, max_uti)

def select_move_alphabeta(board, color, limit, caching = 0, ordering = 0):
    """
    Given a board and a player color, decide on a move.
    The return value is a tuple of integers (i,j), where
    i is the column and j is the row on the board.

    Note that other parameters are accepted by this function:
    If limit is a positive integer, your code should enfoce a depth limit that is equal to the value of the parameter.
    Search only to nodes at a depth-limit equal to the limit.  If nodes at this level are non-terminal return a heuristic
    value (see compute_utility)
    If caching is ON (i.e. 1), use state caching to reduce the number of state evaluations.
    If caching is OFF (i.e. 0), do NOT use state caching to reduce the number of state evaluations.
    If ordering is ON (i.e. 1), use node ordering to expedite pruning and reduce the number of state evaluations.
    If ordering is OFF (i.e. 0), do NOT use node ordering to expedite pruning and reduce the number of state evaluations.
    """
    #IMPLEMENT
    return alphabeta_max_node(board, color, float("-inf"), float("inf"), limit, caching, ordering)[0] #change this!

####################################################
def run_ai():
    """
    This function establishes communication with the game manager.
    It first introduces itself and receives its color.
    Then it repeatedly receives the current score and current board state
    until the game is over.
    """
    print("Othello AI") # First line is the name of this AI
    arguments = input().split(",")

    color = int(arguments[0]) #Player color: 1 for dark (goes first), 2 for light.
    limit = int(arguments[1]) #Depth limit
    minimax = int(arguments[2]) #Minimax or alpha beta
    caching = int(arguments[3]) #Caching
    ordering = int(arguments[4]) #Node-ordering (for alpha-beta only)

    if (minimax == 1): eprint("Running MINIMAX")
    else: eprint("Running ALPHA-BETA")

    if (caching == 1): eprint("State Caching is ON")
    else: eprint("State Caching is OFF")

    if (ordering == 1): eprint("Node Ordering is ON")
    else: eprint("Node Ordering is OFF")

    if (limit == -1): eprint("Depth Limit is OFF")
    else: eprint("Depth Limit is ", limit)

    if (minimax == 1 and ordering == 1): eprint("Node Ordering should have no impact on Minimax")

    while True: # This is the main loop
        # Read in the current game status, for example:
        # "SCORE 2 2" or "FINAL 33 31" if the game is over.
        # The first number is the score for player 1 (dark), the second for player 2 (light)
        next_input = input()
        status, dark_score_s, light_score_s = next_input.strip().split()
        dark_score = int(dark_score_s)
        light_score = int(light_score_s)

        if status == "FINAL": # Game is over.
            print
        else:
            board = eval(input()) # Read in the input and turn it into a Python
                                  # object. The format is a list of rows. The
                                  # squares in each row are represented by
                                  # 0 : empty square
                                  # 1 : dark disk (player 1)
                                  # 2 : light disk (player 2)

            # Select the move and send it to the manager
            if (minimax == 1): #run this if the minimax flag is given
                movei, movej = select_move_minimax(board, color, limit, caching)
            else: #else run alphabeta
                movei, movej = select_move_alphabeta(board, color, limit, caching, ordering)

            print("{} {}".format(movei, movej))

if __name__ == "__main__":
    run_ai()