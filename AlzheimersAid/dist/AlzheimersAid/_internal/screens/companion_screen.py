from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from kivy.properties import ListProperty, StringProperty
from datetime import datetime
import sqlite3

class CompanionScreen(Screen):
    chat_history = ListProperty([])
    chat_text = StringProperty("")

    def on_enter(self, *args):
        if not self.chat_history:
            self.add_message("Companion", "Hello! I am your companion. How can I help you today?")

    def add_message(self, sender, text):
        time_now = datetime.now().strftime("%H:%M")
        self.chat_history.append({"sender": sender, "text": text, "time": time_now})
        self.chat_text += f"[{time_now}] {sender}: {text}\n"
        # Speak the response if from AI
        if sender == "Companion":
            MDApp.get_running_app().speak(text)

    def process_input(self):
        text = self.ids.user_input.text.strip().lower()
        if not text: return
        
        self.add_message("You", self.ids.user_input.text)
        self.ids.user_input.text = ""
        
        # Simple AI Intelligence Logic
        response = self.get_response(text)
        self.add_message("Companion", response)

    def get_response(self, text):
        app = MDApp.get_running_app()
        db_path = "data/alz_aid.db"
        
        # Language detection (simple)
        is_hi = any(k in text for k in ["याद", "बताओ", "कहाँ"])
        is_mr = any(k in text for k in ["आठवण", "सोबती", "कुठे", "कोण"])

        if "who are you" in text or "your name" in text or "सोबती" in text:
            if is_mr: return "मी तुमचा AI सोबती आहे, तुम्हाला मदत करण्यासाठी येथे आहे."
            if is_hi: return "मैं आपका AI साथी हूँ, आपकी मदद के लिए यहाँ हूँ।"
            return "I am your AI Companion, here to help you remember things and keep you safe."
        
        if "who am i" in text or "my name" in text:
            if is_mr: return "तुम्ही एक छान व्यक्ती आहात. मी तुम्हाला मदत करण्यासाठी येथे आहे."
            return "You are a wonderful person, and I am here to assist you."

        if "open" in text or "go to" in text or "जा" in text or "खोलो" in text:
            if "game" in text or "खेळ" in text or "खेल" in text:
                app.root.current = 'games_menu'
                return "Opening Brain Games for you."
            if "reminder" in text or "आठवण" in text or "याद" in text:
                app.root.current = 'reminders'
                return "Going to your Reminders."
            if "face" in text or "people" in text or "चेहरे" in text:
                app.root.current = 'faces'
                return "Opening Faces record."
            if "location" in text or "where" in text or "स्थान" in text or "जागा" in text:
                app.root.current = 'gps'
                return "Checking your location."
            if "record" in text or "medical" in text or "नोंद" in text:
                app.root.current = 'records'
                return "Opening Medical Records."
            if "emergency" in text or "help" in text or "आणीबाणी" in text or "मदद" in text:
                app.root.current = 'emergency'
                return "Switching to Emergency screen."

        if "remind me" in text or "set reminder" in text or "reminders" in text:
            # More flexible parsing for "remind me [at] HH:MM [to] [TASK]"
            import re
            print(f"[AI] Parsing reminder from: {text}")
            
            # Pattern 1: time then task (e.g., 14:00 take pills)
            match1 = re.search(r'(\d{1,2}:\d{2})\s+(?:to\s+)?(.*)', text)
            # Pattern 2: task then time (e.g., take pills at 14:00)
            match2 = re.search(r'(?:to\s+)?(.*?)\s+at\s+(\d{1,2}:\d{2})', text)
            
            rem_time, rem_title = None, None
            if match1:
                rem_time, rem_title = match1.group(1), match1.group(2)
            elif match2:
                rem_title, rem_time = match2.group(1), match2.group(2)
                # Cleanup "remind me" from title if it leaked in
                rem_title = rem_title.replace("remind me", "").strip()

            if rem_time and rem_title:
                try:
                    conn = sqlite3.connect(db_path)
                    conn.execute("INSERT INTO reminders (title, time, recurring) VALUES (?, ?, 1)", (rem_title.strip(), rem_time))
                    conn.commit()
                    conn.close()
                    print(f"[AI] Success: {rem_title} at {rem_time}")
                    return f"Okay, I've set a reminder for {rem_title} at {rem_time}."
                except Exception as e: return f"Error saving to database: {e}"
            
            # If no time found, maybe they just want a list?
            if "what" in text or "my" in text:
                pass # fall through to list logic below
            else:
                return "Please tell me the time and task, for example: 'remind me at 10:00 to walk' or 'remind me to walk at 10:00'."

        if "log" in text or "record" in text:
            try:
                activity = text.replace("log", "").replace("record", "").replace("activity", "").strip()
                if activity:
                    app.db.add_activity(f"AI Log: {activity}")
                    return f"I've recorded that activity: {activity}"
                return "What activity would you like me to log?"
            except: return "I couldn't record that activity."

        if "reminder" in text or "what should i do" in text:
            try:
                conn = sqlite3.connect(db_path)
                reminders = conn.execute("SELECT title, time FROM reminders").fetchall()
                conn.close()
                if reminders:
                    resp = "You have the following reminders: " + ", ".join([f"{r[0]} at {r[1]}" for r in reminders])
                    return resp
                return "You have no reminders for today."
            except: return "I'm having trouble accessing your reminders."

        if "who is" in text:
            name = text.replace("who is", "").strip()
            try:
                conn = sqlite3.connect(db_path)
                person = conn.execute("SELECT name, relation FROM faces WHERE name LIKE ?", (f"%{name}%",)).fetchone()
                conn.close()
                if person:
                    return f"{person[0]} is your {person[1]}."
                return f"I don't have {name} in your face record yet."
            except: return "I'm having trouble looking that up."

        if "where am i" in text or "location" in text:
            return "You are safely at home. I can check your precise GPS if you go to the Location screen."

        if "emergency" in text or "help" in text or "call" in text:
            return "I can help you call your emergency contact. Please tap the Emergency button or say 'Call Help' again."

        return "I'm not sure about that, but I can help you with your reminders, identifying faces, or finding your location."
