# -*- coding: utf-8 -*-

# as per http://askubuntu.com/questions/73396/how-to-get-espeak-working:
# IF ESPEAK FAILS, MUST DO "amixer cset numid=3 1" (1=3.5mm jack, 2=HDMI)

import sys, os
import RPIO as GPIO
import requests
import arrow
import time

input_ch = 2

prev_input = 0
prev_ts = 0
button_depressed = False
timedelta = 3
endpoint = 'http://sanchopanza.local:5000/api/coffees'

def get_latest_and_speak():
    try:
        resp = requests.get(endpoint)
        prev_coffee = arrow.get(resp.json()['latest'])
        os.system('espeak -v fi "{}"'.format('Kahvi on valmistettu ' + prev_coffee.humanize(locale='fi')))
    except:
        os.system('espeak -v fi "{}"'.format('En tiedä milloin kahvi on valmistettu. Palvelin ei vastaa.'))
    finally:
        time.sleep(2)

def post_made_coffee():
    try:
        resp = requests.post(endpoint)
        os.system('espeak -v fi "{}"'.format('Rekisteröity kahvin uuttamisen aloitus.'))
    except:
        os.system('espeak -v fi "{}"'.format('Ei saatu yhteyttä palvelimeen.'))
    finally:
        time.sleep(2)

if __name__=="__main__":
    print('setting up')
    # GPIO.setmode(GPIO.BCM)
    GPIO.setup(input_ch, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    try:
        while True:
            input = GPIO.input(input_ch)

            # so here we look for the edges manually and sleep a bit to try to ignore the bouncing

            # going from 0 -> 1: BUTTON WENT DOWN
            if (not prev_input) and input and (not button_depressed):
                print('button down')
                button_depressed = True
                prev_ts = time.perf_counter()

            # button is at 1 (pressed down).
            # if it's been down long enough, POST to server
            elif input and button_depressed:
                # down long enough?
                if (time.perf_counter() - prev_ts > timedelta):
                    button_depressed = False
                    # print('REGISTERED')
                    post_made_coffee()
                    time.sleep(1)

            # going from 1 -> 0: BUTTON WENT UP...
            # ...before time was up, so just GET the latest timestamp
            elif (not input) and prev_input and button_depressed:
                button_depressed = False
                if (time.perf_counter() - prev_ts <= timedelta):
                    # print('button up SHORT')
                    get_latest_and_speak()

            prev_input = input
            time.sleep(0.1)

    except KeyboardInterrupt:
        print('interrupted!')
        GPIO.cleanup()
