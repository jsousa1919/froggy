import kivy
import math
import numpy as np
import random
import time

from kivy.app import App
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, Line
from kivy.properties import NumericProperty, ObjectProperty, ListProperty
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget


FROG_SIZE = 80

class RootWidget(FloatLayout):
    def load_main(self):
        self.clear_widgets()
        self.main = MainScreen()
        self.add_widget(self.main)

    def start_game(self):
        self.clear_widgets()
        self.game = FroggyGame()
        self.add_widget(self.game)
        with self.game.canvas.before:
            Color(.5, .5, 1)
            Rectangle(pos=self.pos, size=self.size)
        Clock.schedule_interval(self.game.update, 1.0 / 60.0)

class MainScreen(FloatLayout):
    def start_game(self):
        self.parent.start_game()

class Graphic(Image):
    id = 'graphic'
    state = 0
    angle = NumericProperty(0)
    @classmethod
    def get(cls, name):
        return 'assets/images/{}'.format(name)

class Frog(Graphic):
    id = 'frog'
    leaf = None
    sources = [
        Graphic.get('froggy1.png'),
        Graphic.get('froggyleft.png'),
        Graphic.get('froggyright.png')
    ]

    def change_state(self, state):
        self.source = self.sources[state]

class Fly(Widget):
    def __init__(self):
        self.graphic = None

    def move(self):
        pass

class Leaf(Widget):
    def __init__(self, parent):
        self.parent = parent
        self.vx = self.vy = 0
        self.graphic = None
        self.reposition(2.0, -400)

    def reposition(self, scale=1.0, dist=0, vx=0, vy=0):
        self.x = int(random.randrange(600))
        self.y = 800 + int(random.randrange(800) * scale) + dist
        self.vx = vx or self.vx
        self.vy = vy or self.vy

    def move(self):
        if self.graphic:
            self.parent.canvas.remove(self.graphic)
        if self.y < 800:
            newx = self.x + self.vx
            if newx > 600 or newx < 0:
                self.vx = -self.vx
                newx = self.x + self.vx
            self.x = newx
        self.y -= self.vy
        with self.parent.canvas:
            Color(0, 1, 0)
            self.graphic = Line(circle=(self.x, self.y, 20))
        return (self.y + 20) > 0

