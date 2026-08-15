import speech_recognition as sr
import requests
import webbrowser
import time
import subprocess

recognizer = sr.Recognizer()
WAKE_WORD = "hey assistant"
BASE_URL = "http://127.0.0.1:5000"

# ---------------- SPEAK (Windows PowerShell TTS) ----------------
def speak(text):
    print("AI:", text)
    text = text.replace("'", "").replace('"', "")
    subprocess.call([
        "powershell", "-Command",
        f"Add-Type -AssemblyName System.Speech; "
        f"$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
        f"$s.Rate = 1; "
        f"$s.Volume = 100; "
        f"$s.Speak('{text}');"
    ])

# ---------------- LISTEN ----------------
def listen():
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=6)
            text = recognizer.recognize_google(audio)
            print("You:", text)
            return text.lower()
        except:
            return ""

# ---------------- FIX EMAIL ----------------
def clean_email(text):
    text = text.replace(" at ", "@")
    text = text.replace(" dot ", ".")
    text = text.replace(" ", "")
    return text

# ---------------- SAFE INPUT ----------------
def get_input(prompt, label, is_email=False):
    for _ in range(3):
        speak(prompt)
        value = listen()

        if not value:
            speak(f"I didn't catch your {label}")
            continue

        if is_email:
            value = clean_email(value)

        speak(f"You said {value}. Is that correct?")
        if "yes" in listen():
            return value

    return None

# ---------------- LOGIN ----------------
def voice_login():
    webbrowser.open(f"{BASE_URL}/login")
    time.sleep(2)

    speak("Let's log you in")

    email = get_input("Tell your email", "email", True)
    if not email: return True

    password = get_input("Tell your password", "password")
    if not password: return True

    speak("Logging in")

    res = requests.post(f"{BASE_URL}/api/login",
                        data={"email": email, "password": password})

    if res.text == "success":
        speak("Login successful")
        webbrowser.open(BASE_URL)
    else:
        speak("Invalid credentials")

    return True

# ---------------- REGISTER ----------------
def voice_register():
    webbrowser.open(f"{BASE_URL}/register")
    time.sleep(2)

    speak("Let's create your account")

    name = get_input("Tell your name", "name")
    if not name: return True

    email = get_input("Tell your email", "email", True)
    if not email: return True

    password = get_input("Tell your password", "password")
    if not password: return True

    speak("Registering now")

    res = requests.post(f"{BASE_URL}/api/register",
                        data={"name": name, "email": email, "password": password})

    if res.text == "success":
        speak("Registration successful")
        webbrowser.open(f"{BASE_URL}/login")
    else:
        speak("Email already exists")

    return True

# ---------------- NAVIGATION ----------------
def go_home():
    speak("Opening home")
    webbrowser.open(BASE_URL)

def open_ocr():
    speak("Opening OCR")
    webbrowser.open(f"{BASE_URL}/ocr")

def start_detection():
    speak("Starting detection")
    webbrowser.open(f"{BASE_URL}/detection")
    requests.get(f"{BASE_URL}/start_detection")

# ---------------- MAIN INTENT ----------------
def handle(cmd):

    # ---------- REGISTER ----------
    if "register" in cmd:
        return voice_register()

    # ---------- LOGIN ----------
    elif "login" in cmd:
        return voice_login()

    # ---------- HOME ----------
    elif any(x in cmd for x in ["home", "homepage", "go home", "go to home"]):
        go_home()

    # ---------- OCR ----------
    elif any(x in cmd for x in ["ocr", "read", "scan text", "open ocr"]):
        open_ocr()

    # ---------- DETECTION ----------
    elif any(x in cmd for x in ["detect", "object detection", "start detection"]):
        start_detection()

    # ---------- 🚨 EMERGENCY ----------
    elif any(x in cmd for x in ["emergency", "help me", "i need help", "save me"]):
        speak("Emergency detected. Tell your name")

        name = listen()
        if not name:
            speak("Couldn't get your name")
            return True

        speak("Tell your emergency message")
        message = listen()

        if not message:
            message = "User requested help"

        speak("Sending alert now")

        res = requests.post(f"{BASE_URL}/api/emergency",
                            data={"name": name, "message": message})

        if res.text == "sent":
            speak("Emergency alert sent successfully")
        else:
            speak("Failed to send alert")

    # ---------- START CAMERA ----------
    elif any(x in cmd for x in ["start camera", "open camera"]):
        speak("Starting camera from voice")
        requests.get(f"{BASE_URL}/voice_start")

    # ---------- ABOUT ----------
    elif "about" in cmd:
        speak("Opening about page")
        webbrowser.open(f"{BASE_URL}/about")

    # ---------- BACK ----------
    elif any(x in cmd for x in ["close ocr", "back", "go back"]):
        speak("Going back to home")
        go_home()

    # ---------- EXIT (ONLY ONCE ✅) ----------
    elif "exit" in cmd or "close app" in cmd:
        speak("Goodbye")
        return False

    # ---------- DEFAULT ----------
    else:
        speak("Say login, register, home, read text, detect objects, emergency, or about")

    return True

# ---------------- LOOP ----------------
def run():
    speak("Voice assistant ready")
    webbrowser.open(BASE_URL)

    while True:
        cmd = listen()

        if WAKE_WORD not in cmd:
            continue

        speak("Yes, how can I help")

        cmd = cmd.replace(WAKE_WORD, "").strip()
        if not cmd:
            cmd = listen()

        if not handle(cmd):
            break

        speak("What next")

# ---------------- START ----------------
if __name__ == "__main__":
    run()