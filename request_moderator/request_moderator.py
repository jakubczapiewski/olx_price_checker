import time


class TimeModerator:
    def __init__(self, rpm: int):
        self._last_request_time = 0
        self.rps = (rpm - 1) / 60

    def __enter__(self):
        delta_t = (time.time() - self._last_request_time) - (1 / self.rps)
        if delta_t < 0:
            time.sleep(abs(delta_t))

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._last_request_time = time.time()
