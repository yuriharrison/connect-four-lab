'''Evaluation Neural Network Trainer'''
import os, sys
import time
import random
import numpy as np
from threading import Thread
import keras
from keras import Sequential
from keras.layers import Dense, Dropout, Activation
from .. import RunGame
from ..agents import AgentRandom
from ..agents.mcstnn import AgentMCSTNN


model_key = AgentMCSTNN.model_key
kwargs = None
kill_training = False

board_size = 49
quantity_games = 1000
time_limit = None
report_frequency = .1

model = None
model_name = None
load_model = None
model_file = None
weight_file = None
batch_size = 64
num_epochs = 1
verbose = 0
data_memory = list()


__DIR__ = os.path.dirname(__file__)
__MODEL_DIR__ = os.path.join(__DIR__, '..\\models')


def set_attr(log):
    global quantity_games, time_limit, \
        load_model, model_name, model_file, weight_file, model
    
    if kwargs and len(kwargs) > 0:
        log('Setting variables: {}'.format(kwargs))

    for kw, value in kwargs.items():
        if kw == 'quantity_games':
            quantity_games = eval(value)
        elif kw == 'time_limit':
            time_limit = eval(value)
        elif kw == 'load_model':
            load_model = value
        elif kw == 'model_name':
            value = value.replace('\'', '').replace('\"', '')
            model_name = str(value)
        else:
            log('Invalid keyword: {}'.format(kw))

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
                      optimizer='adam')
                    #   metrics=["accuracy"])

        return model


def save_model(log):
    log('Saving model...')
    np.save(weight_file, data_memory)
    model.save(model_file)
    log('Model saved.')


def set_model(log):
    global model, data_memory
    if load_model:
        model = keras.models.load_model(model_file)
        data_memory = np.load(weight_file).tolist()
        log('Model loaded!')
    else:
        model = create_model()
        log('Model Created!')


def controller():
    count = 0
    report = False
    if time_limit:
        cicle_count = 1
        quantity_cicle = int(time_limit * report_frequency)
        time_start = time.time()

        while (time.time() - time_start) < time_limit:
            current_time = (time.time() - time_start)

            if current_time/quantity_cicle > cicle_count:
                div, mod = divmod(current_time,quantity_cicle)
                if mod: div += 1
                report = div*report_frequency*100
                report = int(report)
                cicle_count += 1
            else:
                report = False

            yield count, report
            count += 1
    else:
        quantity_cicle = int(quantity_games * report_frequency)
        for i in range(quantity_games):
            if (i % quantity_cicle) == 0:
                div, mod = divmod(i,quantity_cicle)
                if mod: div += 1
                report = div*report_frequency*100
                report = int(report)
            else:
                report = False

            yield i, report


def play(episode):
    def kill_game(game):
        while game.is_running or game.status == None:
            if kill_training:
                game.kill()
                break
            else:
                time.sleep(.4)

    if episode < 50 and not load_model:
        p_one = AgentRandom
        p_two = AgentRandom
    else:
        p_one = AgentMCSTNN(model=model)
        p_two = AgentMCSTNN(model=model)

    game = RunGame(p_one, p_two, first_player_randomized=False, start=False)
    thread = Thread(target=kill_game, args=(game,))
    thread.start()
    game.start()


    if game.status == game.GameStatus.exception:
        raise game.exception

    return game


def new_data(game):
    data_in, data_out = [], []
    
    for _, p in game.players.items():
        reward = 0
        if game.winner:
            reward = 1 if p.id != game.winner.id else -1

        scenario = []
        for item in p.data_scenario:
            reshaped = list(np.array(item).reshape(-1))
            reshaped.append(p.id)
            scenario.append(reshaped)
        
        data_in += scenario
        data_out += [reward for _ in scenario]

    for i, j in zip(data_in, data_out):
        data_memory.append([i,j])


def train():
    if len(data_memory) < batch_size:
        return
    
    sample = random.sample(data_memory, batch_size)
    data_in = np.array([item[0] for item in sample])
    data_out = np.array([item[1] for item in sample])
    model.fit(data_in, data_out, epochs=num_epochs, verbose=verbose)


def training_loop(log):
    log('Starting training loop...')
    for episode, report in controller():
        if kill_training: break

        if report:
            log('Completed: {}% - Loop episode: {}'.format(report, episode))

        game = play(episode)
        new_data(game)
        train()


def start(log):
    log('Starting traning')
    set_attr(log)
    set_model(log)
    training_loop(log)

    if kill_training:
        log('Training interrupted! Progress lost.')
    else:
        save_model(log)

    return model