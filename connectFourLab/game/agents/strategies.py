import math
import random
import numpy as np
from copy import copy, deepcopy
from ..timer import Timer
from ..helpers import check_winner, available_positions, next_position


class Strategy:
    pass

class RandomStrategy(Strategy):
    
    def random_choice(self, board):
        columns_available = []

        for column, _ in available_positions(board):
            columns_available.append(column)

        if len(columns_available) == 0:
            return None
        
        rand = random.randint(0, len(columns_available) - 1)
        return columns_available[rand]


class TreeSearchStrategy(Strategy):
    zobrist_table = []
    z_t_color = []
    _search_memory = {}

    def negamax(self, node, depth, color):
        value_stored, update = self.stored_value(node, depth, color)

        if value_stored:
            return value_stored

        if not update and check_winner(node):
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
        childs = []

        for column, row in available_positions(node):
            node[column,row] = color
            childs.append([column, deepcopy(node)])
            node[column,row] = 0

        return childs

    def stored_value(self, board, depth, color):
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
            
    def init_zobrist(self):
        table = np.zeros((49,2),)

        for i, _ in enumerate(table):
            for j, _ in enumerate(_):
                table[i][j] = self.next_random64()

        TreeSearchStrategy.zobrist_table = table
        TreeSearchStrategy.z_t_color = [self.next_random64(),self.next_random64()]

    def next_random64(self):
        num = 10**60
        return random.randint(0, num)

    def hash(self, board, color):
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


class SimulationStrategy(RandomStrategy):

    def simulate(self, board, color=-1):
        winner = check_winner(board)
        if winner:
            return winner

        sim_board = copy(board)
        end = False

        while not end:
            column = self.random_choice(sim_board)

            if column == None: #no options left = tie
                break

            next_pos = next_position(sim_board, column)
            sim_board[column, next_pos] = color
            color = 1 if color == -1 else -1

            winner = check_winner(sim_board)
            if winner:
                return winner

        return 0


class TimerStrategy(Strategy):
    clock = None
    clock_management = True

    def start_timer(self, rule, max):
        self.time_out = False
        time_to_spend = None

        if self.clock:
            time_left = self.clock.time_left
            time_to_spend = rule(time_left)
            time_to_spend = time_to_spend if time_to_spend < max else max
        else:
            time_to_spend = max

        self.timer_thread = Timer(time_to_spend, self.time_out_callback)
        self.timer_thread.start()

    def time_out_callback(self):
        self.time_out = True