class FroggyGame(FloatLayout):
    frog = ObjectProperty(None)

    frog_pos = np.array((400, 300))
    target = None
    halfway = None
    tongue_target = None
    game_points = [
        'frog_pos',
        'tongue_target'
    ]

    touch_time = None
    hopping = False
    vector = np.array((0, 1))

    tongue = None
    tongue_return = False
    tongue_points = []

    id = 'game'
    speed = 8
    tongue_speed = 20
    game_speed = 0.1
    game_speed_increment = 0.002
    points = NumericProperty(0)
    tick = 0
    tick_mod = 100

    def __init__(self, *args, **kwargs):
        super(FroggyGame, self).__init__(*args, **kwargs)
        self.frog.allow_stretch = True
        self.frog.size = (FROG_SIZE, FROG_SIZE)
        self.frog.angle = 90
        self.restart_idle()

        self.leaves = []
        for i in range(10):
            leaf = Leaf(self)
            self.leaves.append(leaf)

    def frog_head(self):
        rad = self.frog.angle * np.pi / 180
        vector = np.array((math.cos(rad), math.sin(rad)))
        return self.frog_pos + np.array((vector * FROG_SIZE * (3.0 / 8.0))) 

    def tongue_catch(self, pos, return_=False):
        self.tongue_target = pos
        self.tongue_pos = self.frog_pos.copy()

    def remoteness(self):
        raw = np.abs(np.linalg.norm(self.frog_pos - self.halfway))
        return 1 - (2 * raw / self.distance)

    def frog_move(self):
        current = self.frog_pos.copy()
        self.vector = self.target - current
        mag = max(np.linalg.norm(self.vector), 1)
        if mag <= self.speed:
            self.frog_pos = self.target
            self.frog_stop()
            return True
        else:
            self.frog_pos = (current + ((self.vector / mag) * self.speed))
            if self.tongue_target is not None:
                self.tongue_target += (new - current)
            size = FROG_SIZE + int(self.remoteness() * FROG_SIZE)
            self.frog.size = [size, size]
            return False

    def tongue_move(self):
        begin = self.tongue_pos
        end = self.tongue_target
        vector = end - begin
        mag = max(np.linalg.norm(vector), 1)
        if mag <= self.tongue_speed:
            new = end
            if self.tongue_return:
                self.tongue_target = None
            else:
                self.tongue_target = self.frog_head()
            self.tongue_return = not self.tongue_return
        else:
            new = (begin + ((vector / mag) * self.tongue_speed)) 
        self.tongue_pos = new
        self.tongue_points = (self.frog_head(), self.tongue_pos)

    def frog_stop(self):
        self.frog_pos = self.target
        self.hopping = False
        self.target = None
        self.origin = None
        self.frog_size = (FROG_SIZE, FROG_SIZE)
        self.restart_idle()

    def move_screen(self):
        change = np.array((0, self.game_speed))
        #for attr in self.game_points:
        #    points = getattr(self, attr)
        #    if points is not None and len(points):
        #        setattr(self, attr, points - change)
        if self.tongue_target is not None and len(self.tongue_target):
            self.tongue_target -= change
        if self.frog_pos is not None and len(self.frog_pos):
            self.frog_pos -= change
            if self.frog.leaf:
                self.frog_pos[0] += self.frog.leaf.vx
        if self.tongue:
            self.tongue_points = [arr - change for arr in self.tongue_points]

    def set_angle_from_vector(self, vector):
        self.frog.angle = math.atan2(vector[1], (vector[0] + 1e-10)) * 180 / math.pi

    @property
    def is_active(self):
        return self.hopping or self.tongue_target is not None
    
    def on_touch_down(self, touch):
        self.touch_time = time.time()

    def on_touch_move(self, touch):
        if not self.is_active:
            self.set_angle_from_vector(np.array(touch.pos) - self.frog_pos)

    def on_touch_up(self, touch):
        thresh = max(0, 0.4 - (self.game_speed / 20))
        if self.touch_time and not self.is_active:
            self.set_angle_from_vector(np.array(touch.pos) - self.frog_pos)
            if (self.hopping or time.time() - self.touch_time < thresh) and self.tongue_target is None:
                self.tongue_catch(touch.pos)
            if time.time() - self.touch_time >= thresh and not self.hopping:
                self.hopping = True
                self.frog.change_state(0)
                self.origin = self.frog_pos.copy()
                self.target = np.array(touch.pos)
                self.vector = self.target - self.origin
                #import ipdb; ipdb.set_trace() 
                self.set_angle_from_vector(self.vector)
                self.halfway = self.origin + (self.vector / 2)
                self.distance = np.linalg.norm(self.vector)
                self.unit = self.vector / self.distance
                #self.frog.color = [random.random(), random.random(), random.random(), 1]
            self.touch_time = None
            self.restart_idle()

    def restart_idle(self):
        self.frog.change_state(0)
        self.next_idle = time.time() + (4 - (10 * self.game_speed))

    def idle(self):
        self.frog.change_state(random.randrange(0, len(self.frog.sources)))
        self.next_idle += (random.random() * 2 + (0.5 - (self.game_speed / 5.0))) 

    def update(self, dt):
        if self.tick % self.tick_mod == 0:
            self.points += self.game_speed * (1 / self.game_speed_increment)
            self.tick_mod = max(self.tick_mod - 2, 5)
        self.tick += 1

        if self.tongue:
            self.canvas.remove(self.tongue)
            self.tongue = None
        elif time.time() > self.next_idle:
            self.idle()

        landing = False
        if self.target is not None:
            landing = self.frog_move()
        self.move_screen()
        if self.game_speed < 4:
            self.game_speed += self.game_speed_increment

        if self.tongue_target is not None:
            self.tongue_move()
            with self.canvas:
                Color(1, .7, .7)
                points = map(float, np.hstack(self.tongue_points))
                self.tongue = Line(points=points, width=5)

        self.frog.center_x, self.frog.center_y = map(float, self.frog_pos)
        if self.frog.center_y < 0:
            # self.lose()
            pass

        alive = not landing
        for leaf in self.leaves:
            if not alive:
                if self.frog.collide_point(leaf.x, leaf.y):
                    alive = True
                    self.frog.leaf = leaf
            leaf.vy = self.game_speed
            active = leaf.move()
            if not active:
                print "REPOSITION"
                leaf.reposition(vx=self.game_speed / 2.0)

        if not alive:
            # self.drown()
            pass

class FroggyApp(App):
    def build(self):
        self.root = RootWidget()
        return self.root


if __name__ == '__main__':
    FroggyApp().run()

