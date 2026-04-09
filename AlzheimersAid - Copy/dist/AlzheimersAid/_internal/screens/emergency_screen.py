from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from kivymd.uix.list import TwoLineAvatarIconListItem, IconLeftWidget, IconRightWidget
from kivy.utils import platform
import webbrowser
from kivymd.toast import toast

class EmergencyScreen(Screen):
    def on_enter(self, *args):
        self.populate_contacts()

    def populate_contacts(self):
        self.ids.contact_list.clear_widgets()
        app = MDApp.get_running_app()
        contacts = app.db.get_contacts()
        for cid, name, number in contacts:
            item = TwoLineAvatarIconListItem(
                text=name,
                secondary_text=number,
                on_release=lambda x, n=name, num=number: self.dial_contact(n, num)
            )
            phone_icon = IconLeftWidget(icon="phone")
            item.add_widget(phone_icon)
            
            delete_btn = IconRightWidget(
                icon="delete",
                on_release=lambda x, c_id=cid: self.confirm_delete(c_id)
            )
            item.add_widget(delete_btn)
            self.ids.contact_list.add_widget(item)

    def dial_contact(self, name, number):
        app = MDApp.get_running_app()
        app.speak(f"Calling {name}")
        if platform in ("android", "ios"):
            webbrowser.open(f"tel:{number}")
        else:
            toast(f"Dialing {number}...")

    def confirm_delete(self, cid):
        app = MDApp.get_running_app()
        app.show_confirmation_dialog(
            "Delete Contact",
            "Are you sure you want to delete this contact?",
            lambda: self.delete_contact(cid)
        )

    def delete_contact(self, cid):
        app = MDApp.get_running_app()
        app.db.delete_contact(cid)
        self.populate_contacts()

    def add_contact(self):
        app = MDApp.get_running_app()
        name = self.ids.contact_name_input.text.strip()
        number = self.ids.contact_phone_input.text.strip()
        
        if not name or not number:
            app.show_info_dialog("Both name and phone number are required.")
            return

        app.db.add_contact(name, number)
        self.populate_contacts()
        app.speak(f"Contact {name} added.")
        self.ids.contact_name_input.text = ""
        self.ids.contact_phone_input.text = ""

    def emergency_call(self):
        app = MDApp.get_running_app()
        contacts = app.db.get_contacts()
        if contacts:
            _, name, number = contacts[0]
            app.speak(f"Calling emergency contact {name}")
            if platform in ("android", "ios"):
                webbrowser.open(f"tel:{number}")
            else:
                app.show_info_dialog(f"Emergency: Call {name} at {number}")
        else:
            if platform in ("android", "ios"):
                webbrowser.open("tel:911")
            else:
                app.show_info_dialog("No contacts saved. Please call 911.")
