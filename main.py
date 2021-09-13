from sys import platform
from user_actions import on_keyboard_up
from kivy.config import Config
Config.set('graphics', 'width', '900')
Config.set('graphics', 'height', '400')

from kivy.app import App
from kivy.core.audio import SoundLoader
from kivy.uix.relativelayout import RelativeLayout
from kivy.properties import NumericProperty
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Line, Quad
from kivy.properties import Clock, ObjectProperty, StringProperty
from kivy.core.window import Window
from kivy.lang import Builder
import random

Builder.load_file('menu.kv')

class MainWidget(RelativeLayout):
    from transform import transform, transform_3D
    from user_actions import on_keyboard_down, on_keyboard_up, on_touch_down, on_touch_up, keyboard_closed
    menu_screen = ObjectProperty()
    perspective_point_x = NumericProperty(0)
    perspective_point_y = NumericProperty(0)
    
    V_NB_LINES = 15
    V_LINES_SPACING = .2 # percentage in screen width
    vertical_lines = []

    H_NB_LINES = 6
    H_LINES_SPACING = .2 # percentage in screen height
    horizontal_lines = []

    game_speed = .008
    current_offset = 0
    current_loop = 0

    move_speed = 0
    movement = 0

    NB_TILES = 8
    tiles = []
    tile_coordinates = []

    SHIP_WIDTH = .1
    SHIP_HEIGHT = .035
    SHIP_BASE = 0.04
    ship = None
    ship_coordinate = [(0,0), (0,0), (0,0), (0,0)]

    title = StringProperty("N E O N      S P A C E")
    button = StringProperty("Start!")
    score = StringProperty("Score: 0")
    game_over = True

    sound_impace = None
    sound_music = None

    def __init__(self, **kwargs):
        super(MainWidget, self).__init__(**kwargs)
        self.init_audio()
        self.init_vertical_line()
        self.init_horizontal_line()
        self.init_tiles()
        self.init_ship()
        self.generate_starting_tile()
        self.generate_tiles_coordinates()



        if self.is_desktop():
            self._keyboard = Window.request_keyboard(self.keyboard_closed, self)
            self._keyboard.bind(on_key_down=self.on_keyboard_down)
            self._keyboard.bind(on_key_up=self.on_keyboard_up)

        Clock.schedule_interval(self.animation, 1.0/60.0)


    def reset_game(self):
        self.current_loop = 0
        self.current_offset = 0
        self.movement = 0
        
        self.score = "Score: 0"
        self.tile_coordinates = []
        self.generate_starting_tile()
        self.generate_tiles_coordinates()
        

    def is_desktop(self):
        if platform in ('linux', 'win32','macosx', 'win','win64'):
            return True

        return False


    def init_audio(self):
        self.sound_impace = SoundLoader.load("audio/gameover_impact.wav")
        self.sound_music = SoundLoader.load("audio/music.mp3")

        self.sound_impace.volume = .05
        self.sound_music.volume = .10


    def init_ship(self):
        with self.canvas:
            Color(1,1,1)
            self.ship = Quad(source = 'images/ship.png')


    def update_ship(self):
        self.ship_coordinate[0] = (self.width/2 - self.width*.025, self.SHIP_BASE * self.height)
        self.ship_coordinate[1] = (self.width/2 - self.width*.025, self.SHIP_BASE * self.height + self.width*.05)
        self.ship_coordinate[2] = (self.width/2 + self.width*.025, self.SHIP_BASE * self.height + self.width*.05)
        self.ship_coordinate[3] = (self.width/2 + self.width*.025, self.SHIP_BASE * self.height)


        self.ship.points = [*self.ship_coordinate[0], *self.ship_coordinate[1],
                            *self.ship_coordinate[2], *self.ship_coordinate[3]] 


    def collision(self, x, y):
        '''
        return True if not collide
        '''
        clear_points = 0

        xmin, ymin = self.get_tile_coordinates(x,y)
        xmax, ymax = self.get_tile_coordinates(x + 1,y + 1)

        for i in range(4):
            x, y = self.ship_coordinate[i]
            if xmin <= x <= xmax and ymin <= y <= ymax:
                clear_points += 1

            if clear_points >= 2:
                return True

        return False

    def check_collision(self):
        for i in range(len(self.ship_coordinate)):
            x, y = self.tile_coordinates[i]

            if y > self.current_loop + 1:
                return False
            
            if self.collision(x, y):
                return True

        return False



    def get_line_x_from_index(self, index):
        '''
        Obtain line index x from location
        '''
        center_x = self.perspective_point_x
        spacing = self.V_LINES_SPACING * self.width
        offset = index - 0.5
        line_x = center_x + offset * spacing + self.movement
        return line_x


    def get_line_y_from_index(self, index):
        '''
        Obtain line index y from location
        '''
        spacing = self.H_LINES_SPACING * self.height
        line_y = index * spacing - self.current_offset
        return line_y

    
    def get_tile_coordinates(self, x, y):
        y = y - self.current_loop
        x = self.get_line_x_from_index(x)
        y = self.get_line_y_from_index(y)
        return x, y


    def init_vertical_line(self):
        '''
        Initialize vertical lines
        '''
        with self.canvas:
            Color(1,1,1)
            for i in range(self.V_NB_LINES):
                self.vertical_lines.append(Line())
    

    def update_vertical_lines(self):
        '''
        Draw vertical lines
        '''
        starting = -int(self.V_NB_LINES/2) + 1
        ending = starting + self.V_NB_LINES

        for i in range(starting, ending):
            line_x = self.get_line_x_from_index(i)

            x1, y1 = self.transform(line_x, 0)
            x2, y2 = self.transform(line_x, self.height)
            self.vertical_lines[i].points = [x1, y1, x2, y2]


    def init_horizontal_line(self):
        '''
        Initialize horizontal lines
        '''
        with self.canvas:
            Color(1,1,1)
            for i in range(self.H_NB_LINES):
                self.horizontal_lines.append(Line())
    

    def update_horizontal_lines(self):
        '''
        Draw horizontal lines
        '''
        starting = -int(self.V_NB_LINES/2) + 1
        ending = starting + self.V_NB_LINES - 1

        x_min = self.get_line_x_from_index(starting)
        x_max = self.get_line_x_from_index(ending)

        for i in range(self.H_NB_LINES):
            line_y = self.get_line_y_from_index(i)

            x1, y1 = self.transform(x_min, line_y)
            x2, y2 = self.transform(x_max, line_y)
            self.horizontal_lines[i].points = [x1, y1, x2, y2]


    def init_tiles(self):
        '''
        Initialize tiles
        '''
        with self.canvas:
            Color(0,1,1)
            for i in range(self.NB_TILES):
                self.tiles.append(Quad())

    def generate_starting_tile(self):
        for i in range(10):
            self.tile_coordinates.append((0,i))
    
    def generate_tiles_coordinates(self):
        last_x = 0
        last_index = 0
        starting = -int(self.V_NB_LINES/2) + 1
        ending = starting + self.V_NB_LINES - 2
        
        # delete out of screen tile
        for i in range(len(self.tile_coordinates) - 1, -1, -1):
            if self.tile_coordinates[i][1] < self.current_loop:
                del self.tile_coordinates[i]

        # check if need more tile
        if len(self.tile_coordinates) > 0:
            last_index = self.tile_coordinates[-1][1] + 1
            last_x = self.tile_coordinates[-1][0]

        # update more tile
        for i in range(len(self.tile_coordinates), self.NB_TILES):
            r = random.randint(0,2)
            # 0 -> straight
            # 1 -> right
            # 2 -> left
            self.tile_coordinates.append((last_x,last_index))
            if last_x <= starting :
                r = 1
            elif last_x >= ending:
                r = 2

            if r == 1:
                last_x += 1
                self.tile_coordinates.append((last_x,last_index))
                last_index += 1
                self.tile_coordinates.append((last_x,last_index))
            elif r == 2:
                last_x -= 1
                self.tile_coordinates.append((last_x,last_index))
                last_index += 1
                self.tile_coordinates.append((last_x,last_index))

            last_index += 1


    def update_tile(self):
        for i in range(self.NB_TILES):
            coordinates = self.tile_coordinates[i]
            xmin, ymin = self.get_tile_coordinates(coordinates[0], coordinates[1])
            xmax, ymax = self.get_tile_coordinates(coordinates[0] + 1, coordinates[1] + 1)
            tile = self.tiles[i]

            '''
            2   3
            
            1   4
            '''
            x1, y1 = self.transform_3D(xmin, ymin)
            x2, y2 = self.transform_3D(xmin, ymax)
            x3, y3 = self.transform_3D(xmax, ymax)
            x4, y4 = self.transform_3D(xmax, ymin)

            tile.points = [x1, y1, x2, y2, x3, y3, x4, y4]
    
    def animation(self, dt):
        '''
        animate the movement of the ship in all direction
        '''
        time_factor = dt*60
        self.update_vertical_lines()
        self.update_horizontal_lines()
        self.update_tile()
        self.update_ship()

        if not self.game_over:
        # y speed
            speed = self.game_speed * self.height
            self.current_offset += speed * time_factor
        
            # x speed
            speed = self.move_speed * self.width
            self.movement += speed * time_factor

            spacing = self.H_LINES_SPACING * self.height
            if self.current_offset >= spacing:
                self.current_offset = 0
                self.current_loop += 1
                self.score = "Score: " + str(self.current_loop * 10)
                self.generate_tiles_coordinates()

        if not self.check_collision() and not self.game_over:
            self.sound_impace.play()
            self.sound_music.stop()
            self.title = "G  A  M  E     O  V  E  R"
            self.button = "RESTART"
            self.menu_screen.opacity = 1
            self.game_over = True
            
    
    def on_button_press(self):
        self.reset_game()
        self.game_over = False
        self.menu_screen.opacity = 0
        self.sound_music.play()

class NeonApp(App):
    pass

if __name__ == "__main__":
    NeonApp().run()
