from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.list import ThreeLineAvatarIconListItem, IconRightWidget, ImageLeftWidget
from kivy.utils import platform
from kivymd.toast import toast
import os
import shutil

class FacesScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,
            select_path=self.select_path,
            preview=True,
        )
        self.file_mode = "" # 'photo' or 'audio'
        self.selected_photo = ""
        self.selected_audio = ""

    def on_enter(self, *args):
        self.populate_faces()

    def populate_faces(self):
        self.ids.face_list.clear_widgets()
        app = MDApp.get_running_app()
        faces = app.db.get_faces()
        for fid, name, relation, photo_path, audio_path in faces:
            item = ThreeLineAvatarIconListItem(
                text=name,
                secondary_text=relation,
                on_release=lambda x, n=name, a=audio_path: self.play_face(n, a)
            )
            if photo_path and os.path.exists(photo_path):
                img = ImageLeftWidget(source=photo_path)
                item.add_widget(img)
            
            delete_btn = IconRightWidget(
                icon="delete",
                on_release=lambda x, f_id=fid: self.confirm_delete(f_id)
            )
            item.add_widget(delete_btn)
            self.ids.face_list.add_widget(item)

    def play_face(self, name, audio_path):
        app = MDApp.get_running_app()
        app.speak(f"This is {name}")
        if audio_path and os.path.exists(audio_path):
            # Play actual audio if we had a sound player, but for now speak is fine
            # app.speak will handle it
            pass

    def confirm_delete(self, fid):
        app = MDApp.get_running_app()
        app.show_confirmation_dialog(
            "Delete Face",
            "Are you sure you want to delete this person?",
            lambda: self.delete_face(fid)
        )

    def delete_face(self, fid):
        app = MDApp.get_running_app()
        app.db.delete_face(fid)
        self.populate_faces()

    def add_face(self):
        app = MDApp.get_running_app()
        name = self.ids.face_name_input.text.strip()
        relation = self.ids.face_relation_input.text.strip()
        
        if not name or not relation:
            app.show_info_dialog("Name and relation are required.")
            return
            
        # Move files to internal folders
        final_photo = ""
        if self.selected_photo:
            os.makedirs("faces", exist_ok=True)
            final_photo = os.path.join("faces", f"{name}_{os.path.basename(self.selected_photo)}")
            shutil.copy(self.selected_photo, final_photo)
            
        final_audio = ""
        if self.selected_audio:
            os.makedirs("audio", exist_ok=True)
            final_audio = os.path.join("audio", f"{name}_{os.path.basename(self.selected_audio)}")
            shutil.copy(self.selected_audio, final_audio)

        app.db.add_face(name, relation, final_photo, final_audio)
        self.populate_faces()
        app.speak(f"Added {name} to faces.")
        
        # Reset fields
        self.ids.face_name_input.text = ""
        self.ids.face_relation_input.text = ""
        self.selected_photo = ""
        self.selected_audio = ""

    def open_file_manager(self, mode):
        self.file_mode = mode
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            def callback(permissions, results):
                if all(results):
                    self._launch_file_manager()
                else:
                    toast("Storage permission required to select files")
            request_permissions([Permission.READ_EXTERNAL_STORAGE], callback)
        else:
            self._launch_file_manager()

    def _launch_file_manager(self):
        from pathlib import Path
        self.file_manager.show(str(Path.home()))

    def select_path(self, path):
        if self.file_mode == 'photo':
            self.selected_photo = path
            toast(f"Selected Photo: {os.path.basename(path)}")
        else:
            self.selected_audio = path
            toast(f"Selected Audio: {os.path.basename(path)}")
        self.exit_manager()

    def exit_manager(self, *args):
        self.file_manager.close()
