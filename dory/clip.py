import threading
import pyperclip as pc
from time import sleep


class Clip:
    def __init__(self, function, tick=20, thread=False, copy=False):
        self.now = ''
        self.tick = 1 / tick
        self.function = function
        self.thread = thread
        self.copy = copy

    def run(self):
        while True:
            sleep(self.tick)
            now = self._check()
            if now:
                if self.thread:
                    self._run_thread()
                elif self.copy:
                    self._copy()
                else:
                    self.function(self.now)

    def _run_thread(self):
        threading.Thread(target=self.function, args=(self.now,)).start()

    def _copy(self):
        result = self.function(self.now)
        self.now = result
        pc.copy(result)

    def _check(self):
        new = pc.paste()
        if new == self.now:
            return None
        else:
            self.now = new
            return new
