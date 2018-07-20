import time
import numpy as np
from enum import Enum
from threading import Thread

from kivy.clock import mainthread
from kivy.properties import StringProperty, ObjectProperty, BooleanProperty, DictProperty
from kivy.core.window import Window
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.label import Label
from kivy.uix.button import Button, ButtonBehavior
from kivy.uix.bubble import Bubble
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen

from .. import context
from ..myWidgets import ImagePlus, ConfirmationPopupDecorator, ConfirmationPopup, PolymorphicButton
from ...game import RunGame, helpers


class RematchPopup(ConfirmationPopup):
    pass
class ConfigurationPopup(ConfirmationPopup):
    pass
class ExitPopup(ConfirmationPopup):
    pass


class GameLogic(RunGame):
    '''Class necessary to bypass widget __init__ call'''
    def __init__(self):
        pass


class Board(RelativeLayout, GameLogic):
    texture = StringProperty(None)
    clock = ObjectProperty(None)
    navegation_bar = ObjectProperty(None)
    columns = ObjectProperty(None)
    positions = ObjectProperty(None)

    def __init__(self, **kw):
        RelativeLayout.__init__(self, **kw)

        self.__navegation_episode = None
        self._end_game_events = []
        self.last_hl = None

    def on_texture(self, instance, value):
        self.add_widget(ImagePlus(source=value), 1)

    def on_clock(self, instance, value):
        self.register_end_game_event(self.clock.end_game)

    def on_positions(self, instance, value):
        self._build_board_structure()


    def start(self, player_one=None, player_two=None, time_limit=None):
        RunGame.__init__(self, player_one, player_two, 
            time_limit=time_limit, 
            start=False, 
            async=True)

        super().start()
    
    def rematch(self):
        super().start()

    def _reset(self):
        self.stop_replay = True
        self.change_episode(reset=-1)
        self._initialize_board()
        super()._reset()

    def replay(self, game_memory):
        self.memory = game_memory
        self.change_episode(reset=0)
        self._play()

    def save_game(self, save_name='default_name'):
        np.save(r'saved_games/{}'.format(save_name), self.memory)

    def register_end_game_event(self, event):
        self._end_game_events.append(event)

    def navegate(self, button=None, slider=None):
        if slider is not None:
            self.change_episode(reset=slider)
            self._scenario()
            return
        else:
            action = button

        if action == 'pause':
            if self._play_thread:
                self.stop_replay = True

            self.navegation_bar.pause_play.be_play()
        elif action == 'play':
            self._play()
            self.navegation_bar.pause_play.be_pause()
        else:
            if action == 'backward':        
                self.change_episode(-1)
            elif action == 'forward':        
                self.change_episode(1)
            elif action == 'begin':        
                self.change_episode(reset=0)
            elif action == 'end':
                self.change_episode(reset=self._last_episode)

            self._scenario()

    @mainthread
    def change_episode(self, modifier=None, reset=None):
        if reset is not None:
            if reset == self.__navegation_episode:
                return
            else:
                self.__navegation_episode = reset
        elif modifier:
            self.__navegation_episode += modifier
        else:
            return


        # TODO: about the code below: 'IT MUST BE A BETTER WAY!'
        self.navegation_bar.slider.disabled = False
        self.navegation_bar.set_slider_value(self.__navegation_episode)
        self.navegation_bar.pause_play.enable()
        self.navegation_bar.backward.enable()
        self.navegation_bar.begin.enable()
        self.navegation_bar.forward.enable()
        self.navegation_bar.end.enable()

        if self.__navegation_episode == 0:
            self.navegation_bar.backward.disable()
            self.navegation_bar.begin.disable()
        elif self.__navegation_episode == -1:
            self.navegation_bar.pause_play.disable()
            self.navegation_bar.backward.disable()
            self.navegation_bar.begin.disable()
            self.navegation_bar.forward.disable()
            self.navegation_bar.end.disable()
            self.navegation_bar.slider.disabled = True
        elif self.__navegation_episode == self._last_episode:
            self.navegation_bar.pause_play.be_play().disable()
            self.navegation_bar.forward.disable()
            self.navegation_bar.end.disable()
            
    
    @property
    def navegation_episode(self):
        return self.__navegation_episode

    def _play(self):
        def _async_play(self):
            while self.navegation_episode != self._last_episode:
                self.change_episode(1)
                self._scenario()
                time.sleep(1)

                if self.stop_replay:
                    break

        self.stop_replay = False
        self._play_thread = Thread(target=_async_play, args=(self,))
        self._play_thread.start()


    def get_human_input(self, player, board):
        self.columns.disabled = False
        self.column_choosed = None

        while not self.kill_match and self.column_choosed is None:
            time.sleep(0.1)

        return self.column_choosed

    def _on_column_click(self, btn):
        if self.navegation_episode != self._last_episode:
            return

        column = int(btn.id)
        
        next = helpers.next_position(self.board, column)
        
        if next is None:
            self.message_box.show_message('This column is full! Choose another one.',
                                          time_sec=5,
                                          keep_old_msg=True)
        else:
            self.column_choosed = column
            self.columns.disabled = True


    def on_new_turn(self, player, clock):
        if self._time_limit:
            self.clock.new_turn_starts(clock)

        msg = 'Turn: {}'.format(self._player_description(player))
        self.message_box.show_message(msg)

    def on_end_turn(self):
        self.change_episode(modifier=1)
        self.navegation_bar.set_selider_max(self._last_episode)
        self._scenario()


    @property
    def _last_episode(self):
        return len(self.memory) - 1

    def on_game_end(self):
        msg = str()

        if self.winner:
            msg = ''

            if self.status == self.GameStatus.timeout:
                msg += 'Time expired! '

            player = self._player_description(self.winner)
            msg += '{} is the winner!'.format(player)
        elif self.status == self.GameStatus.tie:
            msg = 'The ended in a tie!'
        elif self.status == self.GameStatus.killed:
            msg = 'The game was interrupted!'
        elif self.status == self.GameStatus.exception:
            msg = 'Exception during the game execution!'

        for event in self._end_game_events:
            event()

        self.message_box.show_message(msg)

    def _player_description(self, player):
        player_desc = 'Player One' if player.id == 1 else 'Player Two'
        return player_desc + ' ({})'.format(player.name)

    @mainthread
    def _scenario(self):
        player, board, action = self._get_memory_navegation()
        self._load_scenario(board)
        self._action(player, board, action)

    def _action(self, player, board, column):
        next = helpers.next_position(board, column)
        position = self._get_screen_position(column, next)
        position.owner(player, highlight=True)

    def _get_memory_navegation(self):
        try:
            return self.memory[self.navegation_episode]
        except IndexError:
            print('Index error - Episode:', self.navegation_episode)

    def _build_board_structure(self):
        self.columns.disabled = True
        columns = self.columns
        positions = self.positions
        
        for i in range(self.BOARD_FORMAT[0]):
            btn = Button(id=str(i), opacity=0)
            btn.bind(on_press=self._on_column_click)
            columns.add_widget(btn)
            
            positions_column = BoxLayout(orientation='vertical')

            for _ in range(self.BOARD_FORMAT[1]):
                positions_column.add_widget(Position())

            positions.add_widget(positions_column)
    
    def _load_scenario(self, game_board):
        for i, column in enumerate(game_board):
            for j, value in enumerate(column):
                position = self._get_screen_position(i,j)
                position.owner(value)

    def _get_screen_position(self, column, row):
        screen_column = 6 - column
        position = self.positions.children[screen_column].children[row]
        return position

    @mainthread
    def _initialize_board(self):
        empty_board = np.zeros((7,6), dtype=int)
        self._load_scenario(empty_board)

    
