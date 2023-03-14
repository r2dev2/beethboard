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
from argparse import ArgumentParser
from collections import Counter

from recorder import Recorder, Commander
from fft import get_peaks, Peak
from typer import write

buff_size = 256
port = 115200
port = 853600
port = 2_500_000
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

def record(args):
    commander = Commander()
    recorder = Recorder(args.rdir)
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
    # obs = sorted(observed, key=lambda o: o.freq)[0].freq
    # exp = sorted(expected, key=lambda e: e.freq)[0].freq
    # return (obs - exp) ** 2 / exp
    exp_scale = 1 / expected[0].intensity
    ob_scale = 1 / observed[0].intensity
    return sum(
        (e.intensity * exp_scale + o.intensity * ob_scale) * (o.freq - e.freq) ** 2 / e.freq
        for o, e in zip(observed, expected)
    )
    chi1 =  sum((o.freq - e.freq) ** 2 / e.freq for o, e in zip(observed, expected))
    chi2 = sum((o.intensity * ob_scale - e.intensity * exp_scale) ** 2 / (e.intensity * exp_scale) for o, e in zip(observed, expected))
    chi2 *= observed[0].freq ** 2
    return chi1 + chi2


def detect(args):
    commander = Commander()
    measurements = []
    is_record = False
    batch_record = Counter()

    cal_peaks = []
    rdir = args.rdir
    for record in os.listdir(rdir):
        with open(rdir / record, "r") as fin:
            data = json.load(fin)[4096:4096*2]
        peaks = get_peaks(data)
        cal_peaks.append(CalibrationPeak(record, peaks))

    with serial.Serial(device, port) as ser:
        for batch in filter(bool, map(parse_line, ser)):
            measurements.extend(batch)
            measurements = measurements[-4096:]
            with suppress(BaseException):
                peaks = get_peaks(measurements)
                if peaks[0].intensity < 600:
                    if is_record:
                        most_common = batch_record.most_common()
                        if len(most_common):
                            l = most_common[0][0]
                            print("typing", l)
                            write(l)
                    batch_record.clear()
                    is_record = false
                    continue
                try:
                    chis = [(chi_square(peaks, cp.peaks), cp) for cp in cal_peaks]
                    cs, mat = min(chis)
                    if cs < 40:
                        note = "0abcdefghijklmnopqrstuvwxyz"[int(mat.iid.split(".")[0])]
                        print(note, peaks[0].intensity, cs)
                        is_record = True
                        batch_record.update(note)
                except Exception as e:
                    print(traceback.format_exc())


def main():
    parser = ArgumentParser()
    sub = parser.add_subparsers(help="subparsers")

    rec = sub.add_parser("record", help="record the notes")
    det = sub.add_parser("detect", help="detect the notes")

    rec.add_argument(
        "-r",
        "--rdir",
        help="record dir",
        type=Path,
        default=Path("recording")
    )
    det.add_argument(
        "-r",
        "--rdir",
        help="record dir",
        type=Path,
        default=Path("recording")
    )

    rec.set_defaults(func=record)
    det.set_defaults(func=detect)

    args = parser.parse_args()
    if "func" not in args:
        print("ERR: specify a subcommand", file=sys.stderr)
        return 1
    args.func(args)


if __name__ == "__main__":
    main()
