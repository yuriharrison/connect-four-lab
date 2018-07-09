from connectFourLab.app import MainApp

class LogConsole:
    def print(self, new_message):
        if type(new_message) != str:
            msg = 'Invalid value type. \
                Feedback only accept string. Wrong value: {}'.format(new_message)
            ValueError(msg)

        print(new_message)


if __name__ == '__main__':
    MainApp().run()
    # from connectFourLab.game import RunGame
    # from connectFourLab.game.agents.negamax import AgentNegamax
    # from connectFourLab.game.agents.mcstnn import AgentMCSTNN
    # from connectFourLab.game.agents.monteCarlo import AgentSimulation, AgentMonteCarlo
    # from connectFourLab.game.trainers import nn_evaluation_ as nn
    # from connectFourLab.game.trainers import nn_evaluation as nn2

    # nn2.kwargs = {'time_limit': 60*30, 'model_name': 'old'}
    # amodel = nn2.start(LogConsole())
    # import keras
    # model = keras.models.load_model('C:\Development\Python\ConnectFour\sample\connectFourLab\models\MCSTNN.h5')
    # agent = AgentMCSTNN(model)
    # RunGame(AgentMCSTNN(amodel), agent,
    #         first_player_randomized=False,
    #         print_result_on_console=True)
