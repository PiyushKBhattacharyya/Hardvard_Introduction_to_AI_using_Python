import math

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]

def player(board):
    """
    Returns player who has the next turn on a board.
    """
    x_count = 0
    o_count = 0
    for row in board:
        x_count += row.count(X)
        o_count += row.count(O)
    if x_count > o_count:
        return O
    else:
        return X

def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    possible_actions = set()
    for i in range(3):
        for j in range(3):
            if board[i][j] is None:
                possible_actions.add((i, j))
    return possible_actions

def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    new_board = [row.copy() for row in board]
    new_board[action[0]][action[1]] = player(board)
    return new_board

def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    for row in board:
        if row.count(row[0]) == 3 and row[0] is not None:
            return row[0]

    for col in range(3):
        check = []
        for row in board:
            check.append(row[col])
        if check.count(check[0]) == 3 and check[0] is not None:
            return check[0]

    if board[0][0] == board[1][1] == board[2][2] and board[0][0] is not None:
        return board[0][0]

    if board[0][2] == board[1][1] == board[2][0] and board[0][2] is not None:
        return board[0][2]

    return None

def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) is not None:
        return True

    for row in board:
        if None in row:
            return False

    return True

def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if winner(board) == X:
        return 1
    elif winner(board) == O:
        return -1
    else:
        return 0

def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
        return None

    if player(board) == X:
        max_eval = -math.inf
        for action in actions(board):
            eval = minimax(result(board, action))[0]
            max_eval = max(max_eval, eval)
        return None, max_eval

    else:
        min_eval = math.inf
        for action in actions(board):
            eval = minimax(result(board, action))[0]
            min_eval = min(min_eval, eval)
        return None, min_eval

    optimal_action = None
    optimal_eval = -math.inf if player(board) == X else math.inf
    for action in actions(board):
        eval = utility(result(board, action))
        if player(board) == X:
            if eval > optimal_eval:
                optimal_eval = eval
                optimal_action = action
        else:
            if eval < optimal_eval:
                optimal_eval = eval
                optimal_action = action

    return optimal_action, optimal_eval