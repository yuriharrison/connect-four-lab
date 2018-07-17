"""Basic Agents"""
import time
import random
from copy import deepcopy
from .strategies import RandomStrategy
from ..exceptions import BadImplementation


class AgentBase:
    """Base class Agent

    To inherit from this class it's required to implement
    the `action` method

    ```python
    def action(self, board):
        # choose a column based in a given board
        return chosen_column # 0-6
    ```

    # Attributes
        name: str, required, name of the agent
        description: str, required, description of the agent
        kind: str, required, category of the agent
        model_key: str, required for agents who uses
            neural network models
        clock_management: bool, optional, default `False` (*)
            - flag that indicates whether or not the agent 
                can manage a time limit game
        require_nn_model: bool, optional, default `False` (*)
            - flag that indicates whether or not the agent
                needs a neural network model
        
        (*) - only necessary in the `app` interface

    # Saving the data
        You can easily save the data from all turns of the game
        using `save` all data will be saved separately in:
        
        data_scenario: state of the board
        data_action: taken action
        data_reward: attributed reward

    ```python
    def action(self, board):
        choice = self.random_choice(board)
        self.save(board, choice)
        return choice
    ```
    # Exception
        BadImplementation: some class didn't implemented the
            required method(s)

    ### Clock management
        If the game is time limeted the `update_clock` will be
        called every turn and you will be able to manage the
        `Timer` (see [Timer](../Game/timer)) in `self.clock`.

    ### Using Neural Networks
        To use neural network you need a [Trainer](./trainers)
        which have to create and train a model for the agent.
        
    # Example
        MCTSNN: Monte Carlo Tree Search with Neural Network implementation -
            see [documentation](./agents#MCTSNN)

    """
    name = 'Agent name'
    description = 'Agent Description'
    kind = 'Agent Kind'
    model_key = None
    clock_management = False
    require_nn_model = False

    def __init__(self):
        self.id = None
        self.char = str()
        self.data_scenario = []
        self.data_action = []
        self.data_reward = []
        self.clock = None
        super().__init__()

    def __init_subclass__(cls):
        if 'action' not in cls.__dict__:
            raise BadImplementation(cls.__name__, 'action')

    def update_clock(self, turn, timer):
        """Update every turn if the game is time limited
        
        # Arguments
            turn: int, turn number
            timer: `Timer` object
        """
        if self.clock_management:
            self.turn = turn
            self.clock = timer

    def clean(self):
        """Clean all the saved data"""
        self.data_action = []
        self.data_scenario = []
        self.data_reward = []

    def save(self, board, column, reward=0):
        """Save the data of a played turn
        
        # Arguments
            board: matrix, required, current board
            column: int 0-6, required, chosen column
            reward: float, optional
                - attributed reward for the chosen column
        """
        self.data_scenario.append(deepcopy(board))
        self.data_action.append(column)
        self.data_reward.append(reward)

    def switch_ids(self, board):
        """Switch the player's id IN THE BOARD to 1
        
        If this agent id is -1, it will modify the board
        and change de player's id to 1, the enemy id will be
        changed to -1.

        Useful to save the data in a pattern. Example, when
        running two agents against each other, the agents
        will have a diferent id (1 and -1), but the saved
        data will represent a single agents id 1

        Also, applying this method before the logic, your code
        can always treat your id as 1 when analysing the board

        ```python
        def action(self, board):
            self.switch_ids(board)
            # analyse the board and make a choice...
            self.save(board, choice)
            return choice
        ```
        """
        if self.id == -1:
            for i, _ in enumerate(board):
                for j, id in enumerate(_):
                    if id == 1:
                        board[i,j] = 3
                    elif id == -1:
                        board[i,j] = 1
                        
            for i, _ in enumerate(board):
                for j, id in enumerate(_):
                    if id == 3:
                        board[i,j] = -1


class AgentHuman(AgentBase):
    """Human Agent represents the user as a player

    When a UI implements `RunGame` it will
    assign a function to `get_input` which will be
    called each turn. The function should return 
    the column choosed by the user.
    """
    name = 'Human'
    description = 'Get the user input'

    def __init__(self):
        super().__init__()
        self.get_input = lambda agent, board: None

    def action(self, board):
        column_choosed = self.get_input(self, board)
        self.save(board, column_choosed)
        return column_choosed


class AgentRandom(AgentBase, RandomStrategy):
    """Random agent, play a valid column chosen randonly"""
    name = 'Random'
    description = 'Agent make only pseudo random choices'
    kind = 'randomic'

    def __init__(self):
        super().__init__()

    def action(self, board):
        self.switch_ids(board)
        choice = self.random_choice(board)
        self.save(board, choice)
        return choice
