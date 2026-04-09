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

# ✅ RESOURCE PATH (FOR EXE STABILITY)
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Screens import
sys.path.append(resource_path('screens'))
from screens import *

if getattr(sys, 'frozen', False):
    from kivy.resources import resource_add_path
    # Add the base path
    resource_add_path(sys._MEIPASS)
    # Add the _internal folder for newer PyInstaller
    internal_path = os.path.join(sys._MEIPASS, "_internal")
    if os.path.exists(internal_path):
        resource_add_path(internal_path)
    # Ensure fonts and kv paths are searched
    resource_add_path(os.path.join(internal_path if os.path.exists(internal_path) else sys._MEIPASS, 'fonts'))
    resource_add_path(os.path.join(internal_path if os.path.exists(internal_path) else sys._MEIPASS, 'kv'))

from database import Database
from translator_engine import TranslatorEngine

def get_db_path():
    if platform == 'android':
        from android.storage import app_storage_dir
        return os.path.join(app_storage_dir(), "alz_aid.db")
    return resource_path("data/alz_aid.db")

DB_PATH = get_db_path()

class AlzheimersAidApp(MDApp):
    lang_code = StringProperty("en")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = None
        self.translator = None
        self._stop_thread = False
        self.menu = None
        self.dialog = None

    def build(self):
        self.theme_cls.primary_palette = "Indigo"
        self.theme_cls.theme_style = "Light"
        
        # Ensure data directory exists for DB
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        self.db = Database(DB_PATH)
        self.translator = TranslatorEngine(self.lang_code)

        # Register Devanagari Font
        font_path = resource_path(os.path.join("fonts", "noto.ttf"))
        if os.path.exists(font_path):
            LabelBase.register(name="Devanagari", fn_regular=font_path)

        menu_items = [
            {"text": "English", "viewclass": "OneLineListItem", "on_release": lambda x="en": self.set_language(x)},
            {"text": "Hindi", "viewclass": "OneLineListItem", "on_release": lambda x="hi": self.set_language(x)},
            {"text": "Marathi", "viewclass": "OneLineListItem", "on_release": lambda x="mr": self.set_language(x)},
        ]
        self.menu = MDDropdownMenu(items=menu_items, width_mult=4)

        # Load UI
        return Builder.load_file(resource_path("alz_app.kv"))

    def on_start(self):
        threading.Thread(target=self.reminder_worker, daemon=True).start()
        Clock.schedule_interval(self.update_time_label, 1)

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
        return self.translator.translate(key)

    def set_language(self, code):
        self.translator = TranslatorEngine(code)
        self.lang_code = code
        self.menu.dismiss()
        toast(f"Language set to {code}")

    def speak(self, text):
        if platform == 'android':
            try:
                from plyer import tts
                tts.speak(text)
            except Exception as e:
                print(f"Android TTS Error: {e}")
            return

        def _task():
            import pythoncom
            try:
                pythoncom.CoInitialize()
                import pyttsx3
                engine = pyttsx3.init()
                engine.say(text)
                engine.runAndWait()
            except Exception as e:
                print(f"TTS Error: {e}")
            finally:
                try: pythoncom.CoUninitialize()
                except: pass
        threading.Thread(target=_task, daemon=True).start()

    def show_info_dialog(self, message):
        if self.dialog: self.dialog.dismiss()
        self.dialog = MDDialog(text=message, buttons=[MDFlatButton(text="OK", on_release=lambda x: self.dialog.dismiss())])
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