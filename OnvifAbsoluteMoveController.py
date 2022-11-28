import keyboard

from OnvifAbsoluteMove import OnvifAbsoluteMove
from KeyboardController import KeyboardController
from utils import read_settings


class OnvifAbsoluteMoveController:
    def __init__(self):
        self.__onvif_abs_move = OnvifAbsoluteMove(36)
        self.__keyboard_controller = KeyboardController()
        self.is_keyboard_configured = False

        #self.configure_keyboard()

    @property
    def step(self):
        return self.__onvif_abs_move.step

    @step.setter
    def step(self, value):
        self.__onvif_abs_move.step = value

    def increase_step(self):
        delta_step = self.calculate_delta_step()
        print(delta_step)
        try:
            self.__onvif_abs_move.step += delta_step
        except:
            self.__onvif_abs_move.step = 1
        print(f"Current step: {self.step}")

    def decrease_step(self):
        delta_step = self.calculate_delta_step()
        print(delta_step)
        try:
            self.__onvif_abs_move.step -= delta_step
        except:
            self.__onvif_abs_move.step = 0
        print(f"Current step: {self.step}")

    def calculate_delta_step(self):
        print(self.__onvif_abs_move.zoom)
        return 0.001 + 0.004 * (1 - self.__onvif_abs_move.zoom)

    def enable_autofocus(self):
        self.__onvif_abs_move.set_autofocus()

    def disable_autofocus(self):
        self.__onvif_abs_move.unset_autofocus()

    def connect(self, ip_addr: str, port: int, user: str, password: str):
        self.__onvif_abs_move.connect(ip_addr, port, user, password)
        if not self.is_keyboard_configured:
            self.configure_keyboard()

    def disconnect(self):
        self.delete_hotkeys()

    def delete_hotkeys(self):
        self.__keyboard_controller.delete_keymaps()
        self.is_keyboard_configured = False

    def configure_keyboard(self):
        self.__keyboard_controller.add_key_map('w', self.__onvif_abs_move.increase_tilt, once_call=False)
        self.__keyboard_controller.add_key_map('s', self.__onvif_abs_move.decrease_tilt, once_call=False)
        self.__keyboard_controller.add_key_map('a', self.__onvif_abs_move.decrease_pan, once_call=False)
        self.__keyboard_controller.add_key_map('d', self.__onvif_abs_move.increase_pan, once_call=False)
        self.__keyboard_controller.add_key_map('e', self.__onvif_abs_move.increase_zoom, once_call=False)
        self.__keyboard_controller.add_key_map('q', self.__onvif_abs_move.decrease_zoom, once_call=False)
        self.__keyboard_controller.add_key_map('+', self.increase_step)
        self.__keyboard_controller.add_key_map('-', self.decrease_step)
        self.__keyboard_controller.add_key_map('f', self.enable_autofocus)
        self.__keyboard_controller.add_key_map('g', self.disable_autofocus)

    def run_loop(self):
        self.__keyboard_controller.loop()


if __name__ == "__main__":
    settings = read_settings("security.txt")

    ip = settings["ip"]
    port = settings["port"]
    login = settings["login"]
    password = settings["password"]

    onvif_controller = OnvifAbsoluteMoveController()
    onvif_controller.connect(ip, port, login, password)
    onvif_controller.step = 0.005
    onvif_controller.run_loop()
