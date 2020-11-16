#!/usr/bin/env python

import threading
import signal
import time
import datetime
import os
import json
from random import randrange
import requests
import scrollphathd
from scrollphathd.fonts import font3x5, font5x5, font5x7
from envirophat import weather

print("""
prepare to be amazed...
=====================
""")

BRIGHTNESS = 0.2
# heat from the pi affects the reading
TEMP_OFFSET = 4
NEWSAPI_KEY = os.environ['NEWSAPI_KEY']

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

def display_news():
    r = requests.get('https://newsapi.org/v2/top-headlines?sources=bbc-news&apiKey={}'.format(NEWSAPI_KEY))
    #  r = requests.get('https://newsapi.org/v2/top-headlines?sources=bbc-news,nfl-news&pageSize=1&apiKey={}'.format(NEWSAPI_KEY))
    body = r.json()
    article = body['articles'][randrange(10)]

    #  print(json.dumps(article, indent=2))

    print(u"""
    {author}
    {title}

    {description}

    {url}

            * * * * * * * * * * * * * * * * * * * * * * * * 

    """.format(**article))

    scrollphathd.clear()
    scrollphathd.write_string('{author} - {title}'.format(**article), x=16, y=1, font=font3x5, brightness=BRIGHTNESS)

        
#  t = threading.Timer(sec)

news_is_on = False

while True:
    now = datetime.datetime.now()
    second = now.second
    minute = now.minute

    if (minute < 1):
        if (news_is_on == False):
            display_news()
            news_is_on = True
    elif (second > 0 and second < 15):
        news_is_on = False
        display_temp()
    elif (second > 15):
        display_time()

    scrollphathd.show()

    if (news_is_on == True):
        scrollphathd.scroll()
        time.sleep(0.04)
    else:
        time.sleep(0.1)
