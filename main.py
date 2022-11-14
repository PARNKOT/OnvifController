from KeyboardController import KeyboardController
from OnvifController import OnvifController

IP = "192.168.0.15"  # Camera IP address
PORT = 80  # Port
USER = "admin"  # Username
PASS = "qwerty"  # Password


if __name__ == '__main__':
    controller = KeyboardController()
    onvif_controller = OnvifController(IP, PORT, USER, PASS)

    controller.add_key_map('w', onvif_controller.move_up, onvif_controller.stop_move)
    controller.add_key_map('s', onvif_controller.move_down, onvif_controller.stop_move)
    controller.add_key_map('a', onvif_controller.move_left, onvif_controller.stop_move)
    controller.add_key_map('d', onvif_controller.move_right, onvif_controller.stop_move)
    controller.loop()


