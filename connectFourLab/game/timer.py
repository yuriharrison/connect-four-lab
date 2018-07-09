import time
from threading import Thread


class Chronometer:

    def __init__(self):
        self.running = False
        self.__start = None
        self.__end = None
        self.__stop_partial = 0
    
    def __enter__(self):
        self.start()

    def __exit__(self, *i):
        self.stop()

    def start(self):
        if self.running == True:
            return True

        self.running = True
        self.__start = time.clock()

    def reset(self):
        self.stop(reset=True)

    def stop(self, reset=False):
        if reset:
            self.__stop_partial = 0
        else:
            self.__stop_partial = self.partial

        self.running = False

    @property
    def partial(self):
        if self.running:
            return time.clock() - self.__start + self.__stop_partial
        else:
            return self.__stop_partial


class Timer(Chronometer):

    def __init__(self, time, callback=None):
        super().__init__()

        self.time_limit = time
        self.callback = callback
        self.__thread = None

    def __copy__(self):
        new = type(self)(None, None)
        new.__dict__.update(self.__dict__)
        new.callback = None
        return self

    def __deepcopy__(self, memo):
        return self.__copy__()


    def register_new_callback(self, event):
        self._callbacks.append(event)

    def start(self):
        super().start()

        self.__thread = Thread(target=self._time_out)
        self.__thread.start()

    def stop(self, *i):
        super().stop(*i)

        if self.__thread.is_alive():
            self.__kill_thread = True

    @property
    def time_left(self):
        time_left = self.time_limit - self.partial
        time_left = time_left if time_left > 0 else 0
        return time_left

    def _time_out(self):
        while True:
            if self.running:
                if self.partial < self.time_limit:
                    time.sleep(.2)
                else:
                    if self.callback:
                        self.callback()
                    break
            else:
                break

