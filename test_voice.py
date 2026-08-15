import speech_recognition as sr
import pyttsx3

# Text to Speech
engine = pyttsx3.init()

# Speech Recognizer
r = sr.Recognizer()

print("Say: Hey Assistant")

with sr.Microphone() as source:
    r.adjust_for_ambient_noise(source)

    while True:
        try:
            audio = r.listen(source)

            text = r.recognize_google(audio)
            text = text.lower()

            print("You Said:", text)

            if "hey assistant" in text:
                reply = "Yes, I am listening"
                print("Assistant:", reply)

                engine.say(reply)
                engine.runAndWait()

        except Exception as e:
            print("Error:", e)