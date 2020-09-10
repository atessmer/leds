#!/usr/bin/env python3

import pigpio
import signal
import time

FREQUENCY = 38      # (38 kHz)
GPIO = 18           # Pin 18



def khz_to_usec(khz):
    return int((1/khz) * 1000)


def main():
    pi = pigpio.pi()
    pi.set_mode(GPIO, pigpio.OUTPUT)

    pi.wave_clear()

    pi.wave_add_generic([
        pigpio.pulse(1<<GPIO, 0, khz_to_usec(FREQUENCY*2)),
        pigpio.pulse(0, 1<<GPIO, khz_to_usec(FREQUENCY*2)),
    ])
    wid_mark = pi.wave_create()

    pi.wave_add_generic([
        pigpio.pulse(0, 0, khz_to_usec(FREQUENCY)),
    ])
    wid_space = pi.wave_create()

    pi.wave_chain([
        255, 0,             # loop (A) start
        255, 0,             # loop (B) start
        wid_mark,           # transmit mark wave
        255, 1, 38, 0,      # loop (B) end: 38 times; 38 * 26us = ~ 1000 usec
        255, 0,             # loop (C) start
        wid_space,          # transmit space wave
        255, 1, 38, 0,      # loop (C) end: 38 times; 38 * 26us = ~1000 usec
        255, 3,             # loop (A) repeat forever
    ])

    try:
        while pi.wave_tx_busy():
            time.sleep(0.1)
    except KeyboardInterrupt:
        pi.wave_tx_stop()

    pi.wave_delete(wid_mark)
    pi.wave_delete(wid_space)


if __name__ == '__main__':
    main()
