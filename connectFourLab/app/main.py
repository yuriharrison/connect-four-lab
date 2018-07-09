from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.modalview import ModalView
from kivy.core.window import Window
from kivy.config import Config
from .screens import *
from . import context


class LoadScreen(ModalView):
	pass


class MainApp(App):

	def build(self):
		self.title = context.get_application_title()
		self.icon = context.get_icon()
		Window.size= context.get_default_screen_size()
		context.load_all_kivy_files()
		return ScreenManager()
