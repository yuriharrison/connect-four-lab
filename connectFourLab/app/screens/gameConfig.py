import time
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen
from kivy.uix.modalview import ModalView
from ..myWidgets import SelectionBoxItem
from .. import context


class ModelItem(SelectionBoxItem):

    def __init__(self, data, **kw):
        self.model_name = data[0]
        self.model_file = data[1]
        super().__init__(data=data, **kw)


class ModelSelection(ModalView):
    sb_model = ObjectProperty(None)
    selected_model_file = None

    def __init__(self, item, **kw):
        self.item = item
        self.model_key = item.data.model_key
        super().__init__(**kw)

    def load_models(self):
        self.sb_model.data = context.get_trained_models(self.model_key)
        self.sb_model.load_items()
        self.sb_model.bind(on_selection_changed=self._on_selected_model)
    
    def _on_selected_model(self, sb, item):
        self.selected_model_file = item.model_file
        self.dismiss()


class AgentItem(SelectionBoxItem):
    pass

class TimeLimitItem(SelectionBoxItem):

    def __init__(self, data, **kw):
        self.text = data[0]
        self.value = data[1]
        super().__init__(data=data, **kw)


class GameConfigScreen(Screen):

    def __init__(self, **kw):
        super().__init__(**kw)
        self.loaded =  False

    def on_parent(self, widget, parent):
        if not self.loaded:
            self.reset()
            self.load_all_selection_boxes()
            self.loaded = True

    def reset(self):
        self.selecting = 0
        self.time_limit = None
        self.selected_agent_items = [None,None]
        self.selected_models = [None,None]
        self.ids.display_one.select = False
        self.ids.display_two.select = False

    def load_all_selection_boxes(self):
        self.load_agents_options()
        self.load_time_limit_options()

    def load_time_limit_options(self):
        self.ids.sb_time_limit.data = context.get_time_options()
        self.ids.sb_time_limit.load_items()
        self.ids.sb_time_limit.bind(on_selection_changed=self._on_selected_time_limit)

    def load_agents_options(self):
        self.ids.sb_agents.data = context.get_agents()
        self.ids.sb_agents.load_items()
        self.ids.sb_agents.bind(on_selection_changed=self._on_selected_agent)
    
    def on_enter(self):
        self._set_default()

    def _set_default(self):
        #by default index 1 is AgentRandom
        self.ids.sb_agents.select(1)
        #set player two
        self.ids.sb_agents.select(1)
        #by default index 0 is 'No Limit'
        self.ids.sb_time_limit.select(0)

    def on_leave(self):
        self.reset()
        self.ids.sb_agents.reset()
        self.ids.sb_time_limit.reset()


    def _on_selected_time_limit(self, sb, item):
        self.time_limit = item.value

    def _on_selected_agent(self, sb, item, model_set=False):
        if not model_set:
            if self._need_model(item):
                return

        self._set_player(item)
        self.switch_selection()

    def _need_model(self, item):
        if item.data.require_nn_model:
            self.model_selection = ModelSelection(item)
            self.model_selection.bind(on_dismiss=self._on_model_selection_dismiss)
            self.model_selection.load_models()
            self.model_selection.open()
            return True
    
    def _on_model_selection_dismiss(self, modal):
        model_file = self.model_selection.selected_model_file

        if model_file:
            self.selected_models[self.selecting] = model_file
            self._on_selected_agent(None, modal.item, model_set=True)
        else:
            self.ids.sb_agents.select(self.selected_agent_items[self.selecting], 
                                      silent=True)

    def _set_player(self, item):
        self.selected_agent_items[self.selecting] = item
        
        if self.selecting == 0:
            self.ids.display_one.text = item.data.name
            self.ids.display_one.kind = item.data.kind
        elif self.selecting == 1:
            self.ids.display_two.text = item.data.name
            self.ids.display_two.kind = item.data.kind

    def switch_selection(self):
        self.selecting = 0 if self.selecting == 1 else 1

        if self.selected_agent_items[self.selecting]:
            self.ids.sb_agents.select(self.selected_agent_items[self.selecting], 
                                      silent=True)
        
        #switch the selection displays
        if self.selecting == 0:
            self.ids.display_one.selected = True
            self.ids.display_two.selected = False
        elif self.selecting == 1:
            self.ids.display_one.selected = False
            self.ids.display_two.selected = True


    def on_btn_start_game_press(self, btn):
        game_screen = self.manager.game
        game_screen.players = [item.data for item in self.selected_agent_items]
        game_screen.models = self.selected_models
        game_screen.time_limit = self.time_limit
        game_screen = self.manager.game
        self.manager.transition.direction = 'left'
        self.manager.current = game_screen.name

    def on_btn_back_press(self, btn):
        self.manager.transition.direction = 'right'
        self.manager.current = self.manager.home.name

