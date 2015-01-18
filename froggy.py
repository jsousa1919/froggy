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
    sources = [
        Graphic.get('froggy1.png'),
        Graphic.get('froggyleft.png'),
        Graphic.get('froggyright.png')
    ]

    def change_state(self, state):
        self.source = self.sources[state]

class FroggyGame(FloatLayout):
    frog = ObjectProperty(None)
    target = None
    tongue = None
    tongue_target = None
    tongue_return = False
    tongue_points = []
    hopping = False
    id = 'game'
    speed = 8
    tongue_speed = 20

    def __init__(self, *args, **kwargs):
        super(FroggyGame, self).__init__(*args, **kwargs)
        self.frog.allow_stretch = True
        self.frog.size = (FROG_SIZE, FROG_SIZE)
        self.restart_idle()

    def frog_pos(self):
        return np.array((self.frog.center_x, self.frog.center_y))

    def frog_head(self):
        return self.frog_pos() + ((self.vector / np.linalg.norm(self.vector)) * (FROG_SIZE * (3.0 / 8.0))) 

    def tongue_catch(self, pos, return_=False):
        self.tongue_target = pos
        self.tongue_pos = self.frog_pos() 

    def remoteness(self):
        raw = np.abs(np.linalg.norm(self.frog_pos() - self.halfway))
        return 1 - (2 * raw / self.distance)

    def frog_move(self):
        current = self.frog_pos()
        self.vector = self.target - current
        mag = max(np.linalg.norm(self.vector), 1)
        if mag <= self.speed:
            new = self.target
            self.frog_stop()
        else:
            new = (current + ((self.vector / mag) * self.speed))
            if self.tongue_target is not None:
                self.tongue_target += (new - current)
            size = FROG_SIZE + int(self.remoteness() * FROG_SIZE)
            self.frog.size = [size, size]
        self.frog.center_x, self.frog.center_y = map(float, new)

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
        self.tongue_points = map(float, list(np.hstack((self.frog_head(), self.tongue_pos))))
        with self.canvas:
            Color(1, .7, .7)
            self.tongue = Line(points=self.tongue_points, width=5)
        print self.tongue_points

    def frog_stop(self):
        self.hopping = False
        self.target = None
        self.origin = None
        self.restart_idle()

    def move_screen(self):
        if self.tongue_target:
            self.toungue_target -= self.screen_speed
        if self.origin:
            self.origin -= self.screen_speed
        if self.target:
            self.target -= self.screen_speed
        if self.halfway:
            self.halfway -= self.screen_speed
        self.frog.pos -= self.screen_speed
    
    def on_touch_down(self, touch):
        if self.hopping and self.tongue_target is None:
            self.tongue_catch(touch.pos)
        if not self.hopping:
            self.hopping = True
            self.frog.change_state(0)
            self.origin = self.frog_pos()
            self.target = np.array(touch.pos)
            self.vector = self.target - self.origin
            #import ipdb; ipdb.set_trace() 
            self.frog.angle = math.atan2(self.vector[1], (self.vector[0] + 1e-10)) * 180 / math.pi
            self.halfway = self.origin + (self.vector / 2)
            self.distance = np.linalg.norm(self.vector)
            self.unit = self.vector / self.distance
            #self.frog.color = [random.random(), random.random(), random.random(), 1]

    def restart_idle(self):
        self.next_idle = time.time() + 5

    def idle(self):
        self.frog.change_state(random.randrange(0, len(self.frog.sources)))
        self.next_idle += random.random() * 2 + 0.2

    def update(self, dt):
        if self.tongue:
            self.canvas.remove(self.tongue)
        if self.target is not None:
            self.frog_move()
        elif time.time() > self.next_idle:
            self.idle()
        if self.tongue_target is not None:
            self.tongue_move()

class FroggyApp(App):
    def build(self):
        self.root = RootWidget()
        return self.root


if __name__ == '__main__':
    FroggyApp().run()

