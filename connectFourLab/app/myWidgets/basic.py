from kivy.properties import BooleanProperty
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.button import ButtonBehavior
from kivy.uix.slider import Slider
from kivy.uix.relativelayout import RelativeLayout
from .. import context


class ImagePlus(Image):

    def  __init__(self, source=None, **kw):
        super().__init__(**kw)
        self.source_ = source

    @property
    def source_(self):
        return self.source

    @source_.setter
    def source_(self, value):
        if not value:
            self.source = None
            return

        self.source = context.get_image_path(value)


class ButtonPlus(ButtonBehavior, RelativeLayout):
    disabled = BooleanProperty(False)

    def __init__(self, background=None, **kw):
        super().__init__(**kw)
        self.__background = None
        self.__background_down =  None
        self.__background_disabled_normal =  None
        self.__background_disabled_down =  None

        self._image = ImagePlus()
        self.add_widget(self._image)
        self.set_top
        self._label = Label()
        self.add_widget(self._label)

        if background:
            self.__background = background

    def enable(self):
        self.disabled = False

    def disable(self):
        self.disabled = True

    @property
    def background(self):
        return self.__background

    @background.setter
    def background(self, value):
        self.__background = value
        self._image.source_ = self.__background

    @property
    def background_down(self):
        return self.__background_down

    @background_down.setter
    def background_down(self, value):
        self.__background_down = value

    @property
    def background_disabled_normal(self):
        return self.__background_disabled_normal

    @background_disabled_normal.setter
    def background_disabled_normal(self, value):
        self.__background_disabled_normal = value
        
    @property
    def background_disabled_down(self):
        return self.__background_disabled_down

    @background_disabled_down.setter
    def background_disabled_down(self, value):
        self.__background_disabled_down = value

    def on_disabled(self, instance, value):
        if self.disabled and self.background_disabled_normal:
            self._image.source_ = self.background_disabled_normal
        else:
            self._image.source_ = self.background

    def on_press(self):
        if self.disabled:
            if self.background_disabled_down:
                self._image.source_ = self.background_disabled_down
        else:
            if self.background_down:
                self._image.source_ = self.background_down

    def on_release(self):
        if self.disabled:
            if self.background_disabled_down and self.background_disabled_normal:
                self._image.source_ = self.background_disabled_normal
        else:
            if self.background_down:
                self._image.source_ = self.background

    def dispatch(self, event, *a, **kw):
        # Intercept and block 'on_press' and 'on_release' if disabled
        if self.disabled:
            if event == 'on_press':
                self.on_press()
            elif event == 'on_release':
                self.on_release()
            else:
                super().dispatch(event, *a, **kw)
            return
        else:
            super().dispatch(event, *a, **kw)

    @property
    def label_text(self):
        return self._label.text

    @label_text.setter
    def label_text(self, value):
        self._label.text = value

    @property
    def font_size(self):
        return self._label.font_size

    @font_size.setter
    def font_size(self, value):
        self._label.font_size = value
        
    @property
    def font_name(self):
        return self._label.font_name

    @font_name.setter
    def font_name(self, value):
        self._label.font_name = value


class SliderPlus(Slider):

    def __init__(self, **kw):
        super().__init__(**kw)
        self.register_event_type('on_press')
        self.register_event_type('on_slide')
        self.register_event_type('on_release')

    @property
    def cursor_image_(self):
        return self.cursor_image

    @cursor_image_.setter
    def cursor_image_(self, value):
        if not value:
            self.cursor_image = None
            return

        self.cursor_image = context.get_image_path(value)

    @property
    def cursor_disabled_image_(self):
        return self.cursor_image

    @cursor_disabled_image_.setter
    def cursor_disabled_image_(self, value):
        if not value:
            self.cursor_disabled_image = None
            return

        self.cursor_disabled_image = context.get_image_path(value)

    def on_touch_down(self, touch):
        rtr = super().on_touch_down(touch)
        if rtr:
            self.dispatch('on_press')
        return rtr

    def on_touch_move(self, touch):
        rtr = super().on_touch_move(touch)
        if rtr:
            self.dispatch('on_slide')
        return rtr

    def on_touch_up(self, touch):
        rtr = super().on_touch_up(touch)
        if rtr:
            self.dispatch('on_release')
        return rtr

    def on_press(self):
        pass

    def on_slide(self):
        pass

    def on_release(self):
        pass
