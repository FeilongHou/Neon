from kivy.uix.relativelayout import RelativeLayout

def keyboard_closed(self):
    self._keyboard.unbind(on_key_down=self.on_keyboard_down)
    self._keyboard.unbind(on_key_up=self.on_keyboard_up)
    self._keyboard = None

def on_keyboard_down(self, keyboard, keycode, text, modifiers):
    if keycode[1] == 'left':
        self.move_speed = 0.02
    elif keycode[1] == 'right':
        self.move_speed = -0.02

    return True


def on_keyboard_up(self, keyboard, keycode):
    self.move_speed = 0
    return True


def on_touch_down(self, touch):
    '''
    Touch on the phone screen
    '''
    if touch.x < self.width/2:
        self.move_speed = 0.02
    else:
        self.move_speed = -0.02

    return super(RelativeLayout, self).on_touch_down(touch)


def on_touch_up(self, touch):
    '''
    Release touch on the phone screen
    '''
    self.move_speed = 0