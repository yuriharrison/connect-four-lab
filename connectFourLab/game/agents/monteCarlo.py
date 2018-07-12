import time
import math
import numpy as np
from multiprocessing import Process
from threading import Thread
import random
from copy import copy, deepcopy
from .. import helpers
from .basicAgents import AgentBase, AgentRandom
from .strategies import SimulationStrategy, TreeSearchStrategy, TimerStrategy


class AgentSimulation(AgentBase, SimulationStrategy):
    name = 'Simulation'
    description = 'Simple simulation strategy (100 games per possibility)'
    kind = 'simulation'
    num_simulations = 100
    childs = TreeSearchStrategy.childs

    def action(self, board):
        self._switch_ids(board)

        best_position = None
        best_value = -math.inf

        nodes = self.childs(board)

        if(len(nodes) == 1):
            self._save(board, nodes[0][0])
            return nodes[0][0]

        for position, node in nodes:
            value = 0
            
            for _ in range(self.num_simulations):
                value += self.simulate(node)

            if value > best_value:
                best_value = value
                best_position = position
        
        self._save(board, best_position)
        return best_position


class AgentSimulationTL(AgentBase, SimulationStrategy, TimerStrategy):
    name = 'Simulation TL'
    description = 'Simple simulation strategy (simulates with time limit)'
    kind = 'simulation'
    clock_management = True
    childs = TreeSearchStrategy.childs

    def action(self, board):
        self._switch_ids(board)
        # Thread(target=self._run_simulations, args=(board,)).start()

        rule = lambda time_left: time_left/(42-self.turn)
        self.start_timer(rule, max=20)

        self.best_position = None
        self._run_simulations(board)
        
        if not self.best_position:
            self.best_position = self.random_choice(board)

        self._save(board, self.best_position)
        return self.best_position

    def _run_simulations(self, board):
        best_value = -math.inf
        nodes = self.childs(board)

        if(len(nodes) == 1):
            self._save(board, nodes[0][0])
            return nodes[0][0]

        finish = False
        count = 0
        results = np.zeros(len(nodes), dtype=int)
        while not self.time_out and not finish:
            if count > 999: break
            count += 1
            
            for i, item in enumerate(nodes):
                position, node = item
                results[i] += self.simulate(node)

                if count > 99 and results[i] > 99:
                    finish = True

                if results[i] > best_value:
                    best_value = results[i]
                    self.best_position = position


        print('num. simulations:', count, '-- position ratio:', best_value/count)


class AgentMonteCarlo(AgentBase, TimerStrategy):
    name = 'Monte Carlo'
    description = 'Monte carlo search tree strategy'
    kind = 'monte carlo'
    _memory = {}

    def action(self, board):
        self._switch_ids(board)

        rule = lambda time_left: time_left/(42-self.turn)
        self.start_timer(rule, max=20)
        self.start_search(board)

        self._save(board, self.best_position)
        return self.best_position

    def start_search(self, board):
        root_node = self.create_root_node(board)
        root_node.init_zobrist()

        while not self.time_out:
            self._explore(root_node)
        
        best_node = sorted(root_node.children(), key=lambda x: x.value, reverse=True)[0]
        # print('Visits:', best_node.visits, 'Value:', best_node.value)
        self.best_position = best_node.position

    def create_root_node(self, board):
        return Node(board, self.memory)

    def _explore(self, node):
        if not node.rollout():
            children = node.children()
            if not children:
                return 0
                
            next_explore = sorted(children, key=lambda x: x.UCB1, reverse=True)[0]
            self._explore(next_explore)


class Node(SimulationStrategy, TreeSearchStrategy):
    num_simulations=100

    def __init__(self, board, memory=None, parent=None, position=None, color=1):
        self.board = board
        self.color = color
        self.position = position
        self.parent = parent
        self.memory = memory if memory is not None else parent.memory
        self.__score = 0
        self._visits = 0
        self._children = None

        if parent:
            self._hash = self._gen_hash()
            self._save()

    @property
    def UCB1(self):
        if self._visits == 0:
            return math.inf

        lnN = math.log1p(self.parent.visits)
        return self.__score/self._visits + 2*math.sqrt(lnN/self._visits)

    @property
    def visits(self):
        return self._visits

    @property
    def value(self):
        if self._visits == 0:
            return 0

        return self.__score/self._visits

    def _save(self):
        self.memory[self._hash] = self

    def rollout_score(self):
        score = 0
        for _ in range(self.num_simulations):
            score += self.simulate(self.board, self.color)
        return score

    def rollout(self):
        if self.parent and self._visits == 0:
            score = self.rollout_score()

            self.add_score(score)
            self.add_visit()
            return True
        else:
            return False

    def add_score(self, value):
        self.__score += value
        if self.parent:
            self.parent.add_score(value)

    def add_visit(self):
        self._visits += 1
        if self.parent:
            self.parent.add_visit()

    def children(self):
        if not self._children:
            childs = []
            board = self.board
            for column, row in helpers.available_positions(board):
                board[column,row] = self.color
                new_board = deepcopy(board) 
                board[column,row] = 0

                node = self._get_memory(new_board, -self.color)
                if not node:
                    node = self.new_node(new_board, column)
                childs.append(node)

            self._children = childs

        return self._children if len(self._children) > 0 else None

    def new_node(self, board, column):
        node_type = type(self)
        node = node_type(board=board, parent=self, position=column, color=-self.color)
        return node

    def _get_memory(self, board, color):
        hash = self.hash(board, color)
        if hash in self.memory:
            return hash
        else:
            return

    def _gen_hash(self):
        self.hash(self.board,self.color)