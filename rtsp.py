import multiprocessing
import threading
import time

import cv2
from PIL import ImageTk, Image

from utils import read_settings


class RtspStreamer(threading.Thread):
    def __init__(self, uri: str, delay: float = 0.0, scale: float = 1.0):
        super().__init__(target=self.process, name="Rtsp streamer")
        self.uri = uri
        self.video_capture = cv2.VideoCapture(uri, cv2.CAP_FFMPEG)

        self.stop_event = threading.Event()
        self.stop_event.set()

        self.delay = delay
        self.scale = scale

        self.success: bool = False
        self.original_image = None
        self.image = None

    def grabber(self):
        success, image = self.video_capture.read()
        if success:
            self.original_image = image
            self.image = self.resize_image(image)
            self.success = success

    def resize_image(self, image):
        width = int(image.shape[1]*self.scale)
        height = int(image.shape[0]*self.scale)
        return cv2.resize(image, (width, height), interpolation = cv2.INTER_AREA)

    def process(self):
        while self.stop_event.is_set():
            self.grabber()
            if self.delay:
                time.sleep(self.delay)
        else:
            print("RTSP streamer is stopped")

    def get_image(self):
        return self.image.copy()

    def get_image_settings(self, original=False):
        shape = None
        if original:
            shape = self.original_image.shape
        else:
            shape = self.image.shape
        return ImageSettings(width=int(shape[1]), height=int(shape[0]), layers_number=int(shape[2]))

    def get_as_tkinter_image(self):
        b, g, r = cv2.split(self.get_image())
        image = cv2.merge((r, g, b))
        image_new = Image.fromarray(image)
        imgtk = ImageTk.PhotoImage(image=image_new)
        return imgtk

    def stop(self):
        self.stop_event.clear()


class ImageSettings:
    def __init__(self, width: int = 0, height: int = 0, layers_number: int = 0):
        self.width = width
        self.height = height
        self.layers_number = layers_number

    def __str__(self):
        return f"Image setting: width = {self.width}, height = {self.height}, layers = {self.layers_number}"


if __name__ == "__main__":
    settings = read_settings("security.txt")

    ip = settings["ip"]
    port = settings["port"]
    login = settings["login"]
    password = settings["password"]

    uri = f"rtsp://{login}:{password}@{ip}/Streaming/Channels/101"
    #bgs_method = cv2.createBackgroundSubtractorGSOC()

    streamer = RtspStreamer(uri, scale=0.5)
    streamer.start()
    while True:
        if streamer.success:
            image = streamer.get_image()
            #foreground_mask = bgs_method.apply(image)
            #background_img = bgs_method.getBackgroundImage()

            cv2.imshow("Frame", image)
            #cv2.imshow("Foreground", foreground_mask)
            #cv2.imshow("Background", background_img)
            cv2.waitKey(1)

