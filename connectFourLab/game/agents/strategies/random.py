import random
from . import Strategy
from ... import helpers


class RandomStrategy(Strategy):
    """Random strategy"""
    
    def random_choice(self, board):
        """Random choice. Return a valid column from a given
        board state.
        """
        columns_available = []
        for column, _ in helpers.available_positions(board):
            columns_available.append(column)

        if len(columns_available) == 0:
            return None
        
        return random.choice(columns_available)