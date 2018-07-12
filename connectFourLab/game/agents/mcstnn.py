import numpy as np
from .monteCarlo import AgentMonteCarlo, Node
from .. import helpers

'''
    MONTE CARLO SEARCH THREE WITH NERONAL NETWORK EVALUATION
'''

class AgentMCSTNN(AgentMonteCarlo):
    name = 'MCSTNN'
    description = 'Monte Carlo strategy with evaluation based on a neural network'
    kind = 'Agent Kind'
    model_key = 'MCSTNN'
    require_nn_model = True

    def __init__(self, model_file=None, model=None):
        super().__init__()
        
        self.model = None
        self.graph=None

        if model:
            self.model = model
        elif model_file:
            import keras
            import tensorflow as tf
            model = keras.models.load_model(model_file)
            self.model = model
            self.graph = tf.get_default_graph()
        

    def action(self, board):
        if not self.graph:
            return super().action(board)
        else:
            with self.graph.as_default():
                return super().action(board)
        

    def create_root_node(self, board):
        return NodeMCSTNN(self.model, board, self.memory)

    def start_timer(self, rule, max):
        super().start_timer(rule, 20)


class NodeMCSTNN(Node):

    def __init__(self, model, *a, **kw):
        super().__init__(*a, **kw)
        self.model = model

    def new_node(self, board, column):
        node = NodeMCSTNN(model=self.model, 
                    board=board, 
                    parent=self, 
                    position=column, 
                    color=-self.color)
        return node

    def rollout_score(self):
        winner = helpers.check_winner(self.board)
        if winner:
            return winner

        data_in = list(self.board.reshape(-1))
        data_in.append(self.color)
        board = np.array([data_in])
        evaluation = self.model.predict(board)[0][0]

        # if self.color < 0:
        #     evaluation = -evaluation

        return evaluation
        