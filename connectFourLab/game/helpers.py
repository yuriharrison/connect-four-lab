"""Helpers"""


def check_winner(game_board):
    """Check if there is a winner in a given board

    Split the `game_board` for each player and check, 
    using binary operations, if there is a required 
    combination for a win.

    # Arguments
        game_board: matrix (7x7), required

    # Return
        1: id 1 is the winner
        -1: id -1 is the winner
        None: no winner in the given table

    # Example

    ```
    import numpy as np
    board = np.zeros((7,7), dtype=int)
    board[1,0] = 1
    board[2,0] = 1
    board[3,0] = 1
    board[4,0] = 1
    board[3,1] = -1
    board[3,2] = -1
    board[3,3] = -1

    winner = check_winner(board)
    if winner:
        print('Winner id:', winner)
    ```
    """
    #horizontal, vertical, diagonal: top-bottom, bottom-top
    directions = [8,1,7,9] # 7x7 table

    # directions = [7,1,6,8] # 7x6 table
    # directions = [6,1,5,7] # 6x6 table

    p1_board, p2_board = bit_board_split(game_board)

    for direction in directions:
        tmp_board = p1_board & (p1_board >> direction)
        if tmp_board & (tmp_board >> 2*direction):
            return 1

        tmp_board = p2_board & (p2_board >> direction)
        if tmp_board & (tmp_board >> 2*direction):
            return -1


def bit_board_split(board):
    """Split a given board in a bit board for each player

    # Arguments
        board: matrix (7x7), required

    # Return
        Return a bit board of 56 of length, one for each player, which represents
        (in binary) the positions of the player on the board.
    """
    p1_board, p2_board = 56*['0'], 56*['0']#56*['0'], 56*['0']
    bit_index = 0

    for _ in board:
        for value in _:
            if value == 1:
                p1_board[bit_index] = '1'
            elif value == -1:
                p2_board[bit_index] = '1'

            bit_index += 1
        
        bit_index += 1

    p1_board = int(str().join(p1_board), 2)
    p2_board = int(str().join(p2_board), 2)

    return p1_board, p2_board


def next_position(board, column):
    """Return the next availabe position in a column
    
    # Arguments
        board: matrix, required
        column: int (0 to 6) - required - Index of the column

    # Return
        Index (row) of availabe position

    # Exception
        IndexError: `column` argument out of range.
    """
    if column < 0 or column > 6:
        raise IndexError('Column out of range.')

    for i, value in enumerate(board[column]):
        if value == 0:
            return i


def available_positions(board):
    """Yield all empty positions of a given board
    
    # Arguments
        board: matrix, required

    # Yield
        Index of the column and row of all empty positions in the `board`

    # Example

    ```python
    import numpy as np
    board = np.zeros((7,7), dtype=int)
    board[0,0] = 1
    board[1,0] = -1
    board[3,0] = 1
    board[3,1] = -1
    board[6,0] = -1

    for x, y in available_positions(board):
        print('Column: {} - Row: {}'.format(x, y))
        print('Position:', board[x,y])
    ```
    """
    for column, _ in enumerate(board):
        for row, value in enumerate(_):
            if value == 0:
                yield column, row
                break

                
def seconds_to_hms(seconds):
    """Convert seconds in hour, minutes and seconds
    
    # Example

    ```python
    h, m, s = seconds_to_hms(5401)
    print('Hour: {} Minutes: {} Seconds: {}'.format(h, m, s))
    ```
    """
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return h,m,s