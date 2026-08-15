from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
import cv2
import pytesseract
import subprocess

# -------------------------------
# Flask Config
# -------------------------------
app = Flask(__name__)
app.secret_key = "secret123"

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

CAPTION_FILE = "latest_caption.txt"
DB_NAME = "object.db"

# -------------------------------
# Database
# -------------------------------
def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            password TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()


import smtplib
from email.mime.text import MIMEText

EMAIL_ID = "pradeepagandhi3@gmail.com"
EMAIL_PASS = "ojso cunt tacn svrj"   

def send_emergency_email(username, message):
    try:
        subject = "🚨 EMERGENCY ALERT"
        body = f"""
        User: {username}
        Message: {message}

        This user needs immediate help!
        """

        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = EMAIL_ID
        msg['To'] = EMAIL_ID

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_ID, EMAIL_PASS)
        server.send_message(msg)
        server.quit()

        return True
    except Exception as e:
        print("Email error:", e)
        return False
    
# -------------------------------
# Helper Functions
# -------------------------------
def extract_text_from_image(image_path):
    img = cv2.imread(image_path)

    if img is None:
        return "Unable to read image"

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    _, gray = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

    text = pytesseract.image_to_string(gray)

    if not text.strip():
        return "No text detected"

    return text

@app.route("/api/emergency", methods=["POST"])
def emergency():
    username = request.form.get("name")
    message = request.form.get("message")

    if send_emergency_email(username, message):
        return "sent"
    return "error"
    
def get_latest_caption():
    if os.path.exists(CAPTION_FILE):
        with open(CAPTION_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    return "No scene description available yet."

# -------------------------------
# ROUTES
# -------------------------------

@app.route("/")
def index():
    return render_template("index.html", latest_caption=get_latest_caption())

# -------------------------------
# API (USED BY VOICE AI)
# -------------------------------

@app.route("/api/login", methods=["POST"])
def api_login():
    email = request.form.get("email")
    password = request.form.get("password")

    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
    conn.close()

    if user and check_password_hash(user["password"], password):
        return "success"
    return "error"


@app.route("/api/register", methods=["POST"])
def api_register():
    name = request.form.get("name")
    email = request.form.get("email")
    password = generate_password_hash(request.form.get("password"))

    try:
        conn = get_db_connection()
        conn.execute("INSERT INTO users (name,email,password) VALUES (?,?,?)",
                     (name, email, password))
        conn.commit()
        conn.close()
        return "success"
    except:
        return "error"

# -------------------------------
# NORMAL WEB ROUTES (OPTIONAL UI)
# -------------------------------

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user"] = user["name"]
            return redirect(url_for("index"))
        else:
            flash("Invalid login")

    return render_template("login.html")


@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])

        try:
            conn = get_db_connection()
            conn.execute("INSERT INTO users (name,email,password) VALUES (?,?,?)",
                         (name,email,password))
            conn.commit()
            conn.close()
            flash("Registration successful! Please login.")
            return redirect(url_for("login"))
        except:
            flash("Email already exists")

    return render_template("register.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/about")
def about():
    return render_template("about.html")

# -------------------------------
# OCR
# -------------------------------
@app.route("/ocr", methods=["GET", "POST"])
def ocr():
    extracted_text = None
    uploaded_image = None

    if request.method == "POST":
        file = request.files.get("image")

        if not file or file.filename == "":
            flash("No file selected")
            return redirect(url_for("ocr"))

        filename = file.filename.replace(" ", "_")
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(path)

        extracted_text = extract_text_from_image(path)
        uploaded_image = filename

    return render_template("ocr.html", extracted_text=extracted_text, uploaded_image=uploaded_image)

# -------------------------------
# OBJECT DETECTION
# -------------------------------
DETECTION_RUNNING = False

@app.route("/detection")
def detection():
    return render_template("detection.html", latest_caption=get_latest_caption())

@app.route("/start_detection")
def start_detection():
    global DETECTION_RUNNING

    if DETECTION_RUNNING:
        return "already running"

    DETECTION_RUNNING = True
    subprocess.Popen(["python", "object_detection.py"])
    return "started"

@app.route("/voice_start")
def voice_start():
    subprocess.Popen(["python", "object_detection.py"])
    return "started"
# -------------------------------
# RUN
# -------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)