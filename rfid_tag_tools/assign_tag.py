# # /home/admin/rfid_tag_tools/assign_tag.py
# import serial
# import time
# import json
# import os
# import requests
# import base64
# 
# # ----------------------------
# # Config
# # ----------------------------
# TAG_MAPPING_FILE = "/home/admin/rfid_tag_tools/tag_mapping.json"
# KOHA_API_BASE = "http://192.168.0.149:8080/api/v1"
# USERNAME = "Administrator"
# PASSWORD = "Zxcqwe123$"
# SERIAL_PORT = "/dev/ttyUSB0"  # ACM815A default
# BAUDRATE = 115200
# SHORT_TAG_LENGTH = 8  # number of characters for short tag
# TIMEOUT = 10
# 
# # ----------------------------
# # Auth headers (like checkout_logic.py)
# # ----------------------------
# def get_auth_headers():
#     token = base64.b64encode(f"{USERNAME}:{PASSWORD}".encode()).decode()
#     return {
#         "Authorization": f"Basic {token}",
#         "Accept": "application/json",
#         "Content-Type": "application/json",
#     }
# 
# # ----------------------------
# # Load/save tag mappings
# # ----------------------------
# def load_mappings():
#     if os.path.exists(TAG_MAPPING_FILE):
#         with open(TAG_MAPPING_FILE, "r") as f:
#             return json.load(f)
#     return {}
# 
# def save_mappings(mappings):
#     with open(TAG_MAPPING_FILE, "w") as f:
#         json.dump(mappings, f, indent=4)
# 
# # ----------------------------
# # Fetch book info from Koha (like checkout_logic)
# # ----------------------------
# def fetch_book_by_barcode(barcode):
# 
#     """Fetch item_id and title from Koha using barcode"""
#     try:
#         res = requests.get(
#             f"{KOHA_API_BASE}/items",
#             headers=get_auth_headers(),
#             timeout=TIMEOUT
#         )
#         res.raise_for_status()
#         items = res.json()
#     except Exception as e:
#         print("❌ Failed to fetch items from Koha:", e)
#         return None
# 
#     matched_item = None
#     for item in items:
#         if item.get("external_id") == barcode or item.get("barcode") == barcode:
#             matched_item = item
#             break
# 
#     if not matched_item:
#         return None
# 
#     item_id = matched_item.get("item_id")
#     biblio_id = matched_item.get("biblio_id")
# 
#     title = "Unknown Title"
#     if biblio_id:
#         try:
#             biblio_res = requests.get(
#                 f"{KOHA_API_BASE}/biblios/{biblio_id}",
#                 headers=get_auth_headers(),
#                 timeout=TIMEOUT
#             )
#             if biblio_res.status_code == 200:
#                 title = biblio_res.json().get("title", title)
#         except Exception:
#             pass
# 
#     return {"item_id": item_id, "barcode": barcode, "title": title}
# 
# # ----------------------------
# # Assign tag to book
# # ----------------------------
# def assign_tag(tag_id):
#     mappings = load_mappings()
# 
#     if tag_id in mappings:
#         print(f"⚠️ Tag '{tag_id}' is already assigned to item_id '{mappings[tag_id]}'")
#         confirm = input("Do you want to re-assign it? (y/n): ").strip().lower()
#         if confirm != "y":
#             print("❌ Assignment cancelled.")
#             return
# 
#     print(f"\n📶 Tag detected: {tag_id}")
#     confirm = input("Do you want to assign a book to this tag? (y/n): ").strip().lower()
#     if confirm != "y":
#         print("❌ Assignment cancelled.")
#         return
# 
#     barcode = input("Enter the Koha book barcode: ").strip()
#     book = fetch_book_by_barcode(barcode)
#     if not book:
#         print("❌ No book found with that barcode.")
#         return
# 
#     print(f"\nTag: {tag_id}")
#     print(f"Barcode: {book['barcode']}")
#     print(f"Title: {book['title']}")
#     confirm = input("Confirm assignment? (y/n): ").strip().lower()
#     if confirm != "y":
#         print("❌ Assignment cancelled.")
#         return
# 
#     mappings[tag_id] = book["item_id"]
#     save_mappings(mappings)
#     print("✅ Tag successfully assigned to book!")
# 
# # ----------------------------
# # Read tag from ACM815A via serial
# # ----------------------------
# def read_tag():
#     try:
#         ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)
#         print("📳 Waiting for UHF tag...")
#         while True:
#             data = ser.readline().strip()
#             if data:
#                 try:
#                     full_tag = data.decode().strip().upper()
#                 except:
#                     full_tag = data.hex().upper()
#                 # 🔹 Shorten tag
#                 short_tag = full_tag[:SHORT_TAG_LENGTH]
#                 return short_tag
#             time.sleep(0.1)
#     except Exception as e:
#         print("❌ Serial read error:", e)
#         return None
# 
# # ----------------------------
# # Main loop
# # ----------------------------
# if __name__ == "__main__":
#     print("📚 UHF Tag Assignment Tool - Ready")
#     while True:
#         tag = read_tag()
#         if tag:
#             assign_tag(tag)
#         time.sleep(0.2)

