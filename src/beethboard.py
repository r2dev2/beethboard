from contextlib import suppress
import time
import os
import serial

port = 9600
device = os.environ.get("ARDUINO_BEETHBOARD_PORT", "/dev/ttyACM0")
freq = [1] * 500

def main():
    with serial.Serial(device, port) as ser:
        beg = time.time()
        for i, line in enumerate(ser):
            with suppress(Exception):
                line = line.decode().strip()
                timestamp, mic_val = map(int, line.split(","))
                dt = (timestamp - freq[mic_val]) / 1000
                print(timestamp, mic_val, int(1/dt))
                freq[mic_val] = timestamp


if __name__ == "__main__":
    main()
