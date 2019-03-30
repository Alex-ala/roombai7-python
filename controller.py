from roomba import Roomba
from mapper import Mapper


class Controller:
    def __init__(self, ip, blid, password, map_offset=None):
        self.map_offset = map_offset
        if self.map_offset is None:
            self.map_offset = {'x': 0, 'y': 0}
        self.roomba = Roomba(ip, blid, password)
        self.enable_mapping("/tmp/bind.png")
        self.roomba.connect()
        self.mapper = None

    def enable_mapping(self, image_drawmap_path, image_floorplan_path=None):
        self.mapper = Mapper(image_drawmap_path,
                             image_floorplan_path=image_floorplan_path,
                             offset=self.map_offset)
        self.mapper.reset_map()
        self.roomba.add_state_handler(self.mapper.update_map)
