import kivy
import numpy as np
import random

from kivy.app import App
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from kivy.properties import ObjectProperty
from kivy.uix.button import Button
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

class FroggyGame(FloatLayout):
    frog = ObjectProperty(None)
    target = None
    hopping = False
    speed = 10

    def frog_pos(self):
        return np.array((self.frog.center_x, self.frog.center_y))

    def inv_proximity(self, pos):
        return np.abs(
            (np.linalg.norm(pos - self.target) - (self.distance / 2)) / (self.distance / 2)
        )

    def frog_move(self):
        current = self.frog_pos()
        vector = self.target - current
        mag = max(np.linalg.norm(vector), 1)
        if mag <= self.speed:
            new = self.target
            self.frog_stop()
        else:
            new = (current + ((vector / mag) * self.speed))
            self.frog.font_size = 64 + int((1 - self.inv_proximity(new)) * 128)
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
            self.distance = np.linalg.norm(self.vector)
            self.frog.color = [random.random(), random.random(), random.random(), 1]

    def update(self, dt):
        if self.target is not None:
            self.frog_move()

class FroggyApp(App):
    def build(self):
        self.root = RootWidget()
        return self.root


if __name__ == '__main__':
    FroggyApp().run()

