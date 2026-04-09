import os
import sys
import threading
import time
import sqlite3
from datetime import datetime
from pathlib import Path

from kivy.lang import Builder
from kivy.clock import Clock, mainthread
from kivy.core.text import LabelBase
from kivy.utils import platform
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.toast import toast
from kivymd.uix.menu import MDDropdownMenu
from kivy.properties import StringProperty

from database import Database, DatabaseConstants
from translator_engine import TranslatorEngine

sys.path.append(os.path.join(os.path.dirname(__file__), 'screens'))

from screens import *
import sys
import os

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

DB_PATH = "data/alz_aid.db"

class AlzheimersAidApp(MDApp):
    lang_code = StringProperty("en")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = None
        self.translator = None
        self._stop_thread = False
        self.menu = None
        self.dialog = None
        self.tts_engine = None

    def build(self):
        self.theme_cls.primary_palette = "Indigo"
        self.theme_cls.theme_style = "Light"
        self.db = Database(DB_PATH)
        self.translator = TranslatorEngine(self.lang_code)

        # Register Devanagari Font
        font_path = os.path.join(os.path.dirname(__file__), "fonts", "noto.ttf")
        if os.path.exists(font_path):
            LabelBase.register(name="Devanagari", fn_regular=font_path)
        else:
            print(f"CRITICAL: Font not found at {font_path}")

        menu_items = [
            {"text": "English", "viewclass": "OneLineListItem", "on_release": lambda x="en": self.set_language(x)},
            {"text": "Hindi", "viewclass": "OneLineListItem", "on_release": lambda x="hi": self.set_language(x)},
            {"text": "Marathi", "viewclass": "OneLineListItem", "on_release": lambda x="mr": self.set_language(x)},
        ]
        self.menu = MDDropdownMenu(items=menu_items, width_mult=4)

        return Builder.load_file(resource_path("alz_app.kv"))

    def on_start(self):
        try:
            import pyttsx3
            self.tts_engine = pyttsx3.init()
        except: self.tts_engine = None

        threading.Thread(target=self.reminder_worker, daemon=True).start()
        Clock.schedule_interval(self.update_time_label, 1)
        Clock.schedule_interval(self.check_internet_status, 30)
        self.check_internet_status(0)

    def check_internet_status(self, dt):
        import requests
        try:
            requests.get("https://www.google.com", timeout=3)
            online = True
        except: online = False
        if hasattr(self.root.ids, 'home_screen'):
            self.root.ids.home_screen.ids.offline_label.opacity = 0 if online else 1

    def on_stop(self):
        self._stop_thread = True
        if self.db: self.db.close()

    def update_time_label(self, dt):
        now = datetime.now()
        if hasattr(self.root.ids, 'home_screen'):
            self.root.ids.home_screen.ids.time_label.text = now.strftime("%H:%M:%S")
            self.root.ids.home_screen.ids.date_label.text = now.strftime("%A, %d %B %Y")

    def open_menu(self, btn):
        self.menu.caller = btn
        self.menu.open()

    def tr(self, key):
        # The app.lang_code ensures Kivy re-evaluates the call whenever lang_code changes
        return self.translator.translate(key)

    def set_language(self, code):
        self.translator = TranslatorEngine(code)
        self.lang_code = code
        self.menu.dismiss()
        toast(f"Language set to {code}")

    def speak(self, text):
        def _task():
            import pythoncom
            try:
                pythoncom.CoInitialize()
                import pyttsx3
                engine = pyttsx3.init()
                engine.say(text)
                engine.runAndWait()
            except Exception as e:
                print(f"TTS Error in thread: {e}")
            finally:
                try: pythoncom.CoUninitialize()
                except: pass
        threading.Thread(target=_task, daemon=True).start()

    def show_info_dialog(self, message):
        if self.dialog: self.dialog.dismiss()
        self.dialog = MDDialog(text=message, buttons=[MDFlatButton(text="OK", on_release=lambda x: self.dialog.dismiss())])
        self.dialog.open()

    def show_confirmation_dialog(self, title, message, on_confirm):
        if self.dialog: self.dialog.dismiss()
        self.dialog = MDDialog(title=title, text=message, buttons=[
            MDFlatButton(text="CANCEL", on_release=lambda x: self.dialog.dismiss()),
            MDRaisedButton(text="CONFIRM", on_release=lambda x: [on_confirm(), self.dialog.dismiss()])
        ])
        self.dialog.open()

    @mainthread
    def fire_reminder(self, title):
        self.speak(f"Reminder: {title}")
        self.show_info_dialog(f"REMINDER: {title}")
        self.db.add_activity(f"Reminder fired: {title}")

    def reminder_worker(self):
        while not self._stop_thread:
            try:
                now = datetime.now()
                cur_time, today = now.strftime("%H:%M"), now.strftime("%Y-%m-%d")
                conn = sqlite3.connect(DB_PATH, check_same_thread=False)
                try:
                    rows = conn.execute("SELECT id, title, recurring, last_fired_date FROM reminders WHERE time = ?", (cur_time,)).fetchall()
                    for rid, title, recurring, last_fired in rows:
                        if not last_fired or (recurring and last_fired != today):
                            conn.execute("UPDATE reminders SET last_fired_date=? WHERE id=?", (today, rid))
                            conn.commit()
                            self.fire_reminder(title)
                finally: conn.close()
                time.sleep(60)
            except: time.sleep(10)

if __name__ == "__main__":
    AlzheimersAidApp().run()
