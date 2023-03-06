from contextlib import suppress
from struct import unpack, calcsize
from pathlib import Path
import json
import time
import os
import serial

from recorder import Recorder, Commander

buff_size = 16
port = 115200
port = 153600
# port = 2457600
device = os.environ.get("ARDUINO_BEETHBOARD_PORT", "/dev/ttyACM0")
freq = [1] * 500
data_fmt = "<Lh"
data_size = calcsize(data_fmt)

def parse_line(line: bytes):
    # print(len(line))
    if len(line) != buff_size * data_size + 2:
        return []

    # collect each entry into line
    lino = []
    for i in range(buff_size):
        start = i * data_size
        end = start + data_size
        lino.append(unpack(data_fmt, line[start:end]))
    return lino

def main():
    commander = Commander()
    recorder = Recorder(Path("recordings"))
    with serial.Serial(device, port) as ser:
        for batch in filter(bool, map(parse_line, ser)):
            command = commander.get_cmd()
            if command is not None:
                cmd, *args = command
                if cmd in {"r", "record"} and len(args) >= 1:
                    recorder.start_record(args[0])
                if cmd in {"s", "stop"}:
                    recorder.stop_record()
            recorder.save_data(batch)

    # all_lines = []
    # with serial.Serial(device, port) as ser:
    #     beg = time.time()
    #     for i, batch in enumerate(filter(bool, map(parse_line, ser))):
    #         if i == 0:
    #             beg = time.time()
    #         all_lines.extend(batch)
    #         # print(len(all_lines), batch[0], batch[-1])
    #         # print(len(all_lines) / (time.time() - beg))
    #         # debug after 30s
    #         if time.time() - beg > 10:
    #             with open("owo.json", "w+") as fout:
    #                 json.dump(all_lines, fout)
    #                 return


if __name__ == "__main__":
    main()
