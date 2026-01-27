#original code that check the status of the book and print alarm if not checkeout
# import serial
# import time
# import json
# import os
# import requests
# import base64
# import RPi.GPIO as GPIO
# 
# ----------------------------
# GPIO / Buzzer Setup
# ----------------------------
# BUZZER_PIN = 18
# GPIO.setmode(GPIO.BCM)
# GPIO.setup(BUZZER_PIN, GPIO.OUT)
# 
# def beep_buzzer(duration=2):
#     GPIO.output(BUZZER_PIN, GPIO.HIGH)
#     time.sleep(duration)
#     GPIO.output(BUZZER_PIN, GPIO.LOW)
# 
# ----------------------------
# Config
# ----------------------------
# TAG_MAPPING_FILE = "/home/admin/rfid_tag_tools/tag_mapping.json"
# KOHA_API_BASE = "http://192.168.0.149:8080/api/v1"
# USERNAME = "Administrator"
# PASSWORD = "Zxcqwe123$"
# SERIAL_PORT = "/dev/ttyUSB0"
# BAUDRATE = 115200
# SHORT_TAG_LENGTH = 8
# SCAN_COOLDOWN = 5  # seconds between repeated scans
# TIMEOUT = 10
# 
# ----------------------------
# Load mappings
# ----------------------------
# def load_mappings():
#     if os.path.exists(TAG_MAPPING_FILE):
#         with open(TAG_MAPPING_FILE, "r") as f:
#             return json.load(f)
#     return {}
# 
# ----------------------------
# Auth headers
# ----------------------------
# def get_auth_headers():
#     token = base64.b64encode(f"{USERNAME}:{PASSWORD}".encode()).decode()
#     return {
#         "Authorization": f"Basic {token}",
#         "Accept": "application/json",
#         "Content-Type": "application/json",
#     }
# 
# ----------------------------
# Fetch book info by item_id
# ----------------------------
# def get_book_info(item_id):
#     """Return 'title' and 'status' for a given item_id, robustly checking checkout."""
#     # 1️⃣ Fetch item
#     try:
#         res = requests.get(
#             f"{KOHA_API_BASE}/items/{item_id}",
#             headers=get_auth_headers(),
#             timeout=TIMEOUT
#         )
#         res.raise_for_status()
#         item = res.json()
#     except Exception as e:
#         print("❌ Failed to fetch item:", e)
#         return {"title": "Unknown Title", "status": "Error"}
# 
#     # 2️⃣ Fetch title via biblio_id
#     title = "Unknown Title"
#     biblio_id = item.get("biblio_id")
#     if biblio_id:
#         try:
#             biblio_res = requests.get(
#                 f"{KOHA_API_BASE}/biblios/{biblio_id}",
#                 headers=get_auth_headers(),
#                 timeout=TIMEOUT
#             )
#             if biblio_res.status_code == 200:
#                 title = biblio_res.json().get("title", title)
#         except:
#             pass
# 
#     # 3️⃣ Determine status via checkouts
#     try:
#         co_res = requests.get(
#             f"{KOHA_API_BASE}/checkouts",
#             headers=get_auth_headers(),
#             timeout=TIMEOUT
#         )
#         co_res.raise_for_status()
#         checkouts = co_res.json()
# 
#         # Robust detection: check if any checkout matches item_id
#         if any(co.get("item_id") == item_id for co in checkouts):
#             status = "Checked out"
#         else:
#             if item.get("itemlost"):
#                 status = "Lost"
#             elif item.get("withdrawn"):
#                 status = "Withdrawn"
#             elif item.get("notforloan"):
#                 status = "Not for loan"
#             else:
#                 status = "Available"
# 
#     except Exception as e:
#         print("❌ Checkout API error:", e)
#         status = "Unknown"
# 
#     return {"title": title, "status": status}
# 
# ----------------------------
# Process scanned tag
# ----------------------------
# last_scanned = {}
# 
# def process_tag(tag_id, mappings):
#     now = time.time()
# 
#     # Cooldown
#     if tag_id in last_scanned and now - last_scanned[tag_id] < SCAN_COOLDOWN:
#         return
#     last_scanned[tag_id] = now
# 
#     item_id = mappings.get(tag_id)
#     if not item_id:
#         print(f"❌ Tag '{tag_id}' is not assigned to any book.")
#         beep_buzzer(3)
#         return
# 
#     book_info = get_book_info(item_id)
#     title = book_info["title"]
#     status = book_info["status"]
# 
#     # Status handling
#     if status == "Available":
#         print(f"🚨 ALERT! '{title}' is NOT checked out!")
#         beep_buzzer(3)
#     elif status == "Checked out":
#         print(f"✅ '{title}' is checked out — all good")
#     else:
#         print(f"⚠️ '{title}' status = {status}")
#         beep_buzzer(2)
# 
# ----------------------------
# Read tag from ACM815A
# ----------------------------
# def read_tag():
#     try:
#         ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)
#         print("📳 Gate active — waiting for UHF tags...")
#         while True:
#             data = ser.readline().strip()
#             if data:
#                 try:
#                     full_tag = data.decode().strip().upper()
#                 except:
#                     full_tag = data.hex().upper()
#                 # Shorten tag
#                 short_tag = full_tag[:SHORT_TAG_LENGTH]
#                 yield short_tag
#             time.sleep(0.1)
#     except Exception as e:
#         print("❌ Serial read error:", e)
# 
# ----------------------------
# Main loop
# ----------------------------
# if __name__ == "__main__":
#     mappings = load_mappings()
#     print("🔐 UHF Security Gate Active")
# 
#     try:
#         for tag in read_tag():
#             process_tag(tag, mappings)
#     except KeyboardInterrupt:
#         print("\n👋 Stopping gate...")
#     finally:
#         GPIO.cleanup()
#
################THIS IS WHAT IM CURRENTLY RUNNING#######
"""
import serial
import time
import json
import os
import requests
import base64
import subprocess
import RPi.GPIO as GPIO

# ----------------------------
# GPIO / Buzzer Setup (optional)
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
BAUDRATE = 115200
SHORT_TAG_LENGTH = 8
SCAN_COOLDOWN = 5
TIMEOUT = 10

# ----------------------------
# Load mappings
# ----------------------------
def load_mappings():
    if os.path.exists(TAG_MAPPING_FILE):
        with open(TAG_MAPPING_FILE, "r") as f:
            return json.load(f)
    return {}

# ----------------------------
# Auth headers
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

    # Fetch title
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

    # Determine checkout status
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
# Read tag from ACM815A
# ----------------------------
def read_tag():
    try:
        ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)
        print("📳 Gate active — waiting for UHF tags...")
        while True:
            data = ser.readline().strip()
            if data:
                try:
                    full_tag = data.decode().strip().upper()
                except:
                    full_tag = data.hex().upper()

                yield full_tag[:SHORT_TAG_LENGTH]
            time.sleep(0.1)
    except Exception as e:
        print("❌ Serial error:", e)

# ----------------------------
# Main
# ----------------------------
if __name__ == "__main__":
    mappings = load_mappings()
    print("🔐 RFID Security Gate ACTIVE")

    try:
        for tag in read_tag():
            process_tag(tag, mappings)
    except KeyboardInterrupt:
        print("\n👋 Stopping gate...")
        GPIO.cleanup()
    finally:
        GPIO.cleanup()
        
"""
#####################CODE FOR THE ACTUAL SCANNER USB/RS232##############################
import serial
import time
import json
import os
import requests
import base64
import struct
import binascii
from datetime import datetime
import subprocess
import RPi.GPIO as GPIO

