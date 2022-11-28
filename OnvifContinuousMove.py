from onvif import ONVIFCamera
from KeyboardController import KeyboardController
from utils import read_settings

SPEED = 0.75  # 0...1


class OnvifContinuousMove:
    def __init__(self, ip_addr: str, port: int, user: str, password: str):
        self.__camera = ONVIFCamera(ip_addr, port, user, password)
        self.__ptz = self.__camera.create_ptz_service()
        self.__media = self.__camera.create_media_service()
        self.__request = None

        self.is_active = False

        self.xmin = 0
        self.xmax = 0
        self.ymin = 0
        self.ymax = 0
        self.zmax = 0
        self.zmin = 0

        self.setup()

    def setup(self):
        media_profile = self.__media.GetProfiles()[0]
        request = self.__ptz.create_type("GetConfigurationOptions")
        request.ConfigurationToken = media_profile.PTZConfiguration.token
        ptz_configuration_options = self.__ptz.GetConfigurationOptions(request)

        self.__request = self.__ptz.create_type("ContinuousMove")
        self.__request.ProfileToken = media_profile.token
        if self.__request.Velocity is None:
            self.__request.Velocity = self.__ptz.GetStatus({"ProfileToken": media_profile.token}).Position

        self.__request.Velocity.PanTilt.space = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].URI
        self.__request.Velocity.Zoom.space = ptz_configuration_options.Spaces.ContinuousZoomVelocitySpace[0].URI

        self.xmax = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].XRange.Max * SPEED
        self.xmin = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].XRange.Min * SPEED
        self.ymax = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].YRange.Max * SPEED
        self.ymin = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].YRange.Min * SPEED
        self.zmax = ptz_configuration_options.Spaces.ContinuousZoomVelocitySpace[0].XRange.Max * SPEED
        self.zmin = ptz_configuration_options.Spaces.ContinuousZoomVelocitySpace[0].XRange.Min * SPEED

    def send_move_request(self):
        if self.is_active:
            self.__ptz.Stop({"ProfileToken": self.__request.ProfileToken})
        self.is_active = True
        self.__ptz.ContinuousMove(self.__request)

    def move(self, pan_speed=0, tilt_speed=0, zoom_speed=0):
        self.__request.Velocity.PanTilt.x = pan_speed
        self.__request.Velocity.PanTilt.y = tilt_speed
        self.send_move_request()

    def move_up(self):
        self.__request.Velocity.PanTilt.x = 0
        self.__request.Velocity.PanTilt.y = self.ymax
        self.send_move_request()

    def move_down(self):
        self.__request.Velocity.PanTilt.x = 0
        self.__request.Velocity.PanTilt.y = self.ymin
        self.send_move_request()

    def move_left(self):
        self.__request.Velocity.PanTilt.x = self.xmin
        self.__request.Velocity.PanTilt.y = 0
        self.send_move_request()

    def move_right(self):
        self.__request.Velocity.PanTilt.x = self.xmax
        self.__request.Velocity.PanTilt.y = 0
        self.send_move_request()

    def increase_zoom(self):
        self.__request.Velocity.PanTilt.x = 0
        self.__request.Velocity.PanTilt.y = 0
        self.__request.Velocity.Zoom.x = self.zmax
        self.send_move_request()

    def decrease_zoom(self):
        self.__request.Velocity.PanTilt.x = 0
        self.__request.Velocity.PanTilt.y = 0
        self.__request.Velocity.Zoom.x = self.zmin
        self.send_move_request()

    def stop_move(self):
        self.__ptz.Stop({"ProfileToken": self.__request.ProfileToken})


if __name__ == "__main__":
    settings = read_settings("security.txt")

    ip = settings["ip"]
    port = settings["port"]
    login = settings["login"]
    password = settings["password"]

    controller = KeyboardController()
    onvif_controller = OnvifContinuousMove(ip, port, login, password)

    controller.add_key_map('w', onvif_controller.move_up, onvif_controller.stop_move)
    controller.add_key_map('s', onvif_controller.move_down, onvif_controller.stop_move)
    controller.add_key_map('a', onvif_controller.move_left, onvif_controller.stop_move)
    controller.add_key_map('d', onvif_controller.move_right, onvif_controller.stop_move)
    controller.add_key_map('e', onvif_controller.increase_zoom, onvif_controller.stop_move)
    controller.add_key_map('q', onvif_controller.decrease_zoom, onvif_controller.stop_move)
    controller.loop()
