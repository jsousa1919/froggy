import kivy
import numpy
import random

from kivy.app import App
from kivy.graphics import Color, Rectangle
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

class MainScreen(FloatLayout):
    pass

class FroggyApp(App):
    def build(self):
        self.root = RootWidget()
        return self.root


if __name__ == '__main__':
    FroggyApp().run()
