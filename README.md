EchoLight is an AI-powered real-time assistive system that helps visually impaired individuals identify surrounding objects, read printed text, and interact with technology entirely through voice commands and audio feedback, without touching a screen or keyboard.

Features
Real-time Object Detection — YOLOv8 detects surrounding objects through webcam with bounding boxes and labels
Scene Description — BLIP model generates natural language descriptions of the environment
OCR Text Reading — Tesseract OCR extracts text from images and reads it aloud
Voice Assistant — Hands-free control using wake word "hey assistant"
Emergency Alert — Sends instant email alert to guardian via Gmail SMTP
User Authentication — Secure login and registration with hashed passwords
Tech Stack
Object Detection: YOLOv8 (Ultralytics)
Scene Captioning: BLIP (Salesforce)
OCR: Tesseract OCR + pytesseract
Image Processing: OpenCV
Voice Input: SpeechRecognition + Google API
Voice Output: PowerShell TTS
Web Framework: Flask
Database: SQLite
Deep Learning: PyTorch
Email Alerts: smtplib + MIMEText (Gmail SMTP)
How to Run

Install dependencies:

pip install flask opencv-python pytesseract ultralytics transformers torch pillow SpeechRecognition pyttsx3 werkzeug requests

Also install Tesseract OCR from: https://github.com/UB-Mannheim/tesseract/wiki

Run the app:

Terminal 1: python app.py

Terminal 2: python voice_ai.py

Then say "hey assistant" to begin.

Voice Commands
hey assistant register — Create a new account by voice
hey assistant login — Log in by voice
hey assistant detect — Start real-time object detection
hey assistant read — Open OCR text reader
hey assistant emergency — Send emergency email alert
hey assistant home — Go to home page
hey assistant exit — Close the assistant
