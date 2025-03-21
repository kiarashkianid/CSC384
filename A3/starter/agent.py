"""
An AI player for Othello. 
"""

import random
import sys
import time

# You can use the functions from othello_shared to write your AI
from othello_shared import find_lines, get_possible_moves, get_score, play_move

cache = {} # Use this for state caching

def eprint(*args, **kwargs): #use this for debugging, to print to sterr
    print(*args, file=sys.stderr, **kwargs)
    
def compute_utility(board, color):
    """
    Method to compute the utility value of board.
    INPUT: a game state and the player that is in control
    OUTPUT: an integer that represents utility
    """
    scores = get_score(board)
    if color == 1:
        return scores[1] - scores[0]
    else:
        return scores[0] - scores[1]

def compute_heuristic(board, color):
    """
    Method to heuristic value of board, to be used if we are at a depth limit.
    INPUT: a game state and the player that is in control
    OUTPUT: an integer that represents heuristic value
    """
    opponent = 1 if color == 2 else 2
    my_pieces = sum(row.count(color) for row in board)
    opp_pieces = sum(row.count(opponent) for row in board)
    return my_pieces - opp_pieces

############ MINIMAX ###############################
def minimax_min_node(board, color, limit, caching = 0):
    """
    A helper function for minimax that finds the lowest possible utility
    """
    # HINT:
    # 1. Get the allowed moves
    # 2. Check if w are at terminal state
    # 3. If not, for each possible move, get the max utiltiy
    # 4. After checking every move, you can find the minimum utility
    # ...
    if color == 1:
        opponent = 2
    else:
        opponent = 1

        # Terminal condition: Reached depth limit or no moves left
    if limit == 0 or not get_possible_moves(board, color):
        return compute_utility(board, color)

        # Check cache if caching is enabled
    if caching and board in cache:
        return cache[board]

    v = float("Inf")
    for move in get_possible_moves(board, color):
        new_board = play_move(board, color, move[0], move[1])
        v = min(v, minimax_max_node(new_board, opponent, limit - 1, caching))

    # Store result in cache if caching is enabled
    if caching:
        cache[board] = v

    return v


def minimax_max_node(board, color, limit, caching = 0):
    """
    A helper function for minimax that finds the highest possible utility
    """
    # HINT:
    # 1. Get the allowed moves
    # 2. Check if w are at terminal state
    # 3. If not, for each possible move, get the min utiltiy
    # 4. After checking every move, you can find the maximum utility
    # ...
    if color == 1:
        opponent = 2
    else:
        opponent = 1

        # Terminal condition: Reached depth limit or no moves left
    if limit == 0 or not get_possible_moves(board, color):
        return compute_utility(board, color)

        # Check cache if caching is enabled
    if caching and board in cache:
        return cache[board]

    v = float("-Inf")
    for move in get_possible_moves(board, color):
        new_board = play_move(board, color, move[0], move[1])
        v = max(v, minimax_min_node(new_board, opponent, limit - 1, caching))

    # Store result in cache if caching is enabled
    if caching:
        cache[board] = v

    return v
    
def select_move_minimax(board, color, limit, caching = 0):
    """
    Given a board and a player color, decide on a move using Minimax algorithm. 
    Note that other parameters are accepted by this function:
    If limit is a positive integer, your code should enfoRce a depth limit that is equal to the value of the parameter.
    Search only to nodes at a depth-limit equal to the limit.  If nodes at this level are non-terminal return a heuristic 
    value (see compute_utility)
    If caching is ON (i.e. 1), use state caching to reduce the number of state evaluations.
    If caching is OFF (i.e. 0), do NOT use state caching to reduce the number of state evaluations.
    INPUT: a game state, the player that is in control, the depth limit for the search, and a flag determining whether state caching is on or not
    OUTPUT: a tuple of integers (i,j) representing a move, where i is the column and j is the row on the board.
    """
    moves = []
    for option in get_possible_moves(board, color):  # get all minimizer moves
        new_move = play_move(board, color, option[0], option[1])
        utility = minimax_max_node(new_move, color, limit)
        if new_move not in cache:
            cache[new_move] = utility
        moves.append([(option[0], option[1]), utility])
    sorted_options = sorted(moves, key=lambda x: x[1])
    return sorted_options[0][0]

