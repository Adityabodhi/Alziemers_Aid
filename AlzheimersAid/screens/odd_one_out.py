from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from random import choice, shuffle
from kivy.clock import Clock
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivymd.toast import toast

class GameCard(ButtonBehavior, Image):
    def __init__(self, asset_name, **kwargs):
        super().__init__(**kwargs)
        self.asset_name = asset_name
        self.source = f"assets/{asset_name}.png"
        self.allow_stretch = True
        self.keep_ratio = True
        self.size_hint = (None, None)
        self.size = ("120dp", "120dp")

class OddOneOutScreen(Screen):
    patterns = [
        ("apple", "apple", "star"),
        ("star", "star", "heart"),
        ("car", "car", "home"),
        ("dog", "dog", "cat"),
    ]
    
    def on_enter(self, *args):
        self.new_round()

    def new_round(self):
        self.ids.game_grid.clear_widgets()
        pattern = choice(self.patterns)
        items = list(pattern)
        shuffle(items)
        
        counts = {}
        for i in items:
            counts[i] = counts.get(i, 0) + 1
        self.odd_asset = min(counts, key=counts.get)
        
        for asset in items:
            card = GameCard(asset)
            card.bind(on_release=self.check_answer)
            self.ids.game_grid.add_widget(card)

    def check_answer(self, card):
        asset = card.asset_name
        app = MDApp.get_running_app()
        if asset == self.odd_asset:
            toast("Correct ✓")
            app.speak("Correct")
            Clock.schedule_once(lambda dt: self.new_round(), 1.0)
        else:
            toast("Try Again")
