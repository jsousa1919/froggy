import kivy
import math
import numpy as np
import random

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

class FroggyGame(FloatLayout):
    frog = ObjectProperty(None)
    target = None
    hopping = False
    id = 'game'
    speed = 5

    def frog_pos(self):
        return np.array((self.frog.center_x, self.frog.center_y))

    def remoteness(self):
        raw = np.abs(np.linalg.norm(self.frog_pos() - self.halfway))
        return 1 - (2 * raw / self.distance)

    def frog_move(self):
        current = self.frog_pos()
        vector = self.target - current
        mag = max(np.linalg.norm(vector), 1)
        if mag <= self.speed:
            new = self.target
            self.frog_stop()
        else:
            new = (current + ((vector / mag) * self.speed))
            size = 64 + int(self.remoteness() * 128)
        self.frog.center_x, self.frog.center_y = map(float, new)

    def frog_stop(self):
        self.hopping = False
        self.frog.font_size = 64
        self.target = None
        self.origin = None
    
    def on_touch_down(self, touch):
        if not self.hopping:
            self.hopping = True
            self.origin = self.frog_pos()
            self.target = np.array(touch.pos)
            self.vector = self.target - self.origin
            #import ipdb; ipdb.set_trace() 
            self.frog.angle = math.atan2(self.vector[1], (self.vector[0] + 1e-10)) * 180 / math.pi
            self.halfway = self.origin + (self.vector / 2)
            self.distance = np.linalg.norm(self.vector)
            self.unit = self.vector / self.distance
            #self.frog.color = [random.random(), random.random(), random.random(), 1]

    def update(self, dt):
        if self.target is not None:
            self.frog_move()

class FroggyApp(App):
    def build(self):
        self.root = RootWidget()
        return self.root


if __name__ == '__main__':
    FroggyApp().run()

