"""Connect Four game logic"""
import os, sys
import random
import numpy as np
import time
import traceback
from enum import Enum
from copy import copy, deepcopy
from threading import Thread
from enum import Enum, auto
from . import helpers
from .timer import Chronometer, Timer
from .agents import AgentRandom, AgentHuman


class InvalidColumn(Exception):

    def __init__(self, player_name, value, message):
        full_msg = '{} chose an invalid column. Column: {}'.format(player_name, value)

        if message:
            full_msg = '{} - {}'.format(full_msg, message)

        super().__init__(full_msg)


class RunGame:
    """Run matches of Connect Four (7x7)

    This class uses [Agents](./Agents) to take actions
    each turn and [Timer](./timer) to control the `time_limit`.

    # Arguments
        player_one: type or instance, optional, default `None`
            - Type or instance of any `AgentBase` object
            - If `None` the `AgentRandom` object will be assigned 
        player_two: same as `player_one`
        first_player_randomized: bool, optional, default False
            - Defines if the first turn will be randomized or the player one
                will start the game
        time_limit: int, optional, default None
            - Defines the limit of time each player have to play the match
            - `None` - Unlimited time
        print_result_on_console: bool, optional, default False
            - Defines if in the end of the match the result will be printed
                on the console. Good for debug.
        start: bool, optional, default True
            - If `True` the game will be started in the init or 
                else you have to call `start`
        async: bool, optional, default False
            - If `True` the game will be run asynchronously

    # Attributes
        GameStatus: Enum -> (running, winner, tie, timeout, killed, exception)
            - Example: RunGame.GameStatus.winner
        BOARD_FORMAT: tuple, constant, value (7,7), define the board dimensions
        MAX_TURNS_POSSIBLE: int, the maximum number of turns in a match
        winner: `AgentBase` object
            - The Agent winner of the last match, if the is one.
        status: GameStatus, check the example(2) bellow
            - `None` - New instance, not started yet 
            - `running` - Game is running
            - `winner` - Last game ended with a winner
            - `tie` - Last game ended in a tie
            - `timeout` - In the last game one of the players
                left the time run out
            - `killed` - The game was stoped with the `kill` method
            - `exception` - Exception during the game execution

    # Properties
        is_running: Return `True` if the game is currently running

    # Exeptions
        InvalidColumn: raised when the agent return a column out of range
            or a column already fulfilled

    __Example 1__

    ```python
    from connectFourLab.game import RunGame
    RunGame(print_result_on_console=True)
    ```

    __Example 1__

    ```python
    import time
    from connectFourLab.game import RunGame
    from connectFourLab.game.agents.monteCarlo import AgentSimulation

    game = RunGame(player_one=AgentSimulation, async=True)
    while game.is_running:
        time.sleep(1)
    
    if game.status == game.GameStatus.tie:
        print('The game ended in a tie.')
    elif game.status == game.GameStatus.winner:
        print('Winner:', game.winner.name)
    elif etc...
    ```

    ### UI implementation

    To implement an User Interface you can override the events and
    implement the `get_human_input`

    # Events
        on_game_start: Triggered when the game starts
        on_new_turn: Triggered when a new turn starts
        on_end_turn: Triggered when the turn ends
        on_game_end: Triggered when the game ends

    # User input
        get_human_input: It's called by any AgentHuman in the match

    # UI Attributes
        memory: list, register all turns data
            - Item: (player_id, current_board, column_choosed)
        players: dict, two Agents one for each player
            - player one: id `1` - two: id `-1`
        clock: dict, two clocks (`Chronometer` or `Timer`) one for each player
            - player one: id `1` - two: id `-1`

    # UI Example
        See [Game Screen - Board class](../../app/screens/game#board-class)
    """
    GameStatus = Enum('GameStatus', 'running winner tie timeout killed exception')
    BOARD_FORMAT = (7,7)
    MAX_TURNS_POSSIBLE = BOARD_FORMAT[0]*BOARD_FORMAT[1]
    

    def __init__(self,
                 player_one=None, 
                 player_two=None,
                 first_player_randomized=True,
                 time_limit=None,
                 print_result_on_console=False,
                 start=True,
                 async=False
                ):
        self.first_player_randomized = first_player_randomized
        self._time_limit = time_limit
        self._print_console = print_result_on_console
        self.status = None
        self.game_thread = None
        self.async=async

        if not player_one:
            player_one = AgentRandom()
        elif type(player_one) == type:
            player_one = player_one()
            

        if type(player_one) is AgentHuman:
            player_one.get_input = self.get_human_input

        if not player_two:
            player_two = AgentRandom()
        elif type(player_two) == type:
            player_two = player_two()

        if type(player_two) is AgentHuman:
            player_two.get_input = self.get_human_input

        if self._time_limit:
            self.clocks = {1:Timer(self._time_limit, self._time_out), 
                          -1:Timer(self._time_limit, self._time_out)}
        else:
            self.clocks = {1:Chronometer(), -1:Chronometer()}

        player_one.id = 1
        player_two.id = -1
        self.players = {1:player_one, -1:player_two}

        if start:
            self.start()

    def start(self):
        """Starts a new match"""
        self._reset()
        self.kill_match = False
        self.status = self.GameStatus.running

        if self.async:
            self.game_thread = Thread(target=self._run_game)
            self.game_thread.start()
        else:
            self._run_game()

    def _reset(self):
        """Reset the enviroment for a new game"""
        self.kill()
        self.winner = None
        self.time_expired = False
        self.memory = []
        self._empty_board()

        for _, clock in self.clocks.items():
            clock.reset()

    def _run_game(self):
        """Run the game (can be called asynchronously)"""
        try:
            self.on_game_start()

            first_player = 1
            if self.first_player_randomized:
                first_player = 1 if random.randint(0,1) == 0 else -1

            self._define_char(first_player)

            self._turns_loop(first_player)
            
            if self.status == self.GameStatus.running:
                self.status = self.GameStatus.tie

            self._print_result_console()
        except:
            exc = sys.exc_info()
            traceback.print_exception(*exc)
            self.exception = exc
            self.status = self.GameStatus.exception
        finally:
            self.on_game_end()

    def _define_char(self, first_player):
        """Define the character to represent each player (X or O)
        
        Only relevant when printing the result
        """
        if not self._print_console:
            return

        for i in self.players:
            if i == first_player:
                self.players[i].char = 'X'
            else:
                self.players[i].char = 'O'

    def _turns_loop(self, fisrt_player):
        """Run all tuns necessary
        
        Each turn get an action, verify if the action is valid,
        modify board check if the is a winner, if not go to the next turn.

        If the `time_limit` is not None, it will use a [Timer](timer)
        for each player. If the time runs out the player loses.
        """
        next_to_play = fisrt_player

        for i in range(self.MAX_TURNS_POSSIBLE):
            turn = i + 1
            self.on_new_turn(self.players[next_to_play], 
                              self.clocks[next_to_play])

            playing = next_to_play
            next_to_play = 1 if next_to_play == -1 else -1

            with self.clocks[playing] as clock:
                if self._time_limit:
                    c_clock = copy(clock)
                    self.players[playing].update_clock(turn, c_clock)

                column = self.players[playing].action(deepcopy(self.board))
                # Thread(target=self.get_player_choice, args=(playing,)).start()

            if self.time_expired:
                self.winner = self.players[next_to_play]
                self.status = self.GameStatus.timeout
                return
            elif self.kill_match:
                self.status = self.GameStatus.killed
                return

            if column > 6 or column < 0:
                raise InvalidColumn(self.players[playing].name, column,
                    'Column out of range, the range of columns is 0 to 6.')

            next_pos = helpers.next_position(self.board, column)

            if next_pos is None:
                raise InvalidColumn(self.players[playing].name, column,
                    'The chosen column is full.')
            
            self.memory.append([playing, deepcopy(self.board), column])

            self.on_end_turn()


            self.board[column, next_pos] = playing

            self._check_winner()

            if self.winner:
                self.status = self.GameStatus.winner
                return

    def _check_winner(self):
        """Check if the current board has a winner, if so sets the winner"""
        winner = helpers.check_winner(self.board)
        if winner:
            self.winner = self.players[winner]
    
    def _time_out(self):
        """Time out callback of the `clocks`
        triggered if one of the players run out of time."""
        self.time_expired = True

    def kill(self):
        """Stop the current match.

        Force the game to stop and wait for the status confirmation.
        """
        self.kill_match = True

        while self.is_running:
            time.sleep(.2)

    def _empty_board(self):
        self.board = np.zeros(self.BOARD_FORMAT, dtype=int)

    @property
    def is_running(self):
        return self.status == self.GameStatus.running


    def get_human_input(self, player, board):
        """Event game start
        
        To be overridden by an UI.

        This method will be called by every `AgentHuman`
        present in the match, if the is one. This method
        should return the user input, the player
        column of choice.

        If this method is not overridden, the `AgentHuman`
        won't work

        # Arguments
            player: `AgentHuman`, owner of the turn
            board: current state of the board

        # Return
            User input, column of choice, as int 0-6
        """
        pass

    def on_game_start(self):
        """Event game start
        
        To be overridden by an UI. 
        Called in the beginning of a match.
        """
        pass

    def on_new_turn(self, player, clock):
        """Event new turn
        
        To be overridden by an UI.
        Called in the beginning of each turn.
        
        # Arguments
            player: `AgentBase` object, owner of the turn
            clock: `Chronometer` or `Timer`,
                clock of the owner of the turn
        """
        pass

    def on_end_turn(self):
        """Event end turn
        
        To be overridden by an UI. 
        Called in the end of a turn."""
        pass
        
    def on_game_end(self):
        """Event game end
        
        To be overridden by an UI. 
        Called in the end of a match."""
        pass


    def _print_result_console(self):
        """Print the end result of a match in the console
        
        Print the board game with characters ('X' and 'O')
        representing the players ids 1 and -1, the number of turns
        print the array `board` and the name of the winner.
        """
        board = self.board
        players = self.players
        turn = len(self.memory)

        if not self._print_console:
            return

        board_rendered = str()

        if(turn == 0):
            print(50*'_')

            for k in players: 
                print("Player {} played as {}".format(players[k].name, players[k].char))

            print(50*'_')
        else:
            print("Turn: {}\n".format(turn))
        
        for row in range(6)[::-1]:
            for _, column in enumerate(board):
                id = column[row]
                position = '___|' if id == 0 else '_{}_|'.format(players[id].char)
                board_rendered += position
            
            board_rendered += '\n'

        print(board_rendered)
        print(board)
        if self.winner:
            print("\n{} won! Played as {}."
                    .format(self.winner.name, self.winner.char))