class Position(ImagePlus):
    img_blank_space = None
    img_piece_white = None
    img_piece_white_hl = None
    img_piece_red = None
    img_piece_red_hl = None
    
    def __init__(self, **kw):
        super().__init__(**kw)
        self._blank()

    def owner(self, id, highlight=False):
        if id == 1:
            self._white(highlight)
        elif id== -1:
            self._red(highlight)
        else:
            self._blank()

        self.size = self.texture_size

    def _red(self, hl):
        if hl:
            self.source_=self.img_piece_red_hl
        else:
            self.source_=self.img_piece_red

        return self
    
    def _white(self, hl):
        if hl:
            self.source_=self.img_piece_white_hl
        else:
            self.source_=self.img_piece_white

        return self

    def _blank(self):
        self.source_ = self.img_blank_space
        return self


class BoardNavegation(BoxLayout):

    def on_release(self, btn):
        self.board.navegate(button=btn.form_name)

    def on_slider_move(self, slider):
        self.slider_bubble.opacity = 1
        self.slider_bubble.pos=(0,slider.top)
        self.slider_bubble.center_x=slider.value_pos[0]

        x ,y = int(self.slider.value) + 1, self.slider.max + 1
        text = '{} / {}'.format(x, y)
        if self.board.is_running:
           text += '*' 
        self.slider_bubble.text = text

    def on_navegation_slide(self, slider):
        self.board.navegate(slider=int(slider.value))
        self.slider_bubble.opacity = 0
    
    @mainthread
    def set_selider_max(self, value):
        self.slider.max = value

    def set_slider_value(self, value):
        if value < 0:
            self.slider.value = 0
        else:
            self.slider.value = value


