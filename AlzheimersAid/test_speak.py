import pyttsx3
try:
    engine = pyttsx3.init()
    print("Init successful")
    engine.say("Testing")
    engine.runAndWait()
    print("Speak successful")
except Exception as e:
    print(f"Error: {e}")
