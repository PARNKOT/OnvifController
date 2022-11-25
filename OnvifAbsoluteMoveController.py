from OnvifAbsoluteMove import OnvifAbsoluteMove
from KeyboardController import KeyboardController
from functools import partial

IP = "10.1.1.14"  # Camera IP address
PORT = 80  # Port
USER = "admin"  # Username
PASSWORD = "Pa$$w0rd"  # Password


class OnvifAbsoluteMoveController:
    def __init__(self):
        self.__onvif_abs_move = OnvifAbsoluteMove(36)
        self.__keyboard_controller = KeyboardController()
        self.configure_keyboard()

    @property
    def step(self):
        return self.__onvif_abs_move.step

    @step.setter
    def step(self, value):
        self.__onvif_abs_move.step = value

    def increase_step(self):
        try:
            self.step += 0.005
        except:
            self.step = 1
        print(f"Current step: {self.step}")

    def decrease_step(self):
        try:
            self.step -= 0.005
        except:
            self.step = 0
        print(f"Current step: {self.step}")

    def enable_autofocus(self):
        self.__onvif_abs_move.set_autofocus()

    def disable_autofocus(self):
        self.__onvif_abs_move.unset_autofocus()

    def connect(self, ip_addr: str, port: int, user: str, password: str):
        self.__onvif_abs_move.connect(ip_addr, port, user, password)

    def delete_hotkeys(self):
        del self.__keyboard_controller

    def configure_keyboard(self):
        self.__keyboard_controller.add_key_map('w', self.__onvif_abs_move.increase_tilt, None, once_call=False)
        self.__keyboard_controller.add_key_map('s', self.__onvif_abs_move.decrease_tilt, None, once_call=False)
        self.__keyboard_controller.add_key_map('a', self.__onvif_abs_move.decrease_pan, None, once_call=False)
        self.__keyboard_controller.add_key_map('d', self.__onvif_abs_move.increase_pan, None, once_call=False)
        self.__keyboard_controller.add_key_map('e', self.__onvif_abs_move.increase_zoom, None, once_call=False)
        self.__keyboard_controller.add_key_map('q', self.__onvif_abs_move.decrease_zoom, None, once_call=False)
        self.__keyboard_controller.add_key_map('+', self.increase_step, None)
        self.__keyboard_controller.add_key_map('-', self.decrease_step, None)
        self.__keyboard_controller.add_key_map('f', self.enable_autofocus, None)
        self.__keyboard_controller.add_key_map('g', self.disable_autofocus, None)

    def run_loop(self):
        self.__keyboard_controller.loop()


if __name__ == "__main__":
    onvif_controller = OnvifAbsoluteMoveController()
    onvif_controller.connect(IP, PORT, USER, PASSWORD)
    onvif_controller.step = 0.005
    onvif_controller.run_loop()
