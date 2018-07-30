# CONNECT FOUR LAB - DOCUMENTATION

Connect Four Lab is a platform to test AI algorithms in the connect four game.

##### The game

The game engine runs a 7x7 board which is a more competitive version than the classic 7x6 board.

### Repository

[Repository on GitHub](https://github.com/yuriharrison/connect-four-lab)

### Getting Started

To see a guide on where to start go to [Getting Started](./gettingStarted)

### Requirements

- numpy
- Keras - Only to use Agents who requires neural network models
    - [Website & Documentation](https://keras.io/)
    - [Github](https://github.com/keras-team/keras)
- Kivy - Only to use the app
    - [Website](https://kivy.org/)
    - [Documentation](https://kivy.org/docs/)
    - [Github](https://github.com/kivy/kivy)

### Structure

The project is divided in two main packages 'game' and 'app'. The game package contains all the necessary modules to run a game (game engine, agents, models, helpers, etc). The app package is an user interface made in Kivy, in it you can run games see all turns being played, play yourself agains an Agent or train a new model.

### Agents

In Connect Four Lab each AI algorithm is called Agent.

__List of available agents:__

- Negamax - [about](./Agents/agents/#agentnegamax)
- Simulation - [about](./Agents/agents/#agentsimulation)
- Monte Carlo Tree Search - [about](./Agents/agents/#agentmontecarlo)
- Monte Carlo Tree Search with Neural Network - [about](./Agents/agents/#agentmctsnn)


### Related projects

This project use other authorial projects:

- Timer - Powerful python timer with useful functions (Decorator, callback, contextmanager) and easy to use. [see on Github](https://github.com/yuriharrison/timer)
- Custom Widgets for Kivy - [see on Github](https://github.com/yuriharrison/custom-widgets)


## License

This project is licensed under the MIT License - see the [LICENSE](./license) file for details

#### Dependencies

- [Kivy Licence](https://github.com/kivy/kivy/blob/master/LICENSE) - Only to use the app
- [Keras Licence](https://github.com/keras-team/keras/blob/master/LICENSE) - Only to use Agents who requires neural network models
