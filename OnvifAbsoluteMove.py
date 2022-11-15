import math

from onvif import ONVIFCamera
from KeyboardController import KeyboardController

IP = "10.1.1.14"  # Camera IP address
PORT = 80  # Port
USER = "admin"  # Username
PASS = "Pa$$w0rd"  # Password

STEP = 0.005


def range(min, max):
    def decorator(func):
        def wrapper(value, *args, **kwargs):
            if min <= value <= max:
                return func(value, *args, **kwargs)
            raise ValueError("Value is out of range")
        return wrapper
    return decorator


def precision(number, prec=1):
    return math.floor(number*10**prec) / 10**prec


@range(-180, 180)
def degrees_to_proportion(degrees):
    return degrees / 180


class OnvifAbsoluteMove:
    def __init__(self, ip_addr: str, port: int, user: str, password: str):
        self.__camera = ONVIFCamera(ip_addr, port, user, password)
        self.__ptz = self.__camera.create_ptz_service()
        self.__media = self.__camera.create_media_service()
        self.__request = None

        self.__pan = 0
        self.__tilt = 0
        self.__zoom = 0
        self.is_active = False

        self.setup()

    @property
    def pan(self):
        return self.__pan

    @pan.setter
    def pan(self, value):
        self.__pan = value
        self.__request.Position.PanTilt.x = value
        self.do_move()

    @property
    def tilt(self):
        return self.__tilt

    @tilt.setter
    def tilt(self, value):
        self.__tilt = value
        self.__request.Position.PanTilt.y = value
        self.do_move()

    @property
    def zoom(self):
        return self.__zoom

    def setup(self):
        media_profile = self.__media.GetProfiles()[0]
        request = self.__ptz.create_type("GetConfigurationOptions")
        request.ConfigurationToken = media_profile.PTZConfiguration.token
        #ptz_configuration_options = self.__ptz.GetConfigurationOptions(request)

        self.__request = self.__ptz.create_type("AbsoluteMove")
        self.__request.ProfileToken = media_profile.token
        if self.__request.Position is None:
            self.__request.Position = self.__ptz.GetStatus({"ProfileToken": media_profile.token}).Position

        self.__pan = self.__request.Position.PanTilt.x
        self.__tilt = self.__request.Position.PanTilt.y
        self.__zoom = self.__request.Position.Zoom.x

    def do_move(self):
        if self.is_active:
            self.__ptz.Stop({"ProfileToken": self.__request.ProfileToken})
        self.is_active = True
        self.__ptz.AbsoluteMove(self.__request)

    def move_to(self, pan, tilt, zoom):
        self.__pan = pan
        self.__tilt = tilt
        self.__zoom = zoom
        self.__request.Position.PanTilt.x = pan
        self.__request.Position.PanTilt.y = tilt
        self.__request.Position.Zoom.x = zoom
        self.do_move()

    def increase_pan(self, step=STEP):
        self.__pan += step
        self.move_to(self.__pan, self.__tilt, self.__zoom)

    def increase_tilt(self, step=STEP):
        self.__tilt -= step
        self.move_to(self.__pan, self.__tilt, self.__zoom)

    def decrease_pan(self, step=STEP):
        self.__pan -= step
        self.move_to(self.__pan, self.__tilt, self.__zoom)

    def decrease_tilt(self, step=STEP):
        self.__tilt += step
        self.move_to(self.__pan, self.__tilt, self.__zoom)

    def increase_zoom(self, step=0.05):
        self.__zoom += step
        if self.__zoom > 1:
            self.__zoom = 1
        self.move_to(self.__pan, self.__tilt, self.__zoom)

    def decrease_zoom(self, step=0.05):
        self.__zoom -= step
        if self.__zoom < 0:
            self.__zoom = 0
        self.move_to(self.__pan, self.__tilt, self.__zoom)

    def stop_move(self):
        self.__ptz.Stop({"ProfileToken": self.__request.ProfileToken})


if __name__ == "__main__":
    keyboard_controller = KeyboardController()
    onvif_abs_move = OnvifAbsoluteMove(IP, PORT, USER, PASS)

    print(f"Pan: {onvif_abs_move.pan}, Tilt: {onvif_abs_move.tilt}, Zoom: {onvif_abs_move.zoom}")

    keyboard_controller.add_key_map('w', onvif_abs_move.increase_tilt, lambda: print(""))
    keyboard_controller.add_key_map('s', onvif_abs_move.decrease_tilt, lambda: print(""))
    keyboard_controller.add_key_map('a', onvif_abs_move.decrease_pan, lambda: print(""))
    keyboard_controller.add_key_map('d', onvif_abs_move.increase_pan, lambda: print(""))
    keyboard_controller.add_key_map('r', onvif_abs_move.increase_zoom, lambda: print(""))
    keyboard_controller.add_key_map('q', onvif_abs_move.decrease_zoom, lambda: print(""))
    keyboard_controller.loop()
    #print(f"Pan: {onvif_abs_move.pan}, Tilt: {onvif_abs_move.tilt}")
    #onvif_abs_move.tilt = -0.8 #degrees_to_proportion()
