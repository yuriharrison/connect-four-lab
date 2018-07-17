import math
import random
import numpy as np
from copy import deepcopy
from . import AgentBase
from .strategies import TreeSearchStrategy


class AgentNegamax(AgentBase, TreeSearchStrategy):
    """Negamax Agent
    
    This agent uses the negamax algorithm which is a
    simplified version of the minimax algorithm.

    Negamax is based on the observation that
    `max(a,b) = -min(-a,-b)`

    This agent uses negamax in all actions using the maximum
    depth of `5`.

    It also uses a __zobrist hash table__ to store all searches in order
    to be more efficient.
    """
    name = 'Negamax'
    description = 'Simple Tree Search strategy (negamax 5 level deep)'
    kind = 'tree search'
    search_depth = 5

    def __init__(self):
        super().__init__()
        self.init_zobrist()

    def action(self, board):
        self.switch_ids(board)

        best_value = -math.inf
        best_option = None
        
        nodes = self.childs(board, 1)
        random.shuffle(nodes)
        for position, node in nodes:
            value = -self.negamax(node, self.search_depth, -1)

            if value > best_value:
                best_value = value
                best_option = position

                if value > 0:
                    break

        self.save(board, best_option, best_value)
        return best_option
