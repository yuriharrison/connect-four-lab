import os, sys
import random
import numpy as np
import time
import traceback
from enum import Enum
from copy import copy, deepcopy
from threading import Thread
from enum import Enum, auto
from .helpers import next_position, check_winner
from .timer import Chronometer, Timer
from .agents import AgentRandom, AgentHuman


class RunGame:
    GameStatus = Enum('GameStatus', 'running winner tie timeout killed exception')
    BOARD_FORMAT = (7,7)
    MAX_TURNS_POSSIBLE = BOARD_FORMAT[0]*BOARD_FORMAT[1]
    _INVALID_POSITION_MSG = '{} chose an invalid column. Position: {}'

    def __init__(self, 
                 player_one=None, 
                 player_two=None,
                 first_player_randomized=True,
                 time_limit=None,
                 print_result_on_console=False,
                 start=True,
                 ascync=False
                ):
        self.first_player_randomized = first_player_randomized
        self._time_limit = time_limit
        self._print_console = print_result_on_console
        self.status = None
        self.game_thread = None
        self.ascync=ascync

        if not player_one:
            player_one = AgentRandom()
        elif type(player_one) == type:
            player_one = player_one()
            

        if type(player_one) is AgentHuman:
            player_one.get_input = self._get_human_input

        if not player_two:
            player_two = AgentRandom()
        elif type(player_two) == type:
            player_two = player_two()

        if type(player_two) is AgentHuman:
            player_two.get_input = self._get_human_input

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
        self.reset()
        self.kill_match = False
        self.status = self.GameStatus.running

        if self.ascync:
            self.game_thread = Thread(target=self._run_game)
            self.game_thread.start()
        else:
            self._run_game()

    def reset(self):
        self.winner = None
        self.time_expired = False
        self._memory = []
        self._empty_board()
        self.kill()

    def _run_game(self):
        try:
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
            self._on_end_game()

    def _define_char(self, first_player):
        if not self._print_console:
            return

        for i in self.players:
            if i == first_player:
                self.players[i].char = 'X'
            else:
                self.players[i].char = 'O'

    def _turns_loop(self, fisrt_player):
        next_to_play = fisrt_player

        for i in range(self.MAX_TURNS_POSSIBLE):
            turn = i + 1
            self._on_new_turn(self.players[next_to_play], 
                              self.clocks[next_to_play])

            playing = next_to_play
            next_to_play = 1 if next_to_play == -1 else -1

            with self.clocks[playing]:
                if self._time_limit:
                    clock_copy = copy(self.clocks[playing])
                    self.players[playing].update_clock(turn, clock_copy)

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
                raise Exception(self._INVALID_POSITION_MSG
                                .format(self.players[playing].name, column))

            next_pos = next_position(self.board, column)

            if next_pos is None:
                raise Exception(self._INVALID_POSITION_MSG
                                .format(self.players[playing].name, column))
            
            self._memory.append([playing, deepcopy(self.board), column])

            self._on_end_turn()


            self.board[column, next_pos] = playing

            self._check_winner()

            if self.winner:
                self.status = self.GameStatus.winner
                return

    def _check_winner(self):
        winner = check_winner(self.board)
        if winner:
            self.winner = self.players[winner]
    
    def _time_out(self):
        self.time_expired = True

    def kill(self):
        self.kill_match = True

        if self.ascync and self.game_thread:
            for _, player in self.players.items():
                if type(player) is AgentHuman:
                    player.column_choosed = 0

    def _empty_board(self):
        self.board = np.zeros(self.BOARD_FORMAT, dtype=int)

    @property
    def is_running(self):
        return self.status == self.GameStatus.running


    def _get_human_input(self):
        '''To be overridden by an UI'''
        pass

    def _on_new_turn(self, player, clock):
        '''To be overridden by an UI'''
        pass

    def _on_end_turn(self):
        '''To be overridden by an UI'''
        pass

    def _on_end_game(self):
        '''To be overridden by an UI'''
        pass

    def _print_result_console(self):
        board = self.board
        players = self.players
        turn = len(self._memory)

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
