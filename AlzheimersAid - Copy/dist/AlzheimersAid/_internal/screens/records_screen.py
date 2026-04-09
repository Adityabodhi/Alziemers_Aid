from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from kivymd.uix.list import TwoLineAvatarIconListItem, IconRightWidget

class RecordsScreen(Screen):
    def on_enter(self, *args):
        self.populate_records()

    def populate_records(self):
        self.ids.record_list.clear_widgets()
        app = MDApp.get_running_app()
        records = app.db.get_records()
        for rid, title, details in records:
            item = TwoLineAvatarIconListItem(
                text=title,
                secondary_text=details
            )
            delete_btn = IconRightWidget(
                icon="delete",
                on_release=lambda x, r_id=rid: self.confirm_delete(r_id)
            )
            item.add_widget(delete_btn)
            self.ids.record_list.add_widget(item)

    def confirm_delete(self, rid):
        app = MDApp.get_running_app()
        app.show_confirmation_dialog(
            "Delete Record",
            "Are you sure you want to delete this medical record?",
            lambda: self.delete_record(rid)
        )

    def delete_record(self, rid):
        app = MDApp.get_running_app()
        app.db.delete_record(rid)
        self.populate_records()

    def add_record(self):
        app = MDApp.get_running_app()
        title = self.ids.record_title_input.text.strip()
        details = self.ids.record_details_input.text.strip()
        
        if not title or not details:
            app.show_info_dialog("Both title and details are required.")
            return

        app.db.add_record(title, details)
        self.populate_records()
        app.speak(f"Medical record {title} added.")
        self.ids.record_title_input.text = ""
        self.ids.record_details_input.text = ""
