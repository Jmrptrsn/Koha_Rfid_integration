import serial
import json

TAG_FILE = "tag_mapping.json"

# Initialize serial for ACM815A-USB
ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)

# Load mappings
try:
    with open(TAG_FILE, 'r') as f:
        tag_mapping = json.load(f)
except FileNotFoundError:
    tag_mapping = {}

def scan_tag():
    print("Tap your tag on the reader...")
    while True:
        tag = ser.readline().decode('utf-8').strip()
        if tag:
            print(f"Tag scanned: {tag}")
            return tag

def main():
    tag = scan_tag()

    if tag in tag_mapping:
        print(f"This tag is assigned to Koha item: {tag_mapping[tag]}")
    else:
        print("Tag not assigned yet!")

if __name__ == "__main__":
    main()
