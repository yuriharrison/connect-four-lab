import os, sys
import inspect
import json
from importlib import import_module
from kivy.lang import Builder
from ..game.agents import AgentBase, AgentHuman, AgentRandom

__ICON_FILE_NAME__ = 'icon.ico'
__APPLICATION_TITLE__ = 'CONNECT FOUR LAB'
__DEFAULT_SCREEN_SIZE__ = (600, 800)
__GAME_SCREEN_SIZE__ = (800,800)
__AGENTS__ = None
__TRAINERS__ = None
__DIR__ = os.path.dirname(__file__)

_images_dir = 'images'
_screens_dir = 'screens'
_agents_package = 'connectFourLab.game.agents'
_trainer_package = 'connectFourLab.game.trainers'
_agents_dir_relative_path = '../game/agents'
_trainers_dir_relative_path = '../game/trainers'
_models_dir_relative_path = '../game/models'


def get_image_path(value):
    image_dir = os.path.join(__DIR__, _images_dir)
    image_dir = image_dir.replace('\\', '/')
    full_path = str()
    
    atlas_key = 'atlas://'
    if value.startswith(atlas_key):
        value = value.replace(atlas_key, '')
        full_path = atlas_key

    full_path += os.path.join(image_dir, value)
    return full_path


def get_time_options():
    options = [
        ('No Limit', None),
        ('30 seg', 30),
        ('1 min', 1*60),
        ('5 min', 5*60),
        ('10 min', 10*60),
        ('30 min', 30*60)
    ]

    return options


def get_agents():
    if not __AGENTS__:
        load_agents()

    return __AGENTS__


def load_agents():
    global __AGENTS__

    agents_path = os.path.join(__DIR__, _agents_dir_relative_path)
    agents = [AgentHuman,AgentRandom]
    names = [AgentHuman.__name__, AgentRandom.__name__]

    for file_name in os.listdir(agents_path):
        if not file_name.endswith('.py'):
            continue
        elif file_name == 'basicAgents.py' or file_name == '__init__.py':
            continue
        else:
            module_name = file_name[:-3]
        
        absolute_module = _agents_package + '.' + module_name
        module = import_module(absolute_module)

        for name, obj in inspect.getmembers(module):
            if name.startswith('Agent') \
                and name != AgentBase.__name__ \
                and inspect.isclass(obj) \
                and obj.__name__ not in names:

                names.append(obj.__name__)
                agents.append(obj)
    
    __AGENTS__ = agents

def load_trainer_package(module):
    absolute_module = _trainer_package + '.' + module
    module = import_module(absolute_module)
    return module


def get_trainers():
    if not __TRAINERS__:
        load_trainers()

    return __TRAINERS__


def load_trainers():
    global __TRAINERS__

    trainer_dir = os.path.join(__DIR__, _trainers_dir_relative_path)
    py_files, json_list = [], []
    for file_name in os.listdir(trainer_dir):
        file_path = os.path.join(trainer_dir, file_name)
        if file_name.endswith('.py'):
            py_files.append(file_name)

        if file_name.endswith('.json'):
            with open(file_path) as f:
                json_list.append([file_name, json.load(f)])

    trainers = []
    for py_name in py_files:
        module_name = py_name[:-3]
        for json_name, info in json_list:
            if json_name[:-5] == module_name:
                info['module'] = module_name
                trainers.append(info)

    __TRAINERS__ = trainers


def get_trained_models(model_key):
    model_dir = os.path.join(__DIR__, _models_dir_relative_path)
    models = []
    for file_name in os.listdir(model_dir):
        if file_name.startswith(model_key) and file_name.endswith('.h5'):
            file_path = os.path.join(model_dir, file_name)
            models.append([file_name, file_path])

    return models


def load_all_kivy_files():
    screens_path = os.path.join(__DIR__, _screens_dir)
    kivy_files = _find_kivy_files(screens_path, [])

    for file in kivy_files:
        Builder.load_file(file)


def _find_kivy_files(directory, kivy_files):
    for item in os.listdir(directory):
        if os.path.isfile(item):
            new_directory = os.path.join(directory, item)
            _find_kivy_files(new_directory, kivy_files)
        elif item.endswith('.kv'):
            file = os.path.join(directory, item)
            kivy_files.append(file)

    return kivy_files
            

def get_application_title():
    return __APPLICATION_TITLE__


def get_icon():
    return get_image_path(__ICON_FILE_NAME__)

def get_default_screen_size():
    return __DEFAULT_SCREEN_SIZE__

def get_game_screen_size():
    return __GAME_SCREEN_SIZE__