from functools import partialmethod
from kivy.properties import StringProperty, DictProperty, ListProperty
from . import ButtonPlus


class MutationBehavior:
    pass


class PolymorphicButton(ButtonPlus):
    transform_prefix = 'be_'
    atlas = StringProperty(None)
    add_form = DictProperty(None)
    forms = ListProperty(None)
    current = StringProperty(None)

    def on_current(self, instance, value):
        name = 'be_' + value
        method = getattr(self, name)
        # TODO catch not existent method and create an error
        method()

    def on_forms(self, instance, value):
        for form in value:
            self.on_add_form(instance, form)

    def on_add_form(self, instance, value):
        # TODO: CREATE WIDGET EXCEPTION
        if 'name' not in value:
            raise Exception('You ')

        name = value.pop('name')
        method = partialmethod(PolymorphicButton.transform, name, **value)
        method_name = self.transform_prefix + name
        setattr(type(self), method_name, method)

    def transform(self, name,
                text=None,
                normal=None,
                down=None,
                disabled_normal=None,
                disabled_down=None):
        self.form_name = name

        # atlas = context.get_image_path(self.atlas) + '/'
        atlas = self.atlas + '/'
    
        if text:
            self.text = text

        if normal is str():
            image = normal
        else: 
            image = name + '_normal'

        self.background = atlas + image

        if down:
            if type(down) is str:
                image = down
            else:
                image = name + '_down'
            
            self.background_down = atlas + image
            
        if disabled_normal:
            if type(disabled_normal) is str:
                image = disabled_normal
            else:
                image = name + '_disabled_normal'
            
            self.background_disabled_normal = atlas + image
            
        if disabled_down:
            if type(disabled_down) is str:
                image = disabled_down
            else:
                image = name + '_disbled_down'
            
            self.background_disabled_down = atlas + image

        return self
