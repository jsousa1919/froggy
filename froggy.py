import kivy
import numpy as np
import random

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty

class FroggyGame(FloatLayout):
    frog = ObjectProperty(None)
    target = None
    hopping = False
    speed = 10

    def frog_pos(self):
        return np.array((self.frog.center_x, self.frog.center_y))

    def proximity(self, pos):
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
            self.frog.font_size = 64 + int((1 - self.proximity(new)) * 128)
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
        game = FroggyGame()
        Clock.schedule_interval(game.update, 1.0 / 60.0)
        return game

if __name__ == '__main__':
    FroggyApp().run()