############ ALPHA-BETA PRUNING #####################
def alphabeta_min_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    """
    A helper function for alpha-beta that finds the lowest possible utility (don't forget to utilize and update alpha and beta!)
    """
    opponent = 2 if color == 1 else 1

    # Terminal condition: reached depth limit or no moves left
    if limit == 0 or not get_possible_moves(board, color):
        return compute_utility(board, color)

    # Use cached value if caching is enabled
    if caching and board in cache:
        return cache[board]

    v = float("Inf")
    for move in get_possible_moves(board, color):
        new_board = play_move(board, color, move[0], move[1])
        v = min(v, alphabeta_max_node(new_board, opponent, alpha, beta, limit - 1, caching, ordering))

        # Alpha-beta pruning
        if v <= alpha:
            return v
        beta = min(beta, v)

    # Store result in cache if caching is enabled
    if caching:
        cache[board] = v

    return v

def alphabeta_max_node(board, color, alpha, beta, limit, caching = 0, ordering = 0):
    """
    A helper function for alpha-beta that finds the highest possible utility (don't forget to utilize and update alpha and beta!)
    """
    opponent = 2 if color == 1 else 1

    # Terminal condition: reached depth limit or no moves left
    if limit == 0 or not get_possible_moves(board, color):
        return compute_utility(board, color)

    # Use cached value if caching is enabled
    if caching and board in cache:
        return cache[board]

    v = float("-Inf")
    for move in get_possible_moves(board, color):
        new_board = play_move(board, color, move[0], move[1])
        v = max(v, alphabeta_min_node(new_board, opponent, alpha, beta, limit - 1, caching, ordering))

        # Alpha-beta pruning
        if v >= beta:
            return v
        alpha = max(alpha, v)

    # Store result in cache if caching is enabled
    if caching:
        cache[board] = v

    return v

def select_move_alphabeta(board, color, limit = -1, caching = 0, ordering = 0):
    """
    Given a board and a player color, decide on a move using Alpha-Beta algorithm. 
    Note that other parameters are accepted by this function:
    If limit is a positive integer, your code should enfoce a depth limit that is equal to the value of the parameter.
    Search only to nodes at a depth-limit equal to the limit.  If nodes at this level are non-terminal return a heuristic 
    value (see compute_utility)
    If caching is ON (i.e. 1), use state caching to reduce the number of state evaluations.
    If caching is OFF (i.e. 0), do NOT use state caching to reduce the number of state evaluations.    
    If ordering is ON (i.e. 1), use node ordering to expedite pruning and reduce the number of state evaluations. 
    If ordering is OFF (i.e. 0), do NOT use node ordering to expedite pruning and reduce the number of state evaluations. 
    INPUT: a game state, the player that is in control, the depth limit for the search, a flag determining whether state caching is on or not, a flag determining whether node ordering is on or not
    OUTPUT: a tuple of integers (i,j) representing a move, where i is the column and j is the row on the board.
    """
    alpha = float("-Inf")
    beta = float("Inf")
    best_move = None
    best_value = float("-Inf")

    possible_moves = get_possible_moves(board, color)

    # Apply move ordering if enabled
    if ordering:
        possible_moves = sorted(possible_moves, key=lambda move:
        compute_utility(play_move(board, color, move[0], move[1]), color),
                                reverse=True)

    for move in possible_moves:
        new_board = play_move(board, color, move[0], move[1])
        move_value = alphabeta_min_node(new_board, 2 if color == 1 else 1, alpha, beta, limit - 1, caching, ordering)

        # Update best move
        if move_value > best_value:
            best_value = move_value
            best_move = move

        # Alpha-beta pruning
        alpha = max(alpha, move_value)

    return best_move if best_move else (-1, -1)  # Return a default move if no moves are possible

####################################################
def run_ai():
    """
    This function establishes communication with the game manager.
    It first introduces itself and receives its color.
    Then it repeatedly receives the current score and current board state until the game is over.
    """
    print("Othello AI") # First line is the name of this AI
    arguments = input().split(",")
    
    color = int(arguments[0]) # Player color: 1 for dark (goes first), 2 for light. 
    limit = int(arguments[1]) # Depth limit
    minimax = int(arguments[2]) # Minimax or alpha beta
    caching = int(arguments[3]) # Caching 
    ordering = int(arguments[4]) # Node-ordering (for alpha-beta only)

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
            if (minimax == 1): # run this if the minimax flag is given
                movei, movej = select_move_minimax(board, color, limit, caching)
            else: # else run alphabeta
                movei, movej = select_move_alphabeta(board, color, limit, caching, ordering)
            
            print("{} {}".format(movei, movej))

if __name__ == "__main__":
    run_ai()
