# Trainers

Trainers are responsable for create and train a neural network model to be used by an Agent. 

Trainers only appear on the App Training Config Screen if there are a description file in json format, along with the trainer module inside the `game/trainers/` directory. The description file should be named the same as the module file.

The trained models have to be stored on `game/models/` folder, if not, the APP won't be able to detect it. Also the name of the trained model have to start with the Agent `model_key` defined on the Agent class.

__Directory structure__

    game/
        trainers/
            new_trainer.py
            new_trainer.json
        models/
            model_name.h5

__JSON File example__

```json
{
    "name": "Name of the trainer",
    "short_description": "short description",
    "description": "full description"
}
```

### APP Requirements

To work properly with the app the trainer must implement a function named `start` which will receive as argument a function `log`. The log function receive as argument a string which will be shown on the log screen in the app.

It's also required to implement the variables:
- `kwargs` - dictionary, all kwargs informed by the user in the "Variables" on the Training Config Screen.
- `kill_training` - boolean, flag setted to True when the user press the "Cancel" button on the Training Screen.

__Example__

```python
kwargs = None
kill_training = False

def start(log):
    log('Starting traning...')

    for kw, value in kwargs.items():
        if kw == 'quantity_games':
            quantity_games = eval(value)
     
    # ...
```


### Trainer Example
- Evaluation neural network
    - [json file](https://github.com/yuriharrison/connect-four-lab/blob/master/connectFourLab/game/trainers/nn_evaluation.json)
    - [module](https://github.com/yuriharrison/connect-four-lab/blob/master/connectFourLab/game/trainers/nn_evaluation.py)