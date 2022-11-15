import time
import typing
import keyboard


class KeyMap:
    def __init__(self, key: str, func_when_pressed: typing.Callable,
                 func_when_released: typing.Callable, repeat_time=None):
        self.key = key
        self.func_when_pressed = func_when_pressed
        self.func_when_released = func_when_released
        self.is_pressed = False
        self.is_released = True
        self.repeat_time = repeat_time

        keyboard.on_press_key(self.key, self.call_when_pressed, suppress=True)
        keyboard.on_release_key(self.key, self.call_when_released, suppress=True)

    def call_when_pressed(self, event, *args):
        result = None
        if not self.is_pressed:
            result = self.func_when_pressed(*args)
            self.is_pressed = True
        return result

    def call_when_released(self, event, *args):
        result = None
        if self.is_pressed:
            result = self.func_when_released(*args)
            self.is_pressed = False
        return result

    def __eq__(self, other):
        return self.key == other.key


class KeyboardController:
    def __init__(self):
        self.__key_maps = []
        self.is_loop_started = True
        keyboard.add_hotkey("ctrl+c", self.switch_loop)

    def switch_loop(self):
        self.is_loop_started = not self.is_loop_started

    def add_key_map(self, key: str, func_pressed: typing.Callable,
                    func_released: typing.Callable):
        self.__key_maps.append(KeyMap(key, func_pressed, func_released))

    def loop(self):
        while self.is_loop_started:
            pass


if __name__ == "__main__":
    #keyboard.add_hotkey("w+d", lambda: print("w+d is pressed"))
    keyboard.hook(lambda x: print("w+d is pressed", x), True)
    while True:
        pass
    #controller = KeyboardController()
    #controller.add_key_map('w+', onvif_abs_move.increase_tilt, lambda: print(""))
