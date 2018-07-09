from kivy.factory import Factory
from kivy.properties import BooleanProperty
from kivy.uix.button import ButtonBehavior
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.boxlayout import BoxLayout


class SelectionBoxItem(ButtonBehavior, RelativeLayout):
    selected = BooleanProperty(False)
    
    def __init__(self, data):
        self.data = data
        super().__init__()


class SelectionBox(BoxLayout):

    def __init__(self, items=None, **kw):
        super().__init__(**kw)
        self.silent = False
        self.data = []
        self.items = []
        self._selection_changed_events = []
        self.multi_selection = False
        self.reset()
    
    @property
    def selected_item(self):
        return self.items[self.selected_index]

    def select(self, value, silent=False):
        self.silent = silent
        tp = type(value)
        
        if tp is int:
            item = self.items[value]
        elif value in self.items:
            item = value
        else:
            raise ValueError('{} don\'t contain {}'.format(type(self), value))
        
        if not silent:
            item.dispatch(event_type='on_press')
        else:
            self._on_item_press(item)

    @property
    def previous_item(self):
        return self.items[self.previous_index]

    def load_items(self):
        self.items = []

        for i, agent in enumerate(self.data):
            widget = self._convertion(agent)
            widget.index = i
            self.add_widget(widget)
            self.items.append(widget)
    
    def register_event_selection_changed(self, event):
            self._selection_changed_events.append(event)

    def reset(self):
        self.selected_index = None
        self.previous_index = None

        for item in self.items:
            item.selected = False


    def _convertion(self, item):
        model = Factory.classes[self.model]['cls']
        instance = model(item)
        instance.bind(on_press=self._on_item_press)
        return instance
    
    def _on_item_press(self, item):
        if not item.selected:
            item.selected = True

            self.previous_index = self.selected_index
            self.selected_index = item.index

            if not self.multi_selection and self.previous_index is not None:
                self.items[self.previous_index].selected = False

        elif self.multi_selection:
            item.selected = False

        if not self.silent:
            for event in self._selection_changed_events:
                event(item)
        else:
            self.silent = False
