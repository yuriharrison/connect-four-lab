#imports


def check_winner(game_board):
    #horizontal, vertical, diagonal: top-bottom, bottom-top
    checkers = [8,1,7,9] # 7x7 table

    # checkers = [7,1,6,8] # 7x6 table
    # checkers = [6,1,5,7] # 6x6 table

    p1_board, p2_board = bit_board_split(game_board)

    for check in checkers:
        tmp_board = p1_board & (p1_board >> check)
        if tmp_board & (tmp_board >> 2*check):
            return 1

        tmp_board = p2_board & (p2_board >> check)
        if tmp_board & (tmp_board >> 2*check):
            return -1


def bit_board_split(board):
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
    for i, value in enumerate(board[column]):
        if value == 0:
            return i


def available_positions(board):
    for column, _ in enumerate(board):
        for row, value in enumerate(_):
            if value == 0:
                yield column, row
                break

                
def seconds_to_hms(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return h,m,s