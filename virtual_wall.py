#!/usr/bin/env python3

import pigpio
import signal
import time

FREQUENCY = 38      # (38 kHz)
GPIO = 18           # Pin 18



def khz_to_usec(khz):
    return int((1/khz) * 1000)


class WaveChain:
    # Documentation at http://abyz.me.uk/rpi/pigpio/python.html#wave_chain

    @staticmethod
    def _decompose_cmd_count(n):
        """ Convert a command count to the x,y form used by wave chains """
        x = n % 256
        y = int(n / 256)
        return [x, y]

    def __init__(self, pi):
        self.pi = pi
        self.data = []

    def start_loop(self):
        """ Start a new loop """
        self.data += [255, 0]

    def end_loop(self, repeat):
        """ End the current loop after 'repeat' iterations """
        self.data += [255, 1] + self._decompose_cmd_count(repeat)

    def delay(self, duration):
        """ Add a 'duration' microsecond delay """
        self.data += [255, 2] + self._decompose_cmd_count(duration)

    def loop_forever(self):
        self.data += [255, 3]

    def transmit_wave(self, wave_id):
        self.data += [wave_id]

    def start(self):
        self.pi.wave_chain(self.data)


def main():
    pi = pigpio.pi()
    pi.set_mode(GPIO, pigpio.OUTPUT)

    pi.wave_clear()

    pi.wave_add_generic([
        pigpio.pulse(1<<GPIO, 0, khz_to_usec(FREQUENCY*2)),
        pigpio.pulse(0, 1<<GPIO, khz_to_usec(FREQUENCY*2)),
    ])
    mark_usec = pi.wave_get_micros()
    mark_wid = pi.wave_create()

    wc = WaveChain(pi)
    wc.start_loop()                     # loop (A)
    wc.start_loop()                     # loop (B)
    wc.transmit_wave(mark_wid)
    wc.end_loop(int(1000/mark_usec))    # loop (B); ~1000 usec
    wc.delay(1000)
    wc.loop_forever()                   # loop (A)
    wc.start()

    try:
        while pi.wave_tx_busy():
            time.sleep(0.1)
    except KeyboardInterrupt:
        pi.wave_tx_stop()

    pi.wave_delete(mark_wid)


if __name__ == '__main__':
    main()
