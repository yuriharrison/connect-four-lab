"""Tree search strategies"""
import math
import numpy as np
import random
from copy import deepcopy
from . import Strategy
from ... import helpers


class ZobristHashingStrategy(Strategy):
    """Zobrist hashing table strategy provid an
    easy way to implement a hash table using the a board
    state to crate the hash. Useful to store the data in
    a tree search.
    
    # Examples
        TreeSearchStrategy: [documentation](#treesearchstrategy)
        Node: [documentation](#node)
    """
    zobrist_table = []
    z_t_color = []

    def __init__(self):
        ZobristHashingStrategy.init_zobrist()
        super().__init__()

    @staticmethod
    def init_zobrist():
        """Initialize Zobrist hashing table.
        
        This method creates a list of two tables, filled
        randomly with int64 numbers, to represent
        all possitions in a 7x7 board, one table for each
        player. It also generate two random int64 numbers
        which will represent the owner of a board state.

        Both lists are used when generating a hash in the
        `hash` method.
        """
        if len(ZobristHashingStrategy.zobrist_table):
            return

        table = np.zeros((49,2),)

        for i, _ in enumerate(table):
            for j, _ in enumerate(_):
                table[i][j] = ZobristHashingStrategy.next_random64()

        ZobristHashingStrategy.zobrist_table = table
        ZobristHashingStrategy.z_t_color = [ZobristHashingStrategy.next_random64(),
                                            ZobristHashingStrategy.next_random64()]

    @staticmethod
    def next_random64():
        """Return a random int64 number"""
        num = int(1E63)
        return random.randint(0, num)

    def hash(self, board, color):
        """Create a __zobrist hash__ for a given board state.
        
        # Arguments:
            board: matrix, required, board state
            color: int (1 or -1), required, owner of 
                the board state.

        # Return:
            Generated zobrist hash.
        """
        hash = 0
        for i, value in enumerate(board.reshape(-1)):
            if value == 1:
                hash ^= int(self.zobrist_table[i][0])
            elif value == -1:
                hash ^= int(self.zobrist_table[i][1])

        if color == 1:
            hash ^= self.z_t_color[0]
        else: #equal -1
            hash ^= self.z_t_color[1]

        return hash


class TreeSearchStrategy(ZobristHashingStrategy):
    """Tree Search Strategy provide the necessary methods
    to an agent make a tree search in a given board state.
    
    # Example
        AgentNegamax: [documentation](./agents#agentnegamax)
    """
    _search_memory = {}

    def negamax(self, node, depth, color):
        """__Negamax algorithm__

        This algorithm, in order to be more efficiente, 
        also uses a __Zobrist hashing table__ to store
        the values of board states and avoid duplicated
        searches in equal board states in the same depth.
        
        # Arguments
            node: matrix, required, board state
            depth: int, required, number which controls the
                depth limit that the recursive calls should hit
            color: int (1 or -1), required, owner of the board state

        # Return
            Best value of a `node`
        """
        value_stored, update = self.stored_value(node, depth, color)

        if value_stored:
            return value_stored

        if not update and helpers.check_winner(node):
            return -1
        elif depth < 1:
            return 0
        
        childs = self.childs(node, color)
        if len(childs) < 1:
            return 0
            
        best_value = -math.inf
        for _, child_node in childs:
            value = -self.negamax(child_node, depth-1, -color)

            if value > best_value:
                best_value = value

                if value > 0:
                    break

        self.save_search(node, best_value, depth, color)

        return best_value

    def childs(self, node, color=1):
        """Create an return the children of a given `node`.

        The children are generated from all available
        positions in a given `board`

        # Arguments
            node: matrix, required, board state
            color: int (1 or -1), optional, default 1
                owner of the board state

        # Return
            List of children. Each item = (column, new_board_state)
        """
        childs = []

        for column, row in helpers.available_positions(node):
            node[column,row] = color
            childs.append([column, deepcopy(node)])
            node[column,row] = 0

        return childs

    def stored_value(self, board, depth, color):
        """Get the stored value of a board state.

        Search in the hash table if the is already a value
        stored for the `board` and return the value if there is
        one and if it's necessary to update the value.

        The search is made on a __Zobrist hashing table__.

        It will require an update in the value stored when
        the stored value depth is inferior to
        the current search depth.

        # Arguments
            board: matrix, required, board state
            depth: int, required, current search depth
            color: int (1 or -1), owner of the board state

        # Return
            value: int, value of the given board if it finds one
            update: boolean, `True` when the value stored needs to
                be updated.
        """
        hash = self.hash(board, color)
        
        value = None
        update = False
        if hash in self._search_memory:
            memory = self._search_memory[hash]

            if np.all(memory['board'] != board):
                error_msg = 'Diferente boards with the same hash!'
                error_msg += '\nBoard stored: {}'.format(memory['board'])
                error_msg += '\nCurrent board: {}'.format(board)
                error_msg += '\nHash: {}'.format(hash)
                raise ValueError(error_msg)
            elif memory['depth'] < depth:
                update = True
            else:
                value = memory['value']

        return value, update

    def save_search(self, board, value, depth, color):
        """Save the data of a search in a __zobrist hashing table__.
        
        # Arguments:
            board: matrix, required, board state
            value: int, value of the board state
            depth: int, current depth of the search
            color: int (1 or -1), owner of the board state
        """
        hash = self.hash(board, color)
        
        if hash not in self._search_memory:
            self._search_memory[hash] = {'board': board, 
                                        'value': value, 
                                        'depth': depth}
                                        
        elif self._search_memory[hash]['depth'] < depth:
            self._search_memory[hash]['value'] = value
            self._search_memory[hash]['depth'] = depth
        else:
            return False
    
