import cv2
import pytesseract
import pyttsx3
from tkinter import Tk, filedialog

# Set Tesseract path (for Windows)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Initialize text-to-speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)
engine.setProperty('volume', 1.0)


def select_image():
    root = Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Select Image",
        filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp")]
    )
    return file_path


def process_image(image_path):
    img = cv2.imread(image_path)

    if img is None:
        print("Error: Unable to read image")
        return

    # Preprocessing for better OCR accuracy
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    _, gray = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

    # Extract text
    text = pytesseract.image_to_string(gray)

    if not text.strip():
        text = "No text detected"

    print("\nExtracted Text:\n")
    print(text)

    # Speak text directly
    engine.say(text)
    engine.runAndWait()


if __name__ == "__main__":
    image_path = select_image()

    if image_path:
        process_image(image_path)
    else:
        print("No file selected")
