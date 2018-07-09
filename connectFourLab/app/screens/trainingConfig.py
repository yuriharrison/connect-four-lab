from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen
from ..myWidgets import SelectionBoxItem
from .. import context


class TrainerItem(SelectionBoxItem):
    pass


class Trainer:
    name = 'Trainer name'
    short_description = 'Short description'
    description = 'Full description'
    module = None
    variables = None

class TrainingConfigScreen(Screen):
    selected_trainer = ObjectProperty(None, allownone=True)

    def __init__(self, **kw):
        super().__init__(**kw)
        self.loaded =  False

    def on_parent(self, widget, parent):
        if not self.loaded:
            self.reset()
            self.load_selection_box_trainers()
            self.loaded = True

    def reset(self):
        self.selected_trainer = None
        self.ids.ti_variables.text = ''
        self.ids.sb_trainers.reset()

    def load_selection_box_trainers(self):
        self.ids.sb_trainers.data = self.convert_dict_to_trainer(context.get_trainers())
        self.ids.sb_trainers.load_items()
        self.ids.sb_trainers.register_event_selection_changed(self._on_selected_trainer)

    def convert_dict_to_trainer(self, trainers_dict):
        trainers_obj = []
        for trainer in trainers_dict:
            obj = Trainer()
            obj.__dict__.update(trainer)
            trainers_obj.append(obj)
        return trainers_obj

    def on_leave(self):
        self.reset()

    def _on_selected_trainer(self, item):
        self.selected_trainer = item.data
        self.ids.lbl_description.text = item.data.description

    def on_btn_start_training_press(self, btn):
        variables, err = self.get_variables()
        if err:
            return

        self.selected_trainer.variables = variables
        self.manager.training.trainer = self.selected_trainer
        self.manager.transition.direction = 'left'
        self.manager.current = self.manager.training.name

    def get_variables(self):
        variables_input = self.ids.ti_variables.text.strip()
        if variables_input:
            variables = {}
            kwargs = variables_input.split(';')
            for kwa in kwargs:
                kwa = kwa.split('=')
                if len(kwa) is 2:
                    kw, value = kwa
                    variables[kw] = value
            return variables, False
        else:
            return None, False

    def on_btn_back_press(self, btn):
        self.manager.transition.direction = 'right'
        self.manager.current = self.manager.home.name

