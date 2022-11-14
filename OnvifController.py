from onvif import ONVIFCamera


class OnvifController:
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

        self.xmax = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].XRange.Max
        self.xmin = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].XRange.Min
        self.ymax = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].YRange.Max
        self.ymin = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].YRange.Min

    def do_move(self):
        if self.is_active:
            self.__ptz.Stop({"ProfileToken": self.__request.ProfileToken})
        self.is_active = True
        self.__ptz.ContinuousMove(self.__request)

    def move_up(self):
        self.__request.Velocity.PanTilt.x = 0
        self.__request.Velocity.PanTilt.y = self.ymax
        self.do_move()

    def move_down(self):
        self.__request.Velocity.PanTilt.x = 0
        self.__request.Velocity.PanTilt.y = self.ymin
        self.do_move()

    def move_left(self):
        self.__request.Velocity.PanTilt.x = self.xmin
        self.__request.Velocity.PanTilt.y = 0
        self.do_move()

    def move_right(self):
        self.__request.Velocity.PanTilt.x = self.xmax
        self.__request.Velocity.PanTilt.y = 0
        self.do_move()

    def stop_move(self):
        self.__ptz.Stop({"ProfileToken": self.__request.ProfileToken})
