#!/usr/bin/env python3
import serial
import time
import json
import os
import requests
import base64
import subprocess
import RPi.GPIO as GPIO
import re

# ----------------------------
# GPIO / Buzzer Setup
# ----------------------------
BUZZER_PIN = 18
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(BUZZER_PIN, GPIO.OUT)

def beep_buzzer(duration=2):
    GPIO.output(BUZZER_PIN, GPIO.HIGH)
    time.sleep(duration)
    GPIO.output(BUZZER_PIN, GPIO.LOW)

# ----------------------------
# Alarm sound
# ----------------------------
ALARM_SOUND = "/home/admin/rfid_tag_tools/alarm.wav"

def play_alarm():
    try:
        subprocess.Popen(["aplay", ALARM_SOUND])
    except Exception as e:
        print("❌ Failed to play alarm sound:", e)

# ----------------------------
# Config
# ----------------------------
TAG_MAPPING_FILE = "/home/admin/rfid_tag_tools/tag_mapping.json"
KOHA_API_BASE = "http://192.168.0.149:8080/api/v1"
USERNAME = "Administrator"
PASSWORD = "Zxcqwe123$"
SERIAL_PORT = "/dev/ttyUSB2_RS232Device"
BAUDRATE = 57600
SCAN_COOLDOWN = 5
TIMEOUT = 10

# ----------------------------
# Load tag mappings
# ----------------------------
def load_mappings():
    if os.path.exists(TAG_MAPPING_FILE):
        with open(TAG_MAPPING_FILE, "r") as f:
            return json.load(f)
    return {}

# ----------------------------
# Koha auth headers
# ----------------------------
def get_auth_headers():
    token = base64.b64encode(f"{USERNAME}:{PASSWORD}".encode()).decode()
    return {
        "Authorization": f"Basic {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

# ----------------------------
# Fetch book info
# ----------------------------
def get_book_info(item_id):
    try:
        res = requests.get(
            f"{KOHA_API_BASE}/items/{item_id}",
            headers=get_auth_headers(),
            timeout=TIMEOUT
        )
        res.raise_for_status()
        item = res.json()
    except Exception as e:
        print("❌ Failed to fetch item:", e)
        return {"title": "Unknown Title", "status": "Error"}

    title = "Unknown Title"
    biblio_id = item.get("biblio_id")
    if biblio_id:
        try:
            biblio_res = requests.get(
                f"{KOHA_API_BASE}/biblios/{biblio_id}",
                headers=get_auth_headers(),
                timeout=TIMEOUT
            )
            if biblio_res.status_code == 200:
                title = biblio_res.json().get("title", title)
        except:
            pass

    try:
        co_res = requests.get(
            f"{KOHA_API_BASE}/checkouts",
            headers=get_auth_headers(),
            timeout=TIMEOUT
        )
        co_res.raise_for_status()
        checkouts = co_res.json()
        if any(co.get("item_id") == item_id for co in checkouts):
            status = "Checked out"
        else:
            if item.get("itemlost"):
                status = "Lost"
            elif item.get("withdrawn"):
                status = "Withdrawn"
            elif item.get("notforloan"):
                status = "Not for loan"
            else:
                status = "Available"
    except Exception as e:
        print("❌ Checkout API error:", e)
        status = "Unknown"

    return {"title": title, "status": status}

# ----------------------------
# Process scanned tag
# ----------------------------
last_scanned = {}

def process_tag(tag_id, mappings):
    now = time.time()
    if tag_id in last_scanned and now - last_scanned[tag_id] < SCAN_COOLDOWN:
        return
    last_scanned[tag_id] = now

    item_id = mappings.get(tag_id)
    if not item_id:
        print(f"❌ Tag '{tag_id}' is not assigned.")
        play_alarm()
        beep_buzzer(3)
        return

    book_info = get_book_info(item_id)
    title = book_info["title"]
    status = book_info["status"]

    if status == "Available":
        print(f"🚨 ALERT! '{title}' is NOT checked out!")
        play_alarm()
        beep_buzzer(3)
    elif status == "Checked out":
        print(f"✅ '{title}' is checked out — pass")
    else:
        print(f"⚠️ '{title}' status = {status}")
        play_alarm()
        beep_buzzer(2)

# ----------------------------
# Read Wiegand tags from ACM8
# ----------------------------
def read_tag():
    try:
        ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)
        print(f"🔌 Connected to ACM8 at {BAUDRATE} baud (Wiegand mode)")

        while True:
            line = ser.readline().decode(errors="ignore").strip()
            if line:
                # Extract numeric ID from line
                match = re.search(r"\[(\d+)\]", line)
                if match:
                    tag_id = match.group(1)
                    yield tag_id

            time.sleep(0.1)

    except Exception as e:
        print("❌ Serial error:", e)

# ----------------------------
# Main
# ----------------------------
if __name__ == "__main__":
    mappings = load_mappings()
    print("🔐 RFID Security Gate ACTIVE (Wiegand)")

    try:
        for tag in read_tag():
            process_tag(tag, mappings)

    except KeyboardInterrupt:
        print("\n👋 Stopping gate...")
        GPIO.cleanup()

    finally:
        GPIO.cleanup()
