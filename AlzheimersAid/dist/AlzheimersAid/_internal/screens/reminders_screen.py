from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from kivymd.uix.list import ThreeLineAvatarIconListItem, IconRightWidget
from datetime import datetime

class RemindersScreen(Screen):
    def on_enter(self, *args):
        self.populate_reminders()

    def populate_reminders(self):
        self.ids.reminder_list.clear_widgets()
        app = MDApp.get_running_app()
        reminders = app.db.get_reminders()
        
        for rid, title, time_str, recurring in reminders:
            recurring_label = "(Daily)" if recurring else "(Once)"
            item = ThreeLineAvatarIconListItem(
                text=title,
                secondary_text=f"Time: {time_str}",
                tertiary_text=recurring_label
            )
            delete_btn = IconRightWidget(
                icon="delete",
                on_release=lambda x, r_id=rid: self.confirm_delete(r_id)
            )
            item.add_widget(delete_btn)
            self.ids.reminder_list.add_widget(item)

    def confirm_delete(self, rid):
        app = MDApp.get_running_app()
        app.show_confirmation_dialog(
            "Delete Reminder",
            "Are you sure you want to delete this reminder?",
            lambda: self.delete_reminder(rid)
        )

    def delete_reminder(self, rid):
        app = MDApp.get_running_app()
        app.db.delete_reminder(rid)
        self.populate_reminders()
        app.speak("Reminder deleted.")

    def add_reminder(self):
        app = MDApp.get_running_app()
        title = self.ids.reminder_title_input.text.strip()
        time_str = self.ids.reminder_time_input.text.strip()
        recurring = self.ids.reminder_recurring_switch.active

        if not title:
            app.show_info_dialog("Please enter a reminder title.")
            return
        if len(title) > 100:
            app.show_info_dialog("Title is too long (max 100 characters).")
            return
        if not time_str:
            app.show_info_dialog("Please enter a time.")
            return
        try:
            datetime.strptime(time_str, "%H:%M")
        except ValueError:
            app.show_info_dialog("Time must be in HH:MM format (e.g., 14:30).")
            return

        app.db.add_reminder(title, time_str, recurring)
        self.populate_reminders()
        app.speak(f"Added reminder for {title}")
        self.ids.reminder_title_input.text = ""
        self.ids.reminder_time_input.text = ""
