from deep_translator import GoogleTranslator
import requests

TRANSLATIONS = {
    "en": {
        "app_title": "Alzheimer's Aid",
        "home_subtitle": "Your memory companion",
        "reminders": "Reminders",
        "faces": "Faces",
        "location": "Location",
        "games": "Brain Games",
        "emergency": "Emergency",
        "caregiver": "Activity Log",
        "companion": "AI Companion",
        "ask_anything": "Ask your companion anything...",
        "who_is": "Who is",
        "call_help": "Call for help",
        "remind_me": "What are my reminders?",
        "where_am_i": "Where am I?",
        "lang_select": "Select Language",
        "match_prompt": "Find matching pairs!",
        "victory": "Victory! Great job.",
        "match_found": "Match found!",
        "memory_match": "Memory Match",
        "odd_one_out": "Odd One Out",
        "picture_rec": "Picture Recognition",
        "color_rec": "Color Recognition",
        "save": "Save",
        "add_contact": "Add Contact",
        "name": "Name",
        "phone": "Phone Number",
        "saved_contacts": "Saved Contacts",
        "medical_records": "Medical Records",
        "add_reminder": "Add Reminder",
        "title": "Title",
        "time": "Time",
        "recurring": "Recurring",
        "delete": "Delete",
        "add_person": "Add Person",
        "relation": "Relation",
        "photo": "Photo",
        "audio": "Audio",
        "call": "Call",
        "emergency_call": "Emergency Call",
        "find_location": "Find My Location",
        "details": "Details",
        "add_record": "Add Record",
    },
    "hi": {
        "app_title": "अल्जाइमर सहायता",
        "home_subtitle": "आपकी स्मृति के साथी",
        "reminders": "अनुस्मारक",
        "faces": "चेहरे",
        "location": "स्थान",
        "games": "दिमागी खेल",
        "emergency": "आपातकालीन",
        "caregiver": "गतिविधि लॉग",
        "companion": "AI साथ",
        "ask_anything": "अपने साथी से कुछ भी पूछें...",
        "who_is": "कौन है",
        "call_help": "मदद के लिए कॉल करें",
        "remind_me": "मेरे अनुस्मारक क्या हैं?",
        "where_am_i": "मैं कहाँ हूँ?",
        "lang_select": "भाषा चुनें",
        "match_prompt": "मिलते-जुलते जोड़े खोजें!",
        "victory": "जीत! बहुत बढ़िया।",
        "match_found": "जोड़ा मिल गया!",
        "memory_match": "मेमोरी मैच",
        "odd_one_out": "अजीब बाहर",
        "picture_rec": "चित्र पहचान",
        "color_rec": "रंग पहचान",
        "save": "सहेजें",
        "add_contact": "संपर्क जोड़ें",
        "name": "नाम",
        "phone": "फोन नंबर",
        "saved_contacts": "सहेजे गए संपर्क",
        "medical_records": "मेडिकल रिकॉर्ड",
        "add_reminder": "अनुस्मारक जोड़ें",
        "title": "शीर्षक",
        "time": "समय",
        "recurring": "पुनरावर्ती",
        "delete": "हटाएं",
        "add_person": "व्यक्ति जोड़ें",
        "relation": "संबंध",
        "photo": "फोटो",
        "audio": "ऑडियो",
        "call": "कॉल",
        "emergency_call": "आपातकालीन कॉल",
        "find_location": "मेरा स्थान खोजें",
        "details": "विवरण",
        "add_record": "रिकॉर्ड जोड़ें",
    },
    "mr": {
        "app_title": "अल्झायमर मदत",
        "home_subtitle": "तुमचा स्मृती सोबती",
        "reminders": "स्मरणपत्रे",
        "faces": "चेहरे",
        "location": "स्थान",
        "games": "मेंदूचे खेळ",
        "emergency": "आणीबाणी",
        "caregiver": "कृती लॉग",
        "companion": "AI सोबती",
        "ask_anything": "तुमच्या सोबत्याला काहीही विचारा...",
        "who_is": "कोण आहे",
        "call_help": "मदत मागवा",
        "remind_me": "माझी स्मरणपत्रे काय आहेत?",
        "where_am_i": "मी कुठे आहे?",
        "lang_select": "भाषा निवडा",
        "match_prompt": "जुळणाऱ्या जोड्या शोधा!",
        "victory": "विजय! छान काम.",
        "match_found": "जोडी सापडली!",
        "memory_match": "मेमोरी मॅच",
        "odd_one_out": "गटात न बसणारा",
        "picture_rec": "चित्र ओळख",
        "color_rec": "रंग ओळख",
        "save": "जतन करा",
        "add_contact": "संपर्क जोडा",
        "name": "नाव",
        "phone": "फोन नंबर",
        "saved_contacts": "जतन केलेले संपर्क",
        "medical_records": "वैद्यकीय रेकॉर्ड",
        "add_reminder": "स्मरणपत्र जोडा",
        "title": "शीर्षक",
        "time": "वेळ",
        "recurring": "आवर्ती",
        "delete": "हटवा",
        "add_person": "व्यक्ती जोडा",
        "relation": "संबंध",
        "photo": "फोटो",
        "audio": "ऑडिओ",
        "call": "कॉल",
        "emergency_call": "आणीबाणी कॉल",
        "find_location": "माझे स्थान शोधा",
        "details": "तपशील",
        "add_record": "रेकॉर्ड जोडा",
    }
}

class TranslatorEngine:
    def __init__(self, lang_code: str = "en"):
        self.lang_code = lang_code
        self.is_online = self._check_internet()

    def _check_internet(self) -> bool:
        try:
            requests.get("https://www.google.com", timeout=2)
            return True
        except:
            return False

    def translate(self, key: str) -> str:
        # Check static map first (handles offline and core translations)
        if self.lang_code in TRANSLATIONS and key in TRANSLATIONS[self.lang_code]:
            return TRANSLATIONS[self.lang_code][key]
        
        # Fallback to English static map
        text = TRANSLATIONS['en'].get(key, key)
        if self.lang_code == "en":
            return text

        # Attempt online translation for dynamic keys (if any)
        if self.is_online:
            try:
                translated = GoogleTranslator(source='auto', target=self.lang_code).translate(text)
                return translated if translated else text
            except:
                return text
        return text
