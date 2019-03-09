import threading
import paho.mqtt.client as mqtt
import ssl
import logging

class Config(object):
    def __init__(self, address, blid, password,
                 continuous=True, mapping=False,
                 ssl_cert="/etc/ssl/certs/ca-certificates.crt"):
        self.address = address
        self.blid = blid
        self.password = password
        self.continuous = continuous
        self.mapping = mapping
        self.ssl_cert = ssl_cert


class Roomba(object):
    states = {"charge": "Charging",
              "new": "New Mission",
              "run": "Running",
              "resume": "Running",
              "hmMidMsn": "Recharging",
              "recharge": "Recharging",
              "stuck": "Stuck",
              "hmUsrDock": "User Docking",
              "dock": "Docking",
              "dockend": "Docking - End Mission",
              "cancelled": "Cancelled",
              "stop": "Stopped",
              "pause": "Paused",
              "hmPostMsn": "End Mission",
              "disconnected": "Disconnected",
              "":  None}
    bin_states = {
        0: "Empty",
        1: "Full",
        2: "Removed"
    }

    _ErrorMessages = {
        0: "None",
        1: "Uneven ground. Place on a flat surface, and then press Clean - "
           "The left wheel for Roomba is hanging down or Roomba is stuck.",
        2: "Clear the brushes, then press Clean - The multi-surface rubber brushes cannot spin.",
        3: "Uneven ground. Place on a flat surface, and then press Clean - "
           "The right wheel for Roomba is hanging down or Roomba is stuck",
        4: "Clear the wheels, then press Clean - Left wheel stalled. Left wheel is jammed",
        5: "Clear the wheels, then press Clean - Right wheel stalled. Left wheel is jammed",
        6: "Drop off detected. Move to a new area, and then press Clean - "
           "Constant cliff detected. Check that cliff sensors are clear of debris",
        7: "Wheel problem. See the app for help - Left wheel on the ground and robot cannot sense",
        8: "Vacuum problem. See the app for help - Vacuum has poor suction",
        9: "Tap the bumper to unstick, then press Clean - Constant Bump. Bumper is jammed with debris or dislodged",
        10: "Wheel problem. See the app for help - Right wheel on the ground and robot cannot sense",
        11: "Vacuum problem. See the app for help - Vacuum motor not activating",
        12: "Drop off detected. Move to a new area, and then press Clean - Cliff Sensors",
        13: "Uneven ground. Place on a flat surface, and then press Clean - Both wheels on uneven surface",
        14: "Reinstall the bin, then press Clean - "
            "Bin not present in robot. Ensure filter is installed in bin. Check bin detect switch",
        15: "Internal board error",
        16: "Move to a flat surface, then press Clean - Robot bumped upon start. Bumper possibly dislodged",
        17: "Navigation problem. See the app for help - "
            "The robot entered an unknown area and got lost while cleaning and unable to return to Home Base",
        18: "Docking problem. Place on the home base to charge - "
            "Cleaning is complete, but the robot was unable to dock onto the Home Base",
        19: "Undocking problem. Clear obstacles, and then press Clean - "
            "Failed to undock. May have bumped something near Home Base",
        20: "Roomba is experiencing an internal communication error.",
        21: "Lost communication with mobility board. Reboot robot. If persists replace",
        22: "Move to a new area, then press Clean - Roomba's Environment",
        23: "Battery Authentication Failure. Ensure battery is iRobot authentic",
        24: "Place on a flat surface, then press Clean - Roomba's Environment",
        25: "Internal Board Error. Reboot robot. If persists replace",
        26: "Vacuum stall. Filter clog possible",
        27: "Vacuum Motor Over-temp: Clogged filter or bad impeller of vacuum motor",
        29: "Error while upgrading software",
        30: "Vacuum failed to start",
        31: "Internal Board Error. Press CLEAN to restart.",
        32: "Smart Map version on robot does not match map saved on App",
        33: "Robot unable to clean path detailed in Smart Map. Path may be blocked",
        34: "Internal COMM's Error. Reboot robot. If persists replace",
        36: "Bin Full Sensor not Cleared when debris evacuated",
        38: "Power Comms. Issue. Reboot robot. If persists replace",
        39: "Power Comms. Issue. Reboot robot. If persists replace",
        40: "Robot Stuck in Virtual Wall Beam",
        41: "Mission timed out before completion. Press CLEAN to restart mission",
        42: "Failed to re-localize when direct cleaning",
        43: "Started in Home Base IR Halo off Home Base",
        46: "Robot Ended Mission with low battery not on dock",
        47: "Invalid Robot Calibration. Reboot robot.",
        48: "Invalid Robot Calibration. Reboot robot."
    }

    def __init__(self, address, blid, password, continuous=True):
        self.log = logging.getLogger("roomba.__main__")
        self.config = Config(address, blid, password, continuous=continuous)
        self.mqtt_client = None
        self.state = None
        self.position = (0, 0, 0)
        self.battery_level = 0
        self.bin_state = 0
        self.thread = None

    '''Initiate MQTT connection'''
    def connect(self):
        self.mqtt_client = mqtt.Client(client_id=self.config.blid,
                                       clean_session=False,
                                       protocol=mqtt.MQTTv311)
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.on_disconnect = self.on_disconnect
        try:
            self.mqtt_client.tls_set(self.config.ssl_cert,
                                     cert_reqs=ssl.CERT_NONE,
                                     tls_version=ssl.PROTOCOL_TLSv1)
        except (ValueError, IOError):
            self.mqtt_client._ssl_context = None
            context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
            context.verify_mode = ssl.CERT_NONE
            context.load_default_certs()
            self.mqtt_client.tls_set_context(context)
        self.mqtt_client.tls_insecure_set(True)
        self.mqtt_client.username_pw_set(self.config.blid, self.config.password)
        if not self.config.continuous:
            raise NotImplementedError
        else:
            try:
                self.mqtt_client.connect(self.config.address, 8883, 60)
                self.mqtt_client.loop_start()
            except:
                self.log.error("Error connecting to Roomba")
                return False

    def on_message(self, client, userdata, message):
        print(message)

    def on_connect(self, client, userdata, flags, rc):
        if rc != 0:
            self.log.error("Error connecting to Roomba MQTT")

    def on_disconnect(self, client, userdata, rc):
        self.state = self.states["disconnected"]

