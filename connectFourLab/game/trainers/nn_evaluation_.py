import os, sys
import time
import random
import numpy as np
import keras
from keras import Sequential
from keras.layers import Dense, Dropout, Activation
from .. import RunGame
from ..agents import AgentRandom
from ..agents.monteCarlo import Node
from ..agents.mcstnn import AgentMCSTNN

'''     Evaluation Neural Network Trainer    '''

model_key = AgentMCSTNN.model_key
kwargs = None
kill_training = False

board_size = 49
quantity_games = 1000
time_limit = None

model = None
model_name = None
load_model = None
model_file = None
weight_file = None
batch_size = .2
data_memory = list()
data_scenario = list()
data_reward = list()
node_memory = dict()


__DIR__ = os.path.dirname(__file__)
__MODEL_DIR__ = os.path.join(__DIR__, '..\\models')


class TrainingNode(Node):

    def rollout(self):
        if self.parent and self._visits == 0:
            score = self.rollout_score()

            self.add_score(score)
            self.add_visit()

            data_out = int(score/self.num_simulations)
            data_in = list(self.board.reshape(-1))
            data_in.append(self.color)
            data_memory.append([data_in, data_out])

            return True
        else:
            return False


def set_attr(log):
    global quantity_games, time_limit, \
        load_model, model_name, model_file, weight_file, model
    
    for kw, value in kwargs.items():
        if kw == 'quantity_games':
            quantity_games = value
        elif kw == 'time_limit':
            time_limit = value
        elif kw == 'load_model':
            load_model = value
        elif kw == 'model_name':
            model_name = value

    full_name = model_key
    if model_name:
        full_name += '_' + model_name
    full_name += '.h5'
    model_name = full_name

    model_file = os.path.join(__MODEL_DIR__, model_name)
    weight_file = os.path.join(__MODEL_DIR__, model_name.replace('.h5', '.npy'))


def create_model():
        len_in = board_size + 1
        len_out = 1

        model = Sequential()
        model.add(Dense(256, input_dim=len_in, activation='relu'))
        model.add(Dropout(0.1))
        model.add(Dense(256, activation='relu'))
        model.add(Dropout(0.1))
        model.add(Dense(len_out, activation='linear'))

        model.compile(loss='mean_absolute_error',
                      optimizer='adam',
                      metrics=["accuracy"])

        return model


def save_model(log):
    log.print('Saving model...')
    model.save(model_file)
    # np.save(weight_file, data_memory)
    log.print('Model saved.')


def set_model(log):
    global model, data_memory
    if load_model:
        model = keras.models.load_model(model_file)
        # data_memory = np.load(weight_file).tolist()
    else:
        model = create_model()


def controller():
    count = 0
    if time_limit:
        time_start = time.time()
        while (time.time() - time_start) < time_limit:
            count += 1
            yield count
    else:
        for _ in range(quantity_games):
            count += 1
            yield count


def train(log):
    batch_size_normalized = int(len(data_memory)*batch_size)
    sample = random.sample(data_memory, batch_size_normalized)
    data_in = np.array([item[0] for item in sample])
    data_out = np.array([item[1] for item in sample])
    model.fit(data_in, data_out, epochs=10, verbose=1)

    
def practice_loop(log):
    root_node = None
    board = np.zeros((7,7))
    split = 10**5
    for visit in controller():
        if visit is 1 or (visit % split) is 0:
            log.print('New session - Total visits: {}'.format(visit))
            root_node = TrainingNode(board, node_memory)
            root_node.init_zobrist()

        explore_node(root_node)


def explore_node(node):
    if not node.rollout():
        children = node.children()
        if not children:
            return 0
            
        next_explore = sorted(children, key=lambda x: x.UCB1, reverse=True)[0]
        explore_node(next_explore)


def start(log):
    set_attr(log)
    set_model(log)
    practice_loop(log)
    train(log)

    if kill_training:
        log.print('Training interrupted! Progress lost.')
    else:
        save_model(log)

    return model