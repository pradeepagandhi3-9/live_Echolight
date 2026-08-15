import cv2
import pyttsx3
import threading
from ultralytics import YOLO
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import torch
import os

# ------------------------
# Load Models
# ------------------------
yolo_model = YOLO("yolov8n.pt")

model_name = "Salesforce/blip-image-captioning-base"
processor = BlipProcessor.from_pretrained(model_name)
blip_model = BlipForConditionalGeneration.from_pretrained(model_name)

device = "cuda" if torch.cuda.is_available() else "cpu"
blip_model.to(device)

# ------------------------
# Text-to-Speech
# ------------------------
engine = pyttsx3.init()
engine.setProperty('rate', 150)

def speak(text):
    print("Assistant:", text)
    engine.say(text)
    engine.runAndWait()

def speak_async(text):
    threading.Thread(target=speak, args=(text,), daemon=True).start()

# ------------------------
# Save Caption (Flask)
# ------------------------
CAPTION_FILE = "latest_caption.txt"

def save_caption(text):
    with open(CAPTION_FILE, "w", encoding="utf-8") as f:
        f.write(text)

# ------------------------
# CONFUSION MAP (AUTO FIX)
# ------------------------
CONFUSION_MAP = {
    "laptop": ["phone", "cell phone", "remote", "tablet"],
    "bottle": ["glass", "cup"],
    "tv": ["monitor", "screen"],
    "chair": ["sofa", "seat"],
}

# ------------------------
# CLEAN CAPTION (REMOVE GARBAGE)
# ------------------------
def clean_caption(text):
    text = text.lower().strip()

    # Remove prompt-like junk
    bad_phrases = [
        "this image contains",
        "describe clearly",
        "a scene with",
        "there is",
    ]

    for phrase in bad_phrases:
        text = text.replace(phrase, "")

    # Remove duplicate spaces
    text = " ".join(text.split())

    return text

# ------------------------
# Caption Correction
# ------------------------
def refine_caption(caption, detected_labels):
    label_set = set(detected_labels)

    for correct, wrong_list in CONFUSION_MAP.items():
        if correct in label_set:
            for wrong in wrong_list:
                caption = caption.replace(wrong, correct)

    return caption

# ------------------------
# Generate Caption (FIXED PROMPT)
# ------------------------
def generate_caption(frame):
    image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

    inputs = processor(image, return_tensors="pt").to(device)

    output = blip_model.generate(
        **inputs,
        max_length=35,
        num_beams=5
    )

    caption = processor.decode(output[0], skip_special_tokens=True)
    return caption

# ------------------------
# Build Natural Sentence
# ------------------------
def build_sentence(caption, detected_labels):
    caption = clean_caption(caption)

    if detected_labels:
        objects = list(set(detected_labels))

        if len(objects) == 1:
            obj_text = f"a {objects[0]}"
        else:
            obj_text = ", ".join(objects)

        return f"I can see {obj_text}. {caption}"

    return caption

# ------------------------
# MAIN
# ------------------------
def run():
    cap = cv2.VideoCapture(0)

    cap.set(3, 640)
    cap.set(4, 480)

    print("Press 'c' to capture and describe scene")
    print("Press 'q' to quit")

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        detected_labels = []

        # YOLO detection
        results = yolo_model(frame, verbose=False)[0]

        if len(results.boxes) > 0:
            for box in results.boxes:
                conf = float(box.conf[0])

                if conf < 0.6:
                    continue

                cls_id = int(box.cls[0])
                label = yolo_model.names[cls_id]
                detected_labels.append(label)

                x1, y1, x2, y2 = map(int, box.xyxy[0])

                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f"{label} {conf:.2f}",
                            (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.5, (0, 255, 0), 2)

        cv2.imshow("Object Detection", frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord('c'):
            print("Capturing scene...")

            caption = generate_caption(frame)
            caption = clean_caption(caption)
            caption = refine_caption(caption, detected_labels)

            final_text = build_sentence(caption, detected_labels)

            print("Scene:", final_text)

            save_caption(final_text)
            speak_async(final_text)

        elif key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# ------------------------
if __name__ == "__main__":
    run()