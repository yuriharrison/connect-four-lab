"""helpers.py test"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

import pytest
import numpy as np
from copy import deepcopy
from connectFourLab.game import helpers


def empty_board():
    return deepcopy(np.zeros((7,7), dtype=int))


def test_check_winner():
    # player id -1
    board = empty_board()
    board[1,0] = -1
    board[2,0] = -1
    board[3,0] = -1
    board[4,0] = -1

    winner = helpers.check_winner(board)
    assert winner == -1

    # no winner
    board = empty_board()
    winner = helpers.check_winner(board)
    board[1,0] = 1
    board[2,0] = -1
    board[3,0] = 1
    board[4,0] = 1
    assert winner is None

    winner = helpers.check_winner(board)
    assert not winner

    # vertical win
    board = empty_board()
    board[0,0] = 1
    board[0,1] = 1
    board[0,2] = 1
    board[0,3] = 1

    winner = helpers.check_winner(board)
    assert winner == 1

    # diagonal
    board = empty_board()
    board[0,0] = 1
    board[1,1] = 1
    board[2,2] = 1
    board[3,3] = 1

    winner = helpers.check_winner(board)
    assert winner == 1

    board = empty_board()
    board[0,3] = 1
    board[1,2] = 1
    board[2,1] = 1
    board[3,0] = 1

    winner = helpers.check_winner(board)
    assert winner == 1


def test_bit_board_split():
    board = empty_board()
    bb1, bb2 = helpers.bit_board_split(board)
    assert bb1 == 0 and bb2 == 0
    
    board[0,3] = 1
    board[1,2] = 1
    board[2,1] = 1
    board[3,0] = 1
    board[0,2] = -1
    board[0,1] = -1
    board[2,0] = -1
    board[3,1] = -1

    bb1, bb2 = helpers.bit_board_split(board)
    assert 4539061024849920, 27022148593778688


def test_next_position():
    board = empty_board()
    column = 2
    board[2,0] = 1
    board[2,1] = 1
    board[2,2] = 1
    board[2,3] = 1

    assert helpers.next_position(board, column) == 4

    with pytest.raises(IndexError):
        helpers.next_position(board, -1)

    with pytest.raises(IndexError):
        helpers.next_position(board, 7)


def test_available_positions():
    board = empty_board()

    for i in range(7):
        board[2, i] = 1
        if i is not 2:
            board[i, 0] = 1

    board[0,1] = 1
    board[3,1] = 1
    board[3,2] = 1
    board[4,1] = 1
    board[4,2] = 1
    board[4,3] = 1

    for column, row in helpers.available_positions(board):
        assert column is not 0 or row == 2
        assert column is not 1 or row == 1
        assert column is not 2
        assert column is not 3 or row == 3
        assert column is not 4 or row == 4
        assert column is not 5 or row == 1
        assert column is not 6 or row == 1


def test_seconds_to_hms():
    h,m,s = helpers.seconds_to_hms(19805)
    assert h is 5 and m is 30 and s is 5