#============================
#GPIO / Buzzer
#============================
BUZZER_PIN = 18
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUZZER_PIN, GPIO.OUT)

def beep_buzzer(duration=2):
    GPIO.output(BUZZER_PIN, GPIO.HIGH)
    time.sleep(duration)
    GPIO.output(BUZZER_PIN, GPIO.LOW)

def play_alarm():
    subprocess.Popen(["aplay", "/home/admin/alarm.wav"],
                     stdout=subprocess.DEVNULL,
                     stderr=subprocess.DEVNULL)

#============================
#Config
#============================
TAG_MAPPING_FILE = "/home/admin/rfid_tag_tools/tag_mapping.json"
KOHA_API_BASE = "http://192.168.0.149:8080/api/v1"
USERNAME = "Administrator"
PASSWORD = "Zxcqwe123$"
SERIAL_PORT = "/dev/ttyUSB2_RS232Device"
BAUDRATE = 57600
SHORT_TAG_LENGTH = 8
SCAN_COOLDOWN = 5
TIMEOUT = 10

#============================
#Load tag mappings
#============================
def load_mappings():
    if os.path.exists(TAG_MAPPING_FILE):
        with open(TAG_MAPPING_FILE, "r") as f:
            return json.load(f)
    return {}
"""
============================
Koha auth headers
============================
"""
def get_auth_headers():
    token = base64.b64encode(f"{USERNAME}:{PASSWORD}".encode()).decode()
    return {
        "Authorization": f"Basic {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
"""
============================
Koha book info
============================
"""
def get_book_info(item_id):
    try:
        item_res = requests.get(
            f"{KOHA_API_BASE}/items/{item_id}",
            headers=get_auth_headers(),
            timeout=TIMEOUT
        )
        item_res.raise_for_status()
        item = item_res.json()
    except Exception as e:
        print("❌ Item fetch failed:", e)
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

    except:
        status = "Unknown"

    return {"title": title, "status": status}
"""
============================
RFID Reader (REAL GATE)
============================
"""
class RFIDReader:
    FRAME_HEADER = 0xBB
    FRAME_END = 0x7E
    CMD_INVENTORY = 0x22

    def __init__(self, port, baudrate):
        self.ser = serial.Serial(port, baudrate, timeout=1)

    def checksum(self, data):
        return sum(data) & 0xFFFF

    def send_inventory(self):
        frame = bytes([self.FRAME_HEADER, 0x01, self.CMD_INVENTORY])
        chk = self.checksum(frame[1:])
        frame += struct.pack(">H", chk) + bytes([self.FRAME_END])
        self.ser.write(frame)

    def read_response(self):
        while True:
            b = self.ser.read(1)
            if not b:
                return None
            if b[0] == self.FRAME_HEADER:
                break

        length = self.ser.read(1)[0]
        payload = self.ser.read(length + 3)
        return b + bytes([length]) + payload

    def parse_epcs(self, frame):
        epcs = []
        data_len = frame[1] - 1
        data = frame[3:3 + data_len]
        i = 0

        while i + 2 <= len(data):
            pc = struct.unpack(">H", data[i:i+2])[0]
            i += 2
            epc_len = ((pc >> 11) & 0x1F) * 2
            epc = data[i:i+epc_len]
            i += epc_len + 1
            epcs.append(binascii.hexlify(epc).decode().upper())

        return epcs
"""
============================

Process tag
============================
"""
last_scanned = {}

def process_tag(tag_id, mappings):
    now = time.time()
    if tag_id in last_scanned and now - last_scanned[tag_id] < SCAN_COOLDOWN:
        return
    last_scanned[tag_id] = now

    item_id = mappings.get(tag_id)
    if not item_id:
        print(f"❌ Unassigned tag {tag_id}")
        beep_buzzer(3)
        play_alarm()
        return

    info = get_book_info(item_id)
    title = info["title"]
    status = info["status"]

    if status == "Available":
        print(f"🚨 '{title}' is NOT checked out!")
        beep_buzzer(3)
        play_alarm()
    elif status == "Checked out":
        print(f"✅ '{title}' checked out — PASS")
    else:
        print(f"⚠️ '{title}' status = {status}")
        beep_buzzer(2)
"""
============================
MAIN
============================
"""
if __name__ == "__main__":
    mappings = load_mappings()
    reader = RFIDReader(SERIAL_PORT, BAUDRATE)

    print("🔐 UHF Anti-Theft Gate ACTIVE")

    try:
        while True:
            reader.send_inventory()
            frame = reader.read_response()
            if frame:
                epcs = reader.parse_epcs(frame)
                for epc in epcs:
                    short_tag = epc[:SHORT_TAG_LENGTH]
                    process_tag(short_tag, mappings)
            time.sleep(0.2)

    except KeyboardInterrupt:
        print("\n👋 Gate stopped")
    finally:
        GPIO.cleanup()

