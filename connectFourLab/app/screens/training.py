import sys
import traceback
import time
from threading import Thread
from kivy.clock import mainthread
from kivy.properties import ObjectProperty, BooleanProperty
from kivy.uix.screenmanager import Screen
from .. import context


class TrainingScreen(Screen):
    trainer = ObjectProperty(None)
    running = BooleanProperty(False)
    master_msg_key = '[MASTER]'

    def on_enter(self):
        self.start_training()

    def on_leave(self):
        self.ids.log_console.text = ''

    def start_training(self):
        self.module = module = context.load_trainer_module(self.trainer.module)
        module.kwargs = self.trainer.variables
        self.running = True
        self.thread = Thread(target=self.async_start, args=(module,))
        self.thread.start()

    def async_start(self, module):
        try:
            module.start(self.log)
        except:
            self.log('Exception during model training!')
            exc = sys.exc_info()
            traceback.print_exception(*exc)
        finally:
            if self.module.kill_training:
                self.log('Training successfully stopped!', self.master_msg_key)

            self.running = False

    @mainthread
    def log(self, message, msg_key='[TRAINER]'):
        self.ids.log_console.text += '\n {} > {}'.format(msg_key, message)

    def kill_thread(self):
        self.log('Stopping training... Wait..', self.master_msg_key)
        self.module.kill_training = True

    def on_btn_back_press(self, i):
        if self.running:
            self.kill_thread()
        else:
            self.manager.transition.direction = 'right'
            self.manager.current = self.manager.training_config.name

    def on_btn_start_game_press(self, i):
        self.manager.transition.direction = 'left'
        self.manager.current = self.manager.game_config.name