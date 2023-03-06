import traceback
from typing import NamedTuple
from contextlib import suppress
from struct import unpack, calcsize
from pathlib import Path
import json
import time
import os
import serial
import sys

from recorder import Recorder, Commander
from fft import get_peaks, Peak

buff_size = 16
port = 115200
port = 153600
# port = 2457600
device = os.environ.get("ARDUINO_BEETHBOARD_PORT", "/dev/ttyACM0")
freq = [1] * 500
data_fmt = "<Lh"
data_size = calcsize(data_fmt)

class CalibrationPeak(NamedTuple):
    iid: str
    peaks: list[Peak]

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

def record():
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
                if cmd in {"q", "quit", "exit"}:
                    exit()
            recorder.save_data(batch)


def chi_square(observed, expected):
    exp_scale = 1 / expected[0].intensity
    ob_scale = 1 / observed[0].intensity
    chi1 =  sum((o.freq - e.freq) ** 2 / e.freq for o, e in zip(observed, expected))
    chi2 = sum((o.intensity * ob_scale - e.intensity * exp_scale) ** 2 / (e.intensity * exp_scale) for o, e in zip(observed, expected))
    chi2 *= observed[0].freq
    return chi1 + chi2


def detect():
    commander = Commander()
    measurements = []

    cal_peaks = []
    rdir = Path("recordings")
    for record in os.listdir(rdir):
        with open(rdir / record, "r") as fin:
            data = json.load(fin)
        peaks = get_peaks(data)
        cal_peaks.append(CalibrationPeak(record, peaks))

    with serial.Serial(device, port) as ser:
        for batch in filter(bool, map(parse_line, ser)):
            measurements.extend(batch)
            measurements = measurements[-1000:]
            with suppress(Exception):
                peaks = get_peaks(measurements)
                if peaks[0].intensity < 600:
                    continue
                # try:
                #     print(chi_square(peaks, cal_peaks[0].peaks))
                # except Exception as e:
                #     print(e)
                # print(peaks)
                try:
                    chis = [(chi_square(peaks, cp.peaks), cp) for cp in cal_peaks]
                    cs, mat = min(chis)
                    # if cs > 300:
                    print(mat.iid.split(".")[0], cs)
                except Exception as e:
                    print(traceback.format_exc())
                # print(chis)
                # print(chis[0][1])


def main():
    if "--record" in sys.argv:
        record()
    else:
        detect()


if __name__ == "__main__":
    main()
