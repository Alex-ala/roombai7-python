from roombai7.roomba import Roomba
from roombai7.mapper import Mapper


class Controller:
    def __init__(self, ip, blid, password, map_offset=None):
        self.map_offset = map_offset
        if self.map_offset is None:
            self.map_offset = {'x': 0, 'y': 0}
        self.roomba = Roomba(ip, blid, password)
        self.mapper = None

    def enable_mapping(self, image_drawmap_path, image_floorplan_path=None):
        self.mapper = Mapper(image_drawmap_path,
                             image_floorplan_path=image_floorplan_path,
                             offset=self.map_offset)
        self.mapper.reset_map()
        self.roomba.add_state_handler(self.mapper.update_map)

    def connect(self):
        self.roomba.connect()

    def reconnect(self):
        self.roomba.reconnect()

    def disconnect(self):
        self.roomba.disconnect()

    def is_connected(self):
        return self.roomba.connected

    def start_training(self):
        return self.roomba.start_training()

    def start_clean(self):
        self.roomba.start_clean()

    def quick_clean(self):
        self.roomba.quick_clean()

    def spot_clean(self):
        self.roomba.spot_clean()

    def stop(self):
        self.roomba.stop()

    def pause(self):
        self.roomba.pause()

    def resume(self):
        self.roomba.resume()

    def dock(self):
        self.roomba.dock()

    def locate_with_beep(self):
        self.roomba.locate_with_beep()

    def set_cleaning_schedule(self, start_times_with_params):
        self.roomba.set_cleaning_schedule(start_times_with_params)

    def enable_internal_mapping(self):
        self.roomba.set_internal_mapping(True)

    def disable_internal_mapping(self):
        self.roomba.set_internal_mapping(False)

    def set_two_passes(self, enable):
        self.roomba.set_two_passes(enable)

    def set_stop_on_full_bin(self, enable):
        self.roomba.set_stop_on_full_bin(enable)

    def get_battery_level(self):
        return self.roomba.get_battery_level()

    def get_name(self):
        return self.roomba.get_name()

    def get_mission_name(self):
        return self.roomba.get_mission_name()

    def get_mission_state(self):
        return self.roomba.get_mission_state()

    def get_bin_state(self):
        return self.roomba.get_bin_state()

    def get_position(self):
        return self.roomba.get_position()