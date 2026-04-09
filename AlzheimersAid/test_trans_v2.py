from deep_translator import GoogleTranslator
try:
    res = GoogleTranslator(source='auto', target='hi').translate("Hello")
    if res:
        print("Got result for hi")
        print(len(res))
    res2 = GoogleTranslator(source='auto', target='mr').translate("Hello")
    if res2:
        print("Got result for mr")
        print(len(res2))
except Exception as e:
    print(f"Error: {e}")
