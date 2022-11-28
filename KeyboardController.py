import typing
import keyboard


class KeyMap:
    def __init__(self, key: str, func_when_pressed: typing.Callable,
                 func_when_released: typing.Callable, repeat_time=None,
                 once_call_press=True, once_call_release=True):
        self.key = key
        self.func_when_pressed = func_when_pressed if func_when_pressed else self.stub
        self.func_when_released = func_when_released if func_when_released else self.stub
        self.once_call_press = once_call_press
        self.once_call_release = once_call_release
        self.is_pressed = False
        self.repeat_time = repeat_time

        keyboard.on_press_key(self.key, self.call_when_pressed, suppress=True)
        keyboard.on_release_key(self.key, self.call_when_released, suppress=True)


    @staticmethod
    def stub(*args):
        pass

    def call_when_pressed(self, event, *args):
        result = None
        if not self.is_pressed and self.once_call_press:
            result = self.func_when_pressed(*args)
            self.is_pressed = True
            return result
        elif not self.once_call_press:
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


class KeyMapHook:
    def __init__(self, key: str, func_when_pressed: typing.Callable, once_call_press=True):
        self.key = key
        self.func_when_pressed = func_when_pressed if func_when_pressed else self.stub
        self.once_call_press = once_call_press
        self.is_pressed = False

        keyboard.hook_key(key, self.call)
        #keyboard.on_press_key(self.key, self.call_when_pressed, suppress=True)
        #keyboard.on_release_key(self.key, self.call_when_released, suppress=True)

    @staticmethod
    def stub(*args):
        pass

    def call(self, event):
        if event.event_type == "down" and not self.is_pressed and self.once_call_press:
            self.func_when_pressed()
            self.is_pressed = True
        elif event.event_type == "up":
            self.is_pressed = False
        elif not self.once_call_press:
            self.func_when_pressed()

    def __eq__(self, other):
        return self.key == other.key


class KeyboardController:
    def __init__(self):
        self.__key_maps = []
        self.is_loop_started = True
        keyboard.add_hotkey("ctrl+c", self.switch_loop)

    def switch_loop(self):
        self.is_loop_started = not self.is_loop_started

    def add_key_map(self, key: str,
                    func_pressed: typing.Optional[typing.Callable],
                    once_call=True):
        self.__key_maps.append(KeyMapHook(key, func_pressed, once_call_press=once_call))

    def delete_keymaps(self):
        keyboard.unhook_all()
        self.__key_maps.clear()

    def loop(self):
        while self.is_loop_started:
            pass


if __name__ == "__main__":
    #keyboard.hook_key("w", lambda x: print(f"{x.event_type} pressed"))
    #while True:
    #    pass
    controller = KeyboardController()
    controller.add_key_map('w', lambda: print("w pressed :)"))
    controller.loop()
