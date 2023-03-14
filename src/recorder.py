import json
import time
from contextlib import suppress
from pathlib import Path
from queue import Queue
from threading import Thread


class Recorder(Thread):
    def __init__(self, record_dir):
        super().__init__(daemon=True)
        self._record_dir = record_dir
        self._is_recording = False
        self._name = "owo"
        self._data = Queue()
        self._record_dir.mkdir(exist_ok=True)
        self.start()

    def save_data(self, data):
        if not self._is_recording:
            return
        self._data.put(data)

    def start_record(self, name):
        self._name = name
        self._is_recording = True

    def stop_record(self):
        self._is_recording = False
        self._data.put(None)

    def run(self):
        while 1:
            if not self._is_recording:
                time.sleep(0.1)
                continue
            beg = time.time()
            all_data = []
            batch = []
            while batch is not None:
                all_data.extend(batch)
                batch = self._data.get()
            with open(self._record_dir / f"{self._name}.json", "w+") as fout:
                json.dump(all_data, fout)


class Commander(Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self._cmd = Queue()
        self.start()

    def get_cmd(self):
        if self._cmd.empty():
            return None
        return self._cmd.get()

    def run(self):
        while 1:
            uin = input(">>> ")
            with suppress(Exception):
                cmd = uin.split(" ")
                self._cmd.put(cmd)
