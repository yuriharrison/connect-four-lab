import time
import math
import numpy as np
from multiprocessing import Process
from threading import Thread
import random
from copy import copy, deepcopy
from .. import helpers
from . import AgentBase
from .strategies import SimulationStrategy, TreeSearchStrategy, TimerStrategy, Node


class AgentSimulation(AgentBase, SimulationStrategy):
    """Simulation agent
    
    When taking an action this agent simulates a number of
    games for each available column and then choose the 
    best probabilistic option.

    The best probabilistic option is the best score of a column,
    in a 100 simulated games.

    Each simulation consists in simulate every turn randomly for
    both players until the simulation ends in a terminal state.
    Then it will return `1` for victory, `-1` for defeat or `0`
    in case of a draw.
    """
    name = 'Simulation'
    description = 'Simple simulation strategy (100 games per possibility)'
    kind = 'simulation'
    num_simulations = 100
    childs = TreeSearchStrategy.childs

    def action(self, board):
        self.switch_ids(board)

        best_position = None
        best_value = -math.inf

        nodes = self.childs(board)

        if(len(nodes) == 1):
            self.save(board, nodes[0][0])
            return nodes[0][0]

        for position, node in nodes:
            value = 0
            
            for _ in range(self.num_simulations):
                value += self.simulate(node)

            if value > best_value:
                best_value = value
                best_position = position
        
        self.save(board, best_position)
        return best_position


class AgentSimulationTL(AgentBase, SimulationStrategy, TimerStrategy):
    """Simulation strategy with time management

    This agent act by simulating a number of
    games for each available column and then choosing the 
    best probabilistic option.

    Similar with the `AgentSimulation`. Differentiating
    itself by instead of simulating a fixed number of games,
    this agent manage the time available through the game,
    simulating the maximum amount of games (equaly distributed
    to all possible columns) without letting the time run out
    and thus being able to handle limited time games.

    In unlimited time games the agents takes the maximum of
    20 seconds per turn before returning the choice.
    """
    name = 'Simulation TL'
    description = 'Simple simulation strategy (simulates managing the time limit)'
    kind = 'simulation'
    clock_management = True
    childs = TreeSearchStrategy.childs

    def action(self, board):
        self.switch_ids(board)

        rule = lambda time_left: time_left/(25-self.turn)
        self.start_timer(rule, max=20)

        self.best_position = None
        self.run_simulations(board)
        
        if not self.best_position:
            self.best_position = self.random_choice(board)

        self.save(board, self.best_position)
        return self.best_position

    def run_simulations(self, board):
        best_value = -math.inf
        nodes = self.childs(board)

        if(len(nodes) == 1):
            self.save(board, nodes[0][0])
            return nodes[0][0]

        count = 0
        results = np.zeros(len(nodes), dtype=int)
        while not self.time_out:
            if count > 999: break
            count += 1

            if count == 1:
                for position, node in nodes:
                    winner = helpers.check_winner(node)
                    if winner:
                        self.best_position = position
                        return
            
            for i, (position, node) in enumerate(nodes):
                results[i] += self.simulate(node)

                if results[i] > best_value:
                    best_value = results[i]
                    self.best_position = position

        print('num. simulations:', count, '-- position ratio:', best_value/count)


class AgentMonteCarlo(AgentBase, TimerStrategy):
    """Monte Carlo agent.

    This agent applies the Monte Carlo Tree Search method.
    The method consists in search the possibilities of
    the board evaluating each stage of the board (rollout), but
    different from a minimax tree search this search
    don't go into all the possibilities, it uses the
    UCB1 algorithm to measure how much of the search effort
    goes into exploiting promissing branches and exploring
    less prommissing branches.

    This agent evaluate the rollout with a simulation
    of 100 games per board state.
    """
    name = 'Monte Carlo'
    description = 'Monte carlo search tree strategy'
    kind = 'monte carlo'
    _memory = {}

    def action(self, board):
        self.switch_ids(board)

        rule = lambda time_left: time_left/(42 - self.turn)
        self.start_timer(rule, max=20)
        self.start_search(board)

        self.save(board, self.best_position)
        return self.best_position

    def start_search(self, board):
        root_node = self.create_root_node(board)

        while not self.time_out:
            self._explore(root_node)
        
        best_node = sorted(root_node.children(), key=lambda x: x.value, reverse=True)[0]
        # print('Visits:', best_node.visits, 'Value:', best_node.value)
        self.best_position = best_node.position

    def create_root_node(self, board):
        return NodeMCTS(board, self._memory)

    def _explore(self, node):
        if not node.rollout():
            children = node.children()
            if not children:
                return 0
                
            next_explore = sorted(children, key=lambda x: x.UCB1, reverse=True)[0]
            self._explore(next_explore)


class NodeMCTS(Node):
    num_simulations=100

    def rollout_score(self):
        score = 0
        for _ in range(self.num_simulations):
            score += self.simulate(self.board, self.color)
        return score/self.num_simulations