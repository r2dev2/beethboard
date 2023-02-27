from contextlib import suppress
from struct import unpack, calcsize
import time
import os
import serial

buff_size = 256
port = 115200
device = os.environ.get("ARDUINO_BEETHBOARD_PORT", "/dev/ttyACM0")
freq = [1] * 500
data_fmt = "<Lh"
data_size = calcsize(data_fmt)

def parse_line(line: bytes):
    if len(line) != buff_size * data_size + 2:
        return []

    # collect each entry into line
    line = []
    for i in range(buff_size):
        start = i * data_size
        end = start + data_size
        line.append(unpack(data_fmt, line[start:end]))
    return line

def main():
    with serial.Serial(device, port) as ser:
        beg = time.time()
        for i, line in enumerate(ser):
            dur = time.time() - beg
            if i % (1000 // buff_size) == 0:
                print(i, dur, buff_size * i / dur)
                # timestamp, mic_val = map(int, line.split(","))
                # dt = (timestamp - freq[mic_val]) / 1000
                # print(timestamp, mic_val, int(1/dt))
                # freq[mic_val] = timestamp


if __name__ == "__main__":
    main()
