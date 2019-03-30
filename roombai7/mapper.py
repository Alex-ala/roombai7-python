from PIL import Image, ImageDraw


class Mapper(object):

    POSITION_CIRCLE_WIDTH = 5

    def __init__(self, image_drawmap_plan, image_floorplan_path=None, offset=None):
        self.floorplan_path = image_floorplan_path
        self.drawmap_path = image_drawmap_plan
        self.drawmap = None
        self.offset = offset
        if self.floorplan_path is None:
            self.floorplan = Image.new(mode='RGBA', size=(5000, 5000))
            self.offset = (2500, 2500)
        else:
            self.floorplan = Image.open(self.floorplan_path, mode='r')

    def reset_map(self):
        self.drawmap = self.floorplan.copy()
        self.draw_circle((0, 0), (30, 144, 255, 255))
        self.drawmap.save(self.drawmap_path)

    def update_map(self, roomba):
        real_pos = roomba.get_position()
        pos = (real_pos['point']['x'] + self.offset[0],
               real_pos['point']['y'] + self.offset[1])
        self.draw_circle(pos, (124, 252, 0, 255))
        self.drawmap.save(self.drawmap_path)

    def draw_circle(self, pos, color):
        draw = ImageDraw.Draw(self.drawmap)
        draw.ellipse((pos[0] - Mapper.POSITION_CIRCLE_WIDTH,
                      pos[1] - Mapper.POSITION_CIRCLE_WIDTH,
                      pos[0] + Mapper.POSITION_CIRCLE_WIDTH,
                      pos[1] + Mapper.POSITION_CIRCLE_WIDTH),
                     fill=color)
        del draw
