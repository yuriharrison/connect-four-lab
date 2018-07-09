import functools
from kivy.properties import StringProperty
from kivy.uix.popup import Popup
from kivy.lang.builder import Builder


Builder.load_string('''
<ConfirmationPopup>:
    auto_dismiss: False
    title: 'Are you sure?'
    result: None
    size_hint: (.7,.7)
    description: ''
    button_continue_text: 'Continue'
    button_cancel_text: 'Cancel'

    BoxLayout:
        orientation: 'vertical'

        Label:
            text: root.description
            text_size: self.size
            padding_y: sp(20)
            font_size: sp(20)
            halign: 'left'
            valign: 'top'

        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: .25
            pos_hint: {'y': 0}
            Button:
                text: root.button_continue_text
                on_release:
                    root.result = 'continue'
                    root.dismiss()
            Button:
                text: root.button_cancel_text
                on_release:
                    root.result = 'cancel'
                    root.dismiss()
''')


class ConfirmationPopup(Popup):
    title = StringProperty('')
    description = StringProperty(None)
    button_continue_text = StringProperty(None)
    button_cancel_text = StringProperty(None)


class PopupDecorator:
    def __init__(self, cls_name=None, **kw):
        self._a_func = {}
        self._kw_func = {}
        self._self_func = None
        self.popup = None

        self._kw_config = kw
        if cls_name:
            self._cls_name = cls_name
        else:
            self._cls_name = ConfirmationPopup.__name__

    def __call__(self, func=None):
        self._func = func
        return functools.partialmethod(PopupDecorator.decorator, self)

    @staticmethod
    def decorator(func_self, self, *a, **kw):
        self._a_func = a
        self._kw_func = kw
        self._self_func = func_self
        self.popup = self._cls_name(**self._kw_config)
        self.popup.bind(on_dismiss=self.on_dismiss)
        self.popup.open()

    def on_dismiss(self, widget):
        if self.popup.result == 'continue':
            self._func(self._self_func, *self._a_func, **self._kw_func)

    