"""
The following provides a live feed using the camera in the ESP32
:urls:
    Based on: https://github.com/Freenove/Freenove_Ultimate_Starter_Kit_for_ESP32/blob/master/Python/Python_Codes/30.1_Camera_WebServer/picoweb_video.py
    Directions: https://github.com/Freenove/Freenove_Ultimate_Starter_Kit_for_ESP32/blob/master/Python/Python_Tutorial.pdf
:requirements:
    * Download Thorny IDE: https://thonny.org/
    * Clone: https://github.com/Freenove/Freenove_Ultimate_Starter_Kit_for_ESP32
:process:
    0. Connect to PC & validate it's viewable via Device Manager
    1. In Thorny, configure interpreter to support Camera (micropython_camera_feeeb5ea3_esp32_idf4_4)
        --> Otherwise imports will not work
    2. import camera code from git clone into ESP32
    3. In boot file, insert publisher code
    4. execute boot file - note
"""
import camera
import gc
import network
import picoweb
import utime


class WifiNetworking:
    def __init__(self, ssid: str, passwd: str):
        """
        Class configuring WiFi Networking for pymicro
        :args:
            ssid:str - WiFi network name
            passwd:str - Password for wifi network
        :params:
            self.ssid:str - ssid
            self.passwd:str - passwd
            self.sta_if:class.WLAN - declaration of WLAN
        """
        self.ssid = ssid
        self.passwd = passwd
        self.sta_if = None

    def __declare_wlan_sta(self) -> bool:
        """
        Create connection to WLAN
        :params:
            status:bool
        :return:
            True if sucess
            False (with Error) if Fails
        """
        status = True
        try:
            self.sta_if = network.WLAN(network.STA_IF)
        except Exception as error:
            status = False
            print(f"Failed to declare wlan (Error: {error})")
        else:
            self.sta_if.active(True)
        return status

    def __get_ip(self) -> str:
        """
        Get IP address of pymicro device
        """
        try:
            return self.sta_if.ifconfig()[0]
        except Exception as error:
            print(f"Failed to get IP Address (Error: {error}")

    def connect(self):
        """
        Connect to WiFi based on SSID and password
        """
        sta_status = self.__declare_wlan_sta()
        if sta_status is True and not self.sta_if.isconnected():
            self.sta_if.connect(self.ssid, self.passwd)

        start = utime.time()
        while not self.sta_if.isconnected():
            utime.sleep(1)
            if utime.time() - start > 5:
                print("connect timeout!")
                break
        if self.sta_if.isconnected():
            ip_addr = self.__get_ip()
            if ip_addr is not None:
                print(f"Connected against IP: {ip_addr}")
            else:
                print("Connected, Unknown IP address...")

    def disconnect(self):
        """
        Disconnect from WiFi
        """
        if self.sta_if.isconnected():
            try:
                self.sta_if.disconnect()
            except Exception as error:
                print(f'Failed to disconnect from {self.ssid} (Error: {error})')
            else:
                print(f'Disconnected from {self.ssid}')


# The following was taken directly from the Github repo
def camera_init():
    # Disable camera initialization
    camera.deinit()
    # Enable camera initialization
    camera.init(0, d0=4, d1=5, d2=18, d3=19, d4=36, d5=39, d6=34, d7=35,
                format=camera.JPEG, framesize=camera.FRAME_VGA,
                xclk_freq=camera.XCLK_20MHz,
                href=23, vsync=25, reset=-1, pwdn=-1,
                sioc=27, siod=26, xclk=21, pclk=22, fb_location=camera.PSRAM)

    camera.framesize(camera.FRAME_VGA)  # Set the camera resolution
    # The options are the following:
    # FRAME_96X96 FRAME_QQVGA FRAME_QCIF FRAME_HQVGA FRAME_240X240
    # FRAME_QVGA FRAME_CIF FRAME_HVGA FRAME_VGA FRAME_SVGA
    # FRAME_XGA FRAME_HD FRAME_SXGA FRAME_UXGA
    # Note: The higher the resolution, the more memory is used.
    # Note: And too much memory may cause the program to fail.

    camera.flip(1)  # Flip up and down window: 0-1
    camera.mirror(1)  # Flip window left and right: 0-1
    camera.saturation(0)  # saturation: -2,2 (default 0). -2 grayscale
    camera.brightness(0)  # brightness: -2,2 (default 0). 2 brightness
    camera.contrast(0)  # contrast: -2,2 (default 0). 2 highcontrast
    camera.quality(10)  # quality: # 10-63 lower number means higher quality
    # Note: The smaller the number, the sharper the image. The larger the number, the more blurry the image

    camera.speffect(camera.EFFECT_NONE)  # special effects:
    # EFFECT_NONE (default) EFFECT_NEG EFFECT_BW EFFECT_RED EFFECT_GREEN EFFECT_BLUE EFFECT_RETRO
    camera.whitebalance(camera.WB_NONE)  # white balance
    # WB_NONE (default) WB_SUNNY WB_CLOUDY WB_OFFICE WB_HOME


# HTTP Response Content
index_web = """
HTTP/1.0 200 OK\r\n
<html>
  <head>
    <title>Video Streaming</title>
  </head>
  <body>
    <h1>Video Streaming Demonstration</h1>
    <img src="/video" margin-top:100px; style="transform:rotate(180deg)"; />
  </body>
</html>
"""


# HTTP Response
def index(req, resp):
    # You can construct an HTTP response completely yourself, having
    yield from resp.awrite(index_web)


# Send camera pictures
def send_frame():
    buf = camera.capture()
    yield (b'--frame\r\n'
           b'Content-Type: image/jpeg\r\n\r\n'
           + buf + b'\r\n')
    del buf
    gc.collect()


# Video transmission
def video(req, resp):
    yield from picoweb.start_response(resp, content_type="multipart/x-mixed-replace; boundary=frame")
    while True:
        yield from resp.awrite(next(send_frame()))
        gc.collect()


ROUTES = [
    # You can specify exact URI string matches...
    ("/", index),
    ("/video", video),
]


def main():
    ssid = input('WiFi SSID: ')
    passwd = input('WiFi Password: ')
    networking = WifiNetworking(ssid=ssid, passwd=passwd)
    networking.connect()
    camera_init()
    app = picoweb.WebApp(__name__, ROUTES)
    app.run(debug=1, port=8080, host="0.0.0.0")
    # networking.disconnect()


if __name__ == '__main__':
    main()

