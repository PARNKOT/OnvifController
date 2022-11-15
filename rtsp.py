import multiprocessing
import threading
import time

import cv2

#uri = "rtsp://admin:Pa$$w0rd@10.1.1.14/Streaming/Channel/101"
#video_capture = cv2.VideoCapture(uri, cv2.CAP_FFMPEG)


class RtspStreamer(threading.Thread):
    def __init__(self, uri: str, delay: float = 0.0, scale: float = 1.0):
        super().__init__(target=self.process, name="Rtsp streamer")
        self.uri = uri
        self.video_capture = None

        self.delay = delay
        self.scale = scale

        self.success: bool = False
        self.image = None

    def grabber(self):
        success, image = self.video_capture.read()
        if success:
            self.image = self.resize_image(image)
            self.success = success

    def resize_image(self, image):
        width = int(image.shape[1]*self.scale)
        height = int(image.shape[0]*self.scale)
        return cv2.resize(image, (width, height), interpolation = cv2.INTER_AREA)

    def process(self):
        self.video_capture = cv2.VideoCapture(self.uri, cv2.CAP_FFMPEG)
        while True:
            self.grabber()
            if self.delay:
                time.sleep(self.delay)

    def get_image(self):
        return self.image

    def start(self):
        super().start()


if __name__ == "__main__":
    uri = "rtsp://admin:Pa$$w0rd@10.1.1.14/Streaming/Channels/101"
    streamer = RtspStreamer(uri, scale=0.5)
    streamer.start()
    while True:
        if streamer.success:
            cv2.imshow("Frame", streamer.get_image())
            cv2.waitKey(1)
            time.sleep(0.1)