class MessageBox(RelativeLayout):

    def __init__(self, **kw):
        super().__init__(**kw)
        self.thread = None

    def show_message(self, message, time_sec=None, keep_old_msg=False):
        if len(message) > 104:
            raise ValueError('Message is too large.')

        self.thread = Thread(target=self._async_show_message, args=(message, time_sec, keep_old_msg))
        self.thread.start()

    def _async_show_message(self, message, time_sec, keep_old_msg):
        self.opacity = 1

        self.old_text = self.label.text
        self.label.text = message

        if time_sec:
            time.sleep(time_sec)

            if keep_old_msg:
                self.label.text = self.old_text
            else:
                self.opacity = 0


class Menu(BoxLayout):

    def on_press_rematch(self, btn):
        if self.board.is_running:
            self.popup = RematchPopup()
            self.popup.bind(on_dismiss=self.rematch_popup_dismiss)
            self.popup.open()
        else:
            self.board.rematch()

    def rematch_popup_dismiss(self, i):
        if self.popup.result == 'continue':
            self.board.rematch()

    @ConfirmationPopupDecorator(ConfigurationPopup)
    def on_btn_config_release(self):
        self.root.manager.transition.direction = 'right'
        self.root.manager.current = self.root.manager.game_config.name


class GameClock(BoxLayout):
    value = StringProperty('--:--')
    timeout = BooleanProperty(False)
    running = BooleanProperty(False)

    def __init__(self, **kw):
        super().__init__(**kw)
        self._current_clock = None
        self.__thread_clock_tick = None

    def new_turn_starts(self, clock):
        self._current_clock = clock
        self.running = True
        if not self.__thread_clock_tick:
            self._start_clock_tick()

    def end_game(self):
        self.value = '--:--'
        self.timeout = False
        self.running = False
        self._current_clock = None
        self._stop_clock_tick = True
        self.__thread_clock_tick = None

    def _start_clock_tick(self):
        self._stop_clock_tick = False
        self.__thread_clock_tick = Thread(target=self._async_clock_tick)
        self.__thread_clock_tick.start()

    def _on_clock_tick(self):
        time_left = self._current_clock.time_left
        _, m, s = helpers.seconds_to_hms(int(time_left))

        if m == 0 and s == 0:
            self.timeout = True

        self.value = '{:02d}:{:02d}'.format(m,s)

    def _async_clock_tick(self):
        while True:
            self._on_clock_tick()
            time.sleep(1)

            if self._stop_clock_tick:
                break


class GameScreen(Screen):
    texture_source = StringProperty(None)

    def on_texture_source(self, instance, value):
        texture = ImagePlus(source=value).texture
        texture.wrap = 'repeat'

        import math
        uv = [math.ceil(x/y) for x, y in zip(Window.size, texture.size)]
        texture.uvsize = uv
        self.texture = texture

    def on_enter(self):
        self.default_window_size = Window.size
        Window.size = context.get_game_screen_size()
        self.set_players()
        self.board.start(self.player_one, self.player_two, self.time_limit)

    def set_players(self):
        for i, (agent, model_file) in enumerate(zip(self.players, self.models)):
            if agent.require_nn_model:
                agent = agent(model_file)
            self.players[i] = agent
            
        self.player_one, self.player_two = self.players

    def on_leave(self):
        Window.size = self.default_window_size
        self.board.kill()