import math
import random
import numpy as np
from copy import deepcopy
from .basicAgents import AgentBase
from .strategies import TreeSearchStrategy


class AgentNegamax(AgentBase, TreeSearchStrategy):
    name = 'Negamax'
    description = 'Simple Three Search strategy (negamax 5 level deep)'
    kind = 'three search'
    search_depth = 5

    def __init__(self):
        super().__init__()
        self.init_zobrist()

    def action(self, board):
        self._switch_ids(board)

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

        self._save(board, best_option, best_value)
        return best_option
