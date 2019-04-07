import paho.mqtt.client as mqtt
import ssl
import logging
import json
from time import time


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
    cycles = {"charge": "Charging",
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
        self.state = dict()
        self.connected = False
        self.on_state_change = list()

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
                # self.mqtt_client.loop_forever()
            except Exception as e:
                self.log.error("Error connecting to Roomba: "+str(e))
                return False

    def disconnect(self):
        self.mqtt_client.disconnect()

    def reconnect(self):
        self.disconnect()
        self.connect()

    def add_state_handler(self, handler):
        self.on_state_change.append(handler)

    def on_message(self, client, userdata, message):
        try:
            new_state = json.loads(message.payload.decode(' UTF-8'))['state']['reported']
            self.state.update(new_state)
        except Exception as e:
            print('Error reading message from robot: '+str(e)+' --- '+message.payload.decode(' UTF-8'))
        self.on_state_change_handler()

    def on_connect(self, client, userdata, flags, rc):
        if rc != 0:
            print("Error connecting to Roomba MQTT")
            self.connected = False
        else:
            self.connected = True

    def on_disconnect(self, client, userdata, rc):
        self.state = self.states["disconnected"]

    def on_state_change_handler(self):
        for handle in self.on_state_change:
            handle(self)

    def _send_command(self, topic, command):
        message = dict()
        message['initiator'] = 'localApp'
        message['time'] = int(time())
        if topic == 'delta':
            message['state'] = command
        else:
            message['command'] = command
        self.mqtt_client.publish(topic, json.dumps(message))

    def send_command(self, command):
        self._send_command('cmd', command)

    def send_property(self, properties):
        self._send_command('delta', properties)

    # Set settings

    '''
    :param enable: Enable internal mapping feature
    This requires (and sets) to allow upload of the data to cloud. Your Roomba will upload map data into Roomba AWS.
    This feature also works offline if You prevent map upload via firewall. You wont have access to the internal map,
    but Your Roomba still learns the area. 
    '''
    def set_internal_mapping(self, enable):
        state = {'pmapLearningAllowed': enable, 'mapUploadAllowed': enable}
        self.send_property(state)

    def set_two_passes(self, enable):
        state = {"twoPass": enable, "noAutoPasses": not enable}
        self.send_property(state)

    def set_stop_on_full_bin(self, enable):
        state = {"binPause": enable}
        self.send_property(state)

    def set_audio(self, enable):
        state = {"audio": {"active": enable}}
        self._send_command('delta', state)

    '''
    :param language: Language ID supported by Roomba like en-GB en-US de-DE etc
    '''
    def set_language(self, language):
        if language in self.state['langs']:
            state = {"language": self.state['langs'][language]}
            self.send_property(state)
        else:
            return False

    '''
    :param start_times_with_params: Cleaning Schedule in the following form:
    {
        "cmd": {
            "command": "start",             # I dont know if this is modifiable
            "params": {
                "carpetBoost": false,       # Enable vacuum boost on carpets
                "noAutoPasses": false,      # Disable automatic decision whether to clean an area twice
                "twoPass": false,           # Clean every area twice
                "openOnly": true,           # Do not clean edges and close to walls
                "vacHigh": false            # Suck more!!!!
            }
        },
        "enabled": true,                    # Enable this schedule
        "start": {
            "day": [1, 3, 5],               # Day of week, seems 1=Monday
            "hour": 9,                      # Hour of starting time
            "min": 0                        # Minute of starting time
        },
        "type": 0                           # No clue what types there are. Cleaning normally is 0
    }
    :return: 
    '''
    def set_cleaning_schedule(self, start_times_with_params):
        state = {"cleanSchedule2": start_times_with_params}
        self.send_property(state)

    # Get state

    def get_languages(self):
        return self.state.get('langs')

    def get_cleaning_schedule(self):
        return self.state.get('cleaningSchedule2')

    def get_stop_on_full_bin(self):
        return self.state.get('binPause')

    def get_passes(self):
        try:
            if self.state['noAutoPasses']:
                return 'Automatic'
            else:
                if self.state['twoPass']:
                    return 'Two passes'
                else:
                    return 'Single pass'
        except KeyError:
            return None

    def get_mapping_enabled(self):
        try:
            if not self.state['mapUploadAllowed']:
                return False
            else:
                if self.state['pmapLearningAllowed']:
                    return True
        except KeyError:
            return False
        return False

    def get_total_state(self):
        return self.state

    def get_bin_state(self):
        try:
            if self.state['bin']['present'] == 0:
                return "Not present"
            if not self.state['cap']['binFullDetect'] == 1:
                return "Present"
            else:
                if self.state['bin']['full'] == 0:
                    return "Not full"
                else:
                    return "Full"
        except KeyError:
            return None

    def get_battery_level(self):
        return self.state.get('batPct', 0)

    def get_name(self):
        return self.state.get('name', 'roomba')

    def get_mission_name(self):
        try:
            mission = self.state['cleanMissionStatus']['cycle']
        except KeyError:
            mission = None
        return mission

    def get_mission_state(self):
        try:
            mission = self.state['cleanMissionStatus']['phase']
        except KeyError:
            mission = None
        return mission

    '''
    When you look at the base:
    (0,0) is a rough meter in front of the base
    (-x,0) is behind (0,0), can be behind the base
    (0,-x) is to the right of the base
    Theta: 
    0 is facing away from base
    -90 is facing left from base (when you look at base)
    90 is facing right from base
    '''
    def get_position(self):
        if 'pose' in self.state:
            return self.state['pose']
        else:
            return {'point': {'x': 0, 'y': 0}, 'theta': 0}

    # Commands

    def start_training(self):
        try:
            if self.state['pmapLearningAllowed']:
                self.send_command('train')
                return True
            else:
                return False
        except KeyError:
            return False

    def start_clean(self):
        self.send_command('clean')

    def quick_clean(self):
        self.send_command('quick')

    def spot_clean(self):
        self.send_command('spot')

    def stop(self):
        self.send_command('stop')

    def pause(self):
        self.send_command('pause')

    def resume(self):
        self.send_command('resume')

    def dock(self):
        self.send_command('dock')

    def locate_with_beep(self):
        self.send_command('find')

    def factory_reset(self):
        self.send_command('wipe')