#!/usr/bin/env python3
import serial
import time
import json
import os
import requests
import base64
import re

# ----------------------------
# Config
# ----------------------------
TAG_MAPPING_FILE = "/home/admin/rfid_tag_tools/tag_mapping.json"
KOHA_API_BASE = "http://192.168.0.149:8080/api/v1"
USERNAME = "Administrator"
PASSWORD = "Zxcqwe123$"
SERIAL_PORT = "/dev/ttyUSB2_RS232Device"  # Wiegand reader
BAUDRATE = 57600
TIMEOUT = 10 

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
# Load/save tag mappings
# ----------------------------
def load_mappings():
    if os.path.exists(TAG_MAPPING_FILE):
        with open(TAG_MAPPING_FILE, "r") as f:
            return json.load(f)
    return {}

def save_mappings(mappings):
    with open(TAG_MAPPING_FILE, "w") as f:
        json.dump(mappings, f, indent=4)

# ----------------------------
# Fetch book info from Koha
# ----------------------------
def fetch_book_by_barcode(barcode):
    try:
        res = requests.get(f"{KOHA_API_BASE}/items", headers=get_auth_headers(), timeout=TIMEOUT)
        res.raise_for_status()
        items = res.json()
    except Exception as e:
        print("❌ Failed to fetch items from Koha:", e)
        return None

    for item in items:
        if item.get("external_id") == barcode or item.get("barcode") == barcode:
            item_id = item.get("item_id")
            biblio_id = item.get("biblio_id")
            title = "Unknown Title"
            if biblio_id:
                try:
                    biblio_res = requests.get(f"{KOHA_API_BASE}/biblios/{biblio_id}",
                                              headers=get_auth_headers(), timeout=TIMEOUT)
                    if biblio_res.status_code == 200:
                        title = biblio_res.json().get("title", title)
                except:
                    pass
            return {"item_id": item_id, "barcode": barcode, "title": title}

    return None

# ----------------------------
# Assign tag to book
# ----------------------------
def assign_tag(tag_id):
    mappings = load_mappings()

    if tag_id in mappings:
        print(f"⚠️ Tag '{tag_id}' is already assigned to item_id '{mappings[tag_id]}'")
        confirm = input("Do you want to re-assign it? (y/n): ").strip().lower()
        if confirm != "y":
            print("❌ Assignment cancelled.")
            return

    print(f"\n📶 Tag detected: {tag_id}")
    confirm = input("Do you want to assign a book to this tag? (y/n): ").strip().lower()
    if confirm != "y":
        print("❌ Assignment cancelled.")
        return

    barcode = input("Enter the Koha book barcode: ").strip()
    book = fetch_book_by_barcode(barcode)
    if not book:
        print("❌ No book found with that barcode.")
        return

    print(f"\nTag: {tag_id}")
    print(f"Barcode: {book['barcode']}")
    print(f"Title: {book['title']}")
    confirm = input("Confirm assignment? (y/n): ").strip().lower()
    if confirm != "y":
        print("❌ Assignment cancelled.")
        return

    mappings[tag_id] = book["item_id"]
    save_mappings(mappings)
    print("✅ Tag successfully assigned to book!")

# ----------------------------
# Read numeric Wiegand tag from ACM8
# ----------------------------
def read_tag():
    try:
        ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)
        print("📳 Waiting for Wiegand tag...")
        while True:
            line = ser.readline().decode(errors="ignore").strip()
            if line:
                # Extract numeric ID inside brackets
                match = re.search(r"\[(\d+)\]", line)
                if match:
                    tag_id = match.group(1)
                    return tag_id
            time.sleep(0.1)
    except Exception as e:
        print("❌ Serial read error:", e)
        return None

# ----------------------------
# Main loop
# ----------------------------
if __name__ == "__main__":
    print("📚 Wiegand Tag Assignment Tool - Ready")
    while True:
        tag = read_tag()
        if tag:
            assign_tag(tag)
        time.sleep(0.2)

