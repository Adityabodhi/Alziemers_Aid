from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from kivy.clock import Clock
from random import shuffle
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image

class MemoryCard(ButtonBehavior, Image):
    def __init__(self, asset_name, **kwargs):
        super().__init__(**kwargs)
        self.asset_name = asset_name
        self.real_source = f"assets/{asset_name}.png"
        self.source = "assets/question.png"
        self.is_matched = False
        self.allow_stretch = True
        self.keep_ratio = True
        self.size_hint = (None, None)
        self.size = ("80dp", "80dp")

class MemoryMatchScreen(Screen):
    # assets match what we generated
    assets = ["apple", "star", "heart", "car", "camera", "home"] * 2
    
    def on_enter(self, *args):
        self.reset_game()

    def reset_game(self):
        self.ids.game_grid.clear_widgets()
        shuffle(self.assets)
        self.flipped_cards = []
        self.matched_pairs = 0
        
        for asset in self.assets:
            card = MemoryCard(asset)
            card.bind(on_release=self.flip_card)
            self.ids.game_grid.add_widget(card)

    def flip_card(self, card):
        if card in self.flipped_cards or card.is_matched or len(self.flipped_cards) >= 2:
            return
            
        card.source = card.real_source
        self.flipped_cards.append(card)
        
        if len(self.flipped_cards) == 2:
            Clock.schedule_once(self.check_match, 1.0)

    def check_match(self, dt):
        card1, card2 = self.flipped_cards
        app = MDApp.get_running_app()
        
        if card1.asset_name == card2.asset_name:
            card1.is_matched = True
            card2.is_matched = True
            self.matched_pairs += 1
            app.speak(app.tr("match_found"))
            if self.matched_pairs == len(self.assets) // 2:
                app.speak(app.tr("victory"))
                app.show_info_dialog(app.tr("victory"))
        else:
            card1.source = "assets/question.png"
            card2.source = "assets/question.png"
            
        self.flipped_cards = []
