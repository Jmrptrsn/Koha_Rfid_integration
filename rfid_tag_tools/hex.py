#!/usr/bin/env python3
import serial
import time

# ----------------------------
# Config
# ----------------------------
SERIAL_PORT = "/dev/ttyUSB2_RS232Device"  # ACM8/ACM815A RS232 port
BAUDRATE = 57600
TIMEOUT = 1  # seconds

# ----------------------------
# Main
# ----------------------------
try:
    ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=TIMEOUT)
    print(f"🔌 Connected to {SERIAL_PORT} at {BAUDRATE} baud")
    print("📳 Waiting for UHF tags... (press Ctrl+C to stop)\n")

    while True:
        # Read a line from the reader
        data = ser.readline()
        if data:
            # Convert raw bytes to hex string
            hex_data = data.hex().upper()
            print(f"🔹 Raw tag hex: {hex_data}")

        time.sleep(0.1)

except serial.SerialException as e:
    print(f"❌ Serial error: {e}")

except KeyboardInterrupt:
    print("\n👋 Stopping...")

finally:
    if 'ser' in locals() and ser.is_open:
        ser.close()
    print("🔌 Serial port closed")
