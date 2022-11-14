import typing
import keyboard


class KeyMap:
    def __init__(self, key: str, func_when_pressed: typing.Callable,
                 func_when_released: typing.Callable):
        self.key = key
        self.func_when_pressed = func_when_pressed
        self.func_when_released = func_when_released
        self.is_pressed = False
        self.is_released = True

        keyboard.on_press_key(self.key, self.call_when_pressed)
        keyboard.on_release_key(self.key, self.call_when_released)

    def call_when_pressed(self, event, *args):
        self.is_released = False
        result = None
        if not self.is_pressed:
            result = self.func_when_pressed(*args)
            self.is_pressed = True
        return result

    def call_when_released(self, event, *args):
        self.is_pressed = False
        result = None
        if not self.is_released:
            result = self.func_when_released(*args)
            self.is_released = True
        return result

    def __eq__(self, other):
        return self.key == other.key


class KeyboardController():
    def __init__(self):
        self.__key_maps = []
        self.is_loop_started = True
        keyboard.add_hotkey("ctrl+c", self.turn_loop)

    def turn_loop(self):
        self.is_loop_started = not self.is_loop_started

    def add_key_map(self, key: str, func_pressed: typing.Callable,
                    func_released: typing.Callable):
        self.__key_maps.append(KeyMap(key, func_pressed, func_released))

    def loop(self):
        while self.is_loop_started:
            pass
