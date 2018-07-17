"""MONTE CARLO TREE SEARCH WITH NERONAL NETWORK EVALUATION"""
import numpy as np
from .monteCarlo import AgentMonteCarlo
from .strategies import Node
from .. import helpers
from ..exceptions import MissingModel


class AgentMCTSNN(AgentMonteCarlo):
    """Agent Monte Carlo Tree Search with Neural Network evaluation.
    
    This agent inherit from `AgentMonteCarlo` using the same
    process but evaluating the rollouts by using a trained
    neural network model.

    This agent uses the Node `NodeMCTSNN` which evaluate the rollout
    score by predicting the board state in a trained model.

    # Arguments
        model_file: str; path to the '.h5' model file;
        model: str, loaded `keras.models.Model` object;

    # Exceptions
        MissingModel: raise when creating a new instance, if
            both model_file and model are None.
    """
    name = 'MCTSNN'
    description = 'Monte Carlo strategy with evaluation based on a neural network'
    kind = 'Agent Kind'
    model_key = 'MCTSNN'
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
        else:
            raise MissingModel(AgentMCTSNN.__name__, 'Evaluation model')
        

    def action(self, board):
        if not self.graph:
            return super().action(board)
        else:
            with self.graph.as_default():
                return super().action(board)
        

    def create_root_node(self, board):
        return NodeMCTSNN(self.model, board, self._memory)

    def start_timer(self, rule, max):
        super().start_timer(rule, 20)


class NodeMCTSNN(Node):

    def __init__(self, model, *a, **kw):
        super().__init__(*a, **kw)
        self.model = model

    def new_node(self, board, column):
        node = NodeMCTSNN(model=self.model, 
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
        