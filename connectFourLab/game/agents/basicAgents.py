import time
import random
from copy import deepcopy


class BadImplementation(Exception):

    def __init__(self, cls_name, method_name):
        msg = 'Bad implementation: Class {} needs to implement action method.'
        msg = msg.format(cls_name, method_name)
        super().__init__(msg)


class AgentBase:
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

    def __init_subclass__(cls):
        if 'action' not in cls.__dict__:
            raise BadImplementation(cls.__name__, 'action')

    def update_clock(self, turn, timer):
        if self.clock_management:
            self.turn = turn
            self.clock = timer

    def clean(self):
        self.data_action = []
        self.data_scenario = []
        self.data_reward = []

    def _save(self, board, choice, reward=0):
        self.data_scenario.append(deepcopy(board))
        self.data_action.append(choice)
        self.data_reward.append(reward)

    def _switch_ids(self, board):
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
    name = 'Human'
    description = 'Get the user input'

    def __init__(self):
        super().__init__()
        self.column_choosed = None
        self.get_input = lambda agent, board: None

    def action(self, board):
        self.column_choosed = None

        self.get_input(self, board)

        while self.column_choosed is None:
            time.sleep(0.1)

        self._save(board, self.column_choosed)
        return self.column_choosed


class AgentRandom(AgentBase):
    name = 'Random'
    description = 'Agent make only pseudo random choices'
    kind = 'randomic'

    def __init__(self):
        super().__init__()

    def action(self, board):
        self._switch_ids(board)
        choice = self.random_choice(board)
        self._save(board, choice)
        return choice

    def random_choice(self, board):
        columns_available = []
        
        for column, _ in enumerate(board):
            for _, value in enumerate(_):
                if value == 0:
                    columns_available.append(column)
                    break
        
        rand = random.randint(0, len(columns_available) - 1)
        choice = columns_available[rand]
        return choice
