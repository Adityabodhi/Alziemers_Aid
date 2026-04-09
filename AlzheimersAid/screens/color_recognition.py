from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from random import choice, shuffle
from kivy.clock import Clock
from kivymd.toast import toast
from kivymd.uix.button import MDRaisedButton

class ColorButton(MDRaisedButton):
    def __init__(self, color_name, color_val, **kwargs):
        super().__init__(**kwargs)
        self.color_name = color_name
        self.md_bg_color = color_val
        self.size_hint = (0.4, 0.4)
        self.text = "" # Blank color blocks

class ColorRecognitionScreen(Screen):
    colors = [
        ("RED", (1, 0, 0, 1)),
        ("BLUE", (0, 0, 1, 1)),
        ("GREEN", (0, 0.5, 0, 1)),
        ("YELLOW", (1, 1, 0, 1)),
        ("PURPLE", (0.5, 0, 0.5, 1)),
        ("ORANGE", (1, 0.5, 0, 1)),
    ]
    
    def on_enter(self, *args):
        self.new_round()

    def new_round(self):
        self.ids.game_grid.clear_widgets()
        app = MDApp.get_running_app()
        
        target_name, target_val = choice(self.colors)
        self.target_color = target_name
        
        others = [c for c in self.colors if c[0] != target_name]
        shuffle(others)
        options = [(target_name, target_val), others[0]]
        shuffle(options)
        
        self.ids.prompt_label.text = f"Tap {target_name}"
        app.speak(f"Tap {target_name}")
        
        for name, val in options:
            btn = ColorButton(name, val)
            btn.on_release = lambda x, n=name: self.check_answer(n)
            self.ids.game_grid.add_widget(btn)

    def check_answer(self, name):
        app = MDApp.get_running_app()
        if name == self.target_color:
            toast("Correct ✓")
            app.speak("Correct")
            Clock.schedule_once(lambda dt: self.new_round(), 1.0)
        else:
            toast("Try Again")
