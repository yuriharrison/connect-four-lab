"""Monte Carlo strategies"""
import math
from copy import copy, deepcopy
from . import Strategy, RandomStrategy, ZobristHashingStrategy
from . import RandomStrategy
from ... import helpers
from ...exceptions import BadImplementation


class SimulationStrategy(RandomStrategy):
    """Simulation Stragegy provide the method necessary
    to simulate matches."""

    def simulate(self, board, color=-1):
        """Simulate a match to the end from a given
        board state. All turns are played randomly till
        the board hits a terminal state then the value is
        returned.

        # Arguments
            board: matrix, required, board state to be simulated
            color: int, required, id of the owner of the board state

        # Return
            Id of the winner of the simulation or zero in case
            the simulation ends in a draw.

        # Example
            AgentSimulation: [documentation](./agents#agentsimulation)
        """
        winner = helpers.check_winner(board)
        if winner:
            return winner

        sim_board = copy(board)
        end = False

        while not end:
            column = self.random_choice(sim_board)

            if column == None: #no options left = tie
                break

            next_pos = helpers.next_position(sim_board, column)
            sim_board[column, next_pos] = color
            color = 1 if color == -1 else -1

            winner = helpers.check_winner(sim_board)
            if winner:
                return winner

        return 0


class DepthMeasure:
    """Use this class to help when measuring the depth of a
    tree search. Useful when debugging and measuring performance
    optimization.
    
    # Example

    ```
    class AgentNew(AgentBase, TimerStrategy):
        
        def action(self, board):
            DepthMeasure.start()
            self.start_timer(...)

            while not self.time_out:
                # place the line "DepthMeasure.add()" inside the
                # search method, when it creates a new depth
                self.run_search()
                DepthMeasure.reset()

            DepthMeasure.print()

            return ...
    ```
    """
    current_depth = 0
    deepiest = 0

    @staticmethod
    def start():
        """Reset all the variables to begin a new measurement."""
        DepthMeasure.current_depth = 0
        DepthMeasure.deepiest = 0

    @staticmethod
    def add():
        """Add more 1 depth."""
        DepthMeasure.current_depth += 1

    @staticmethod
    def reset():
        """Reset the depth before start a new search episode. Save the
        current depth if it's the deepiest till know.
        """
        if DepthMeasure.current_depth > DepthMeasure.deepiest:
            DepthMeasure.deepiest = DepthMeasure.current_depth
        DepthMeasure.current_depth = 0

    @staticmethod
    def print():
        """Print the deepiest depth reached."""
        print('Last play depth:', DepthMeasure.deepiest)


class Node(SimulationStrategy, ZobristHashingStrategy):
    """Node class is a base for a complex node for a Monte Carlo
    Tree Searches.
    
    This class has specific methods to perform the Monte Carlo Tree
    Search.

    This class __don't work on its own__, because it doesn't have a
    default board evaluation algorithm. When inherited it's required
    to implement the `rollout_score` method which is an evaluation
    of a given state.

    This class uses a __zobrist hashing table__ to optimize the search.

    # Arguments
        board: matrix, required, board state
        memory: empty dictionary, required(*), default None
            - this dictionary will store all searches
                with zobrist hashing.
        parent: `Node` object, required (**), default None
            - Node above in the tree hierarchy.
        position: int, required (**), default None
            - Index of the column which generated the board
                current `board`.
        color: int, required (**), default 1

    (*) required when creating a new root `Node` object.
    
    (**) required when creating a new "children"
    `Node` object (`new_node` method).

    # Properties
        UCB1: float, UCB1 value (*) of the node.
        visits: int, total number of Node visits
        value: float, total number of score divided by the
            number of visits
            - the total number of score is the sum of all
                scores made by the Node and his children.

    (*) UBC1 is an algorithm which calculates the distribution
    of search effort for exploration and exploitation in
    the Monte Carlo Tree Search strategy.
    
    # Example
        AgentMonteCarlo: [documentation](./agents#agentsimulation)
        AgentMCTSNN: [documentation](./agents#agentmctsnn)
    """
    
    def __init__(self, board, memory=None, parent=None, position=None, color=1):
        self.board = board
        self.color = color
        self.position = position
        self.parent = parent
        self.memory = memory if memory is not None else parent.memory
        self.__score = 0
        self._visits = 0
        self._children = None
        super().__init__()

        if parent:
            self._hash = self._gen_hash()
            self._save()

    def __init_subclass__(cls):
        if 'rollout_score' not in cls.__dict__:
            raise BadImplementation(cls.__name__, 'rollout_score')

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
        """This method must return a score (float), evaluation, 
        for the Node board state (`self.board`), from the 
        perspective of the player id 1.
        
        This method is called every rollout. The rollout occur
        in the first visit of the Node, the value is stored in
        the zobrist table and it is __not__ recalculated during the match.

        # Return
            float, score of the Node `board`
        """
        pass

    def rollout(self):
        """Node rollout.

        It will execute a rollout if this is the first
        visits of the Node, otherwise it will return `False`.

        Each rollout adds a visit in the counter and the score
        of the `board` to the Node and all the parents above
        in the tree.

        # Return
            `True` when the rollout occur, `False` when it do not.
        """
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
        """Get all the childen Nodes.

        Generate or get from the memory, all the childen
        Nodes. Each node is generated from the available
        possitions in the `board` of the current Node.
        """
        # DepthMeasure.add()
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
        """This method is called by `children` method to
        generate a new Node.
        
        # Arguments:
            board: matrix, new board state
            column: int, index of the last column

        # Return
            A new instance of `Node` object.
        """
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
        self.hash(self.board, self.color)