#!/usr/bin/env python

import threading
import signal
import time

from envirophat import weather

import scrollphathd
from scrollphathd.fonts import font3x5
from scrollphathd.fonts import font5x5

print("""
prepare to be amazed...
=====================
""")

BRIGHTNESS = 0.2
# heat from the pi affects the reading
TEMP_OFFSET = 4

# TODO alternate between temp, clock, latest news
# TODO report statsd, graphite dashboard
# TODO websockets control + PWA
# TODO slack notication count / last notification

def display_temp():
    scrollphathd.clear()
    temp = weather.temperature() - TEMP_OFFSET
    scrollphathd.write_string(' {}c'.format(str(int(temp))), y=1, font=font3x5, brightness=BRIGHTNESS)

def display_time():
    scrollphathd.clear()

    # Grab the "seconds" component of the current time
    # and convert it to a range from 0.0 to 1.0
    float_sec = (time.time() % 60) / 59.0

    # Multiply our range by 15 to spread the current
    # number of seconds over 15 pixels.
    #
    # 60 is evenly divisible by 15, so that
    # each fully lit pixel represents 4 seconds.
    #
    # For example this is 28 seconds:
    # [x][x][x][x][x][x][x][ ][ ][ ][ ][ ][ ][ ][ ]
    #  ^ - 0 seconds                59 seconds - ^
    seconds_progress = float_sec * 15

    # Step through 15 pixels to draw the seconds bar
    for y in range(15):
        # For each pixel, we figure out its brightness by
        # seeing how much of "seconds_progress" is left to draw
        # If it's greater than 1 (full brightness) then we just display 1.
        current_pixel = min(seconds_progress, 1)

        # Multiply the pixel brightness (0.0 to 1.0) by our global brightness value
        scrollphathd.set_pixel(y + 1, 6, current_pixel * BRIGHTNESS)

        # Subtract 1 now we've drawn that pixel
        seconds_progress -= 1

        # If we reach or pass 0, there are no more pixels left to draw
        if seconds_progress <= 0:
            break

    # Display the time (HH:MM) in a 5x5 pixel font
    scrollphathd.write_string(
        time.strftime("%H:%M"),
        x=0, # Align to the left of the buffer
        y=0, # Align to the top of the buffer
        font=font3x5, # Use the font5x5 font we imported above
        brightness=BRIGHTNESS # Use our global brightness value
    )

    # int(time.time()) % 2 will tick between 0 and 1 every second.
    # We can use this fact to clear the ":" and cause it to blink on/off
    # every other second, like a digital clock.
    # To do this we clear a rectangle 8 pixels along, 0 down,
    # that's 1 pixel wide and 5 pixels tall.
    if int(time.time()) % 2 == 0:
        scrollphathd.clear_rect(8, 0, 1, 5)
        
#  t = threading.Timer(sec)
while True:
    seconds = int(time.time()) % 60

    if (seconds > 0 and seconds < 30):
        display_temp()
    elif (seconds > 30):
        display_time()

    scrollphathd.show()
    #  scrollphathd.scroll()
    time.sleep(0.1)

