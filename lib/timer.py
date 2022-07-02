import time


class Timer:
    def __init__(self):
        self.startTime = time.time()
        self.endTime = time.time()

    def start(self):
        self.startTime = time.time() * 1000000000

    def stop(self):
        self.endTime = time.time() * 1000000000

    def getTime(self):
        return self.endTime - self.startTime
