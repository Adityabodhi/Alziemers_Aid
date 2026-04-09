from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from random import choice, shuffle
from kivy.clock import Clock
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivymd.toast import toast

class GameCard(ButtonBehavior, Image):
    def __init__(self, asset_name, target_key, **kwargs):
        super().__init__(**kwargs)
        self.asset_name = asset_name
        self.target_key = target_key
        self.source = f"assets/{asset_name}.png"
        self.allow_stretch = True
        self.keep_ratio = True
        self.size_hint = (None, None)
        self.size = ("150dp", "150dp")

class PictureRecognitionScreen(Screen):
    # Mapping keys to asset names
    # Note: 'picture_rec' keys in translation engine: APPLE, CAR, HOUSE, etc.
    items = ["APPLE", "HOUSE", "STAR", "HEART", "DOG", "CAT", "CAR", "CAMERA"]
    
    mapping = {
        "APPLE": "apple",
        "HOUSE": "home",
        "STAR": "star",
        "HEART": "heart",
        "DOG": "dog",
        "CAT": "cat",
        "CAR": "car",
        "CAMERA": "camera"
    }
    
    def on_enter(self, *args):
        self.new_round()

    def new_round(self):
        self.ids.game_grid.clear_widgets()
        app = MDApp.get_running_app()
        
        target = choice(self.items)
        self.target_name = target
        other = choice([i for i in self.items if i != target])
        
        options = [target, other]
        shuffle(options)
        
        self.ids.prompt_label.text = f"Tap {target}"
        app.speak(f"Tap {target}")
        
        for name in options:
            card = GameCard(self.mapping[name], target_key=name)
            card.bind(on_release=self.check_answer)
            self.ids.game_grid.add_widget(card)

    def check_answer(self, card):
        name = card.target_key
        app = MDApp.get_running_app()
        if name == self.target_name:
            toast("Correct ✓")
            app.speak("Correct")
            Clock.schedule_once(lambda dt: self.new_round(), 1.0)
        else:
            toast("Try Again")
