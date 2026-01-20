import os
import cv2
import smtplib
from datetime import datetime
from email.message import EmailMessage
from dotenv import load_dotenv
import os
import time

load_dotenv()

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
TO_EMAIL = os.getenv("TO_EMAIL")

ALERT_COOLDOWN = int(os.getenv("ALERT_COOLDOWN", 5))
SNAPSHOT_DIR = "snapshots"
os.makedirs(SNAPSHOT_DIR, exist_ok=True)

last_alert_time = 0  

def send_email_alert(frame, timestamp):
    global last_alert_time
    now = time.time()


    if now - last_alert_time < ALERT_COOLDOWN:
        return

    last_alert_time = now

    
    image_path = os.path.join(SNAPSHOT_DIR, f"alert_{timestamp}.jpg")
    cv2.imwrite(image_path, frame)

    msg = EmailMessage()
    msg["Subject"] = "Vehicle Detected"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = TO_EMAIL
    msg.set_content(f"Vehicle detected at {timestamp}")

    with open(image_path, "rb") as f:
        msg.add_attachment(
            f.read(),
            maintype="image",
            subtype="jpeg",
            filename=os.path.basename(image_path)
        )

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.starttls()
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
        print("Alert sent")
    except Exception as e:
        print("Email failed:", e)
        raise
