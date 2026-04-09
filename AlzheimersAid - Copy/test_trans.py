from deep_translator import GoogleTranslator
try:
    res = GoogleTranslator(source='auto', target='hi').translate("Hello")
    print(f"Translation (hi): {res}")
    res2 = GoogleTranslator(source='auto', target='mr').translate("Hello")
    print(f"Translation (mr): {res2}")
except Exception as e:
    print(f"Error: {e}")
