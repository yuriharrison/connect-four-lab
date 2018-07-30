# Getting Started

This project allow you to use an user interface (app package) or just execute games through code.

### Code only

To run a game you need to choose the Agents which will play the game and import the game engine. To learn how to do that follow the links bellow:

- Game engine - [RunGame class](./Game/game)
- About Agents - [AgentBase Class](./Game/game)
- Agents - [List of Agents](./Game/game)

## APP

To start the App execute the file 'run_app.py' on the root directory.

### Running a game

Click in "Play" on the Main Menu

__[Image 1]__

![main_menu](./img/gs_img1.png)

Select the Agents that you want playing.
Agents who requires neural network models, you'll have to choose which trained model they're gonna use (see image 3 bellow).
The player one will be the white peaces, player two the blacks.
The first player to play will be randomly selected.

You can also select the time limit that the players will have to play the whole match.
The Timer Icon (see image 2 bellow) determine if the Agent are able to manage time limited matches. You can run time limited matches with Agents which don't manage time, but those with the risk of run out of time during the match which will give the win to the adversary.

__[Image 2]__

![main_menu](./img/gs_img2.png)

__[Image 3]__

![main_menu](./img/gs_img3.png)

Some matches can finish immediately others can take minutes, depends on the match configuration.

In time limited matches you can see the clock running o the top left of the screen (see image 4 bellow).

You can navegate on the history of the match in the navebar on the botton of the screen.

See the message box on the bottom right of the screen to know what's happening.

__[Image 4]__

![main_menu](./img/gs_img4.png)


### Training a new model

Click on "Training" on the main menu.

__[Image 5]__

![main_menu](./img/gs_img5.png)

Select which trainer you want to execute. Read the description and set the variables if necessary. Click in "Start Training".

__[Image 6]__

![main_menu](./img/gs_img6.png)

While running the trainer the console screen will show log messages from the trainer. You can stop the training by clicking on the "Cancel" button, the trainer will receive a command to stop.

__[Image 7]__

![main_menu](./img/gs_img7.png)

After finish you can click on "Play" to be directed to the Game Configuration Screen.

__[Image 8]__

![main_menu](./img/gs_img7.png)


## Creating a new Agent

It's easy to create a new Agent. To create a new agent, you only need to crete a new module on the `/game/Agents/` folder and create a class which inherit from AgentBase.

To create the new Agent class see the AgentBase class [documentation](./Agents/base) to check which are the requirements and examples of implementations. Also start the name of the class with 'Agent' to be automatically detected by the APP and appear on the Configuration Screen.

You'll also wanna check the Strategies [documentation](./Agents/strategies) which will help you creating variants of existing Agents and other algorithms.

For Agents which requires neural network models you'll want to create a [Trainer](./Agents/trainers)