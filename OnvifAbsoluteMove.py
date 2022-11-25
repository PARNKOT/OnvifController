import math
import time

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
    def __init__(self, zoom_max):
        self.__camera = None
        self.__ptz = None
        self.__media = None
        self.__imaging = None  # TEST
        self.__request = None
        self.__lens_request = None # TEST
        self.last_time_command = time.time()

        self.__pan = 0
        self.__tilt = 0
        self.__zoom = 0
        self.__step = 0.005
        self.zoom_max = zoom_max - 1
        self._lens_focus_mode = None
        self.is_active = False

    @property
    def pan(self):
        return self.__pan

    @pan.setter
    def pan(self, value):
        if -180 < value < 180:
            self.__pan = value

    @property
    def tilt(self):
        return self.__tilt

    @tilt.setter
    def tilt(self, value):
        if -20 < value < 45:
            self.__tilt = value

    @property
    def zoom(self):
        return self.__zoom

    @property
    def step(self):
        return self.__step

    @step.setter
    def step(self, value):
        if 0 <= value <= 1:
            self.__step = value
        else:
            raise ValueError("Step value is out of bounds [0,1]")

    def connect(self, ip_addr: str, port: int, user: str, password: str):
        self.__camera = ONVIFCamera(ip_addr, port, user, password)
        self.__ptz = self.__camera.create_ptz_service()
        self.__media = self.__camera.create_media_service()
        self.__imaging = self.__camera.create_imaging_service()
        self.setup()

    def setup(self):
        media_profile = self.__media.GetProfiles()[0]
        video_source_token = self.__media.GetVideoSources()[0].token
        #request = self.__ptz.create_type("GetConfigurationOptions")
        #request.ConfigurationToken = media_profile.PTZConfiguration.token
        #ptz_configuration_options = self.__ptz.GetConfigurationOptions(request)

        self.__request = self.__ptz.create_type("AbsoluteMove")
        self.__request.ProfileToken = media_profile.token
        if self.__request.Position is None:
            self.__request.Position = self.__ptz.GetStatus({"ProfileToken": media_profile.token}).Position

        self.__pan = self.__request.Position.PanTilt.x
        self.__tilt = self.__request.Position.PanTilt.y
        self.__zoom = self.__request.Position.Zoom.x

        self.__lens_request = self.__imaging.create_type("SetImagingSettings")  # TEST
        self.__lens_request.VideoSourceToken = video_source_token
        self.__lens_request.ImagingSettings = self.__imaging.GetImagingSettings({"VideoSourceToken": video_source_token})
        print()

    def set_autofocus(self):
        mode = self.__lens_request.ImagingSettings.Focus.AutoFocusMode
        if mode.lower() == "manual":
            self.__lens_request.ImagingSettings.Focus.AutoFocusMode = "AUTO"
            self.__imaging.SetImagingSettings(self.__lens_request)
            print("Autofocus enabled")
        else:
            print("Autofocus is already enabled")

    def unset_autofocus(self):
        mode = self.__lens_request.ImagingSettings.Focus.AutoFocusMode
        if mode.lower() == "auto":
            self.__lens_request.ImagingSettings.Focus.AutoFocusMode = "MANUAL"
            self.__imaging.SetImagingSettings(self.__lens_request)
            print("Autofocus disabled")
        else:
            print("Autofocus is already disabled")

    def do_move(self):
        print(f"Pan: {self.pan*180}, Tilt: {self.tilt*90}, Zoom: {int(self.zoom*35) + 1}")
        if self.is_active:
            self.__ptz.Stop({"ProfileToken": self.__request.ProfileToken})
        self.is_active = True
        self.__ptz.AbsoluteMove(self.__request)

    def move_to(self, pan, tilt, zoom):
        current_time = time.time()
        if (current_time - self.last_time_command) > 0.5:
            self.pan = pan
            self.tilt = tilt
            self.__zoom = zoom
            self.__request.Position.PanTilt.x = self.pan
            self.__request.Position.PanTilt.y = self.tilt
            self.__request.Position.Zoom.x = self.__zoom
            self.last_time_command = current_time
            self.do_move()

    def increase_pan(self):
        self.move_to(self.pan + self.step, self.__tilt, self.__zoom)

    def increase_tilt(self):
        self.move_to(self.__pan, self.__tilt - self.step, self.__zoom)

    def decrease_pan(self):
        self.move_to(self.__pan - self.step, self.__tilt, self.__zoom)

    def decrease_tilt(self):
        self.move_to(self.__pan, self.__tilt + self.step, self.__zoom)

    def increase_zoom(self):
        new_zoom = self.zoom + 1/self.zoom_max
        if new_zoom > 1:
            new_zoom = 1
        self.move_to(self.__pan, self.__tilt, new_zoom)

    def decrease_zoom(self):
        new_zoom = self.zoom - 1/self.zoom_max
        if new_zoom < 0:
            new_zoom = 0
        self.move_to(self.__pan, self.__tilt, new_zoom)

    def stop_move(self):
        pass


if __name__ == "__main__":
    keyboard_controller = KeyboardController()
    onvif_abs_move = OnvifAbsoluteMove(36)
    onvif_abs_move.connect(IP, PORT, USER, PASS)
    onvif_abs_move.step = 0.005
    onvif_abs_move.set_autofocus()

    print(f"Pan: {onvif_abs_move.pan}, Tilt: {onvif_abs_move.tilt}, Zoom: {onvif_abs_move.zoom}")

    keyboard_controller.add_key_map('w', onvif_abs_move.increase_tilt, onvif_abs_move.stop_move, once_call=False)
    keyboard_controller.add_key_map('s', onvif_abs_move.decrease_tilt, onvif_abs_move.stop_move, once_call=False)
    keyboard_controller.add_key_map('a', onvif_abs_move.decrease_pan, onvif_abs_move.stop_move, once_call=False)
    keyboard_controller.add_key_map('d', onvif_abs_move.increase_pan, onvif_abs_move.stop_move, once_call=False)
    keyboard_controller.add_key_map('r', onvif_abs_move.increase_zoom, onvif_abs_move.stop_move, once_call=False)
    keyboard_controller.add_key_map('q', onvif_abs_move.decrease_zoom, onvif_abs_move.stop_move, once_call=False)
    keyboard_controller.loop()
    #print(f"Pan: {onvif_abs_move.pan}, Tilt: {onvif_abs_move.tilt}")
    #onvif_abs_move.tilt = -0.8 #degrees_to_proportion()
