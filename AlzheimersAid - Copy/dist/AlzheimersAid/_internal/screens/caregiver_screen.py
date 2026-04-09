from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from kivymd.uix.list import TwoLineListItem

class CaregiverScreen(Screen):
    def on_enter(self, *args):
        self.populate_activities()

    def populate_activities(self):
        self.ids.activity_list.clear_widgets()
        app = MDApp.get_running_app()
        activities = app.db.get_activities()
        for ts, msg in activities:
            item = TwoLineListItem(
                text=msg,
                secondary_text=ts
            )
            self.ids.activity_list.add_widget(item)
