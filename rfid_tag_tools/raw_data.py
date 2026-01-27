#!/usr/bin/env python3
import serial
import time
import binascii

# ----------------------------
# Config
# ----------------------------
SERIAL_PORT = "/dev/ttyUSB2_RS232Device"  # your ACM8 device
BAUDRATE = 57600
READ_TIMEOUT = 1

# ----------------------------
# ACM815A commands
# ----------------------------
INVENTORY_CMD = bytes.fromhex("01")       # inventory command
SWITCH_TO_UART_CMD = bytes.fromhex("A00401EA0000")  # switch Wiegand → UART/EPC

# ----------------------------
# Main loop
# ----------------------------
def main():
    try:
        ser = serial.Serial(
            SERIAL_PORT,
            BAUDRATE,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=READ_TIMEOUT
        )

        print(f"🔌 Connected to ACM8 at {BAUDRATE} baud")

        # Switch to UART/EPC mode
        ser.write(SWITCH_TO_UART_CMD)
        time.sleep(0.2)
        resp = ser.read(64)
        print("⚡ Mode switch response:", binascii.hexlify(resp).decode().upper())

        print("📳 Waiting for UHF tags (raw hex)...")

        while True:
            ser.write(INVENTORY_CMD)
            time.sleep(0.2)
            data = ser.read(256)
            if data:
                hex_data = binascii.hexlify(data).decode().upper()
                print("⬅️ RAW HEX DATA:", hex_data)

                # Count how many times 0x91 appears
                count_91 = hex_data.count("91")
                print("🔹 Count of 0x91 in data:", count_91)

            time.sleep(0.5)

    except Exception as e:
        print("❌ Serial error:", e)

if __name__ == "__main__":
    main()
