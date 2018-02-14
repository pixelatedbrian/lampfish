#!/usr/bin/python
# Author: Brian Hardenstein

# Simple strand test for Adafruit Dot Star RGB LED strip.
# This is a basic diagnostic tool, NOT a graphics demo...helps confirm
# correct wiring and tests each pixel's ability to display red, green
# and blue and to forward data down the line.  By limiting the number
# and color of LEDs, it's reasonably safe to power a couple meters off
# USB.  DON'T try that with other code!

import time
import RPi.GPIO as GPIO
from dotstar import Adafruit_DotStar
from flask import Flask, render_template, request
app = Flask(__name__)

numpixels = 240     # Number of LEDs in strip

# Here's how to control the strip from any two GPIO pins:
datapin = 10
clockpin = 11
strip = Adafruit_DotStar(numpixels, 12000000)

# Alternate ways of declaring strip:
#  Adafruit_DotStar(npix, dat, clk, 1000000) # Bitbang @ ~1 MHz
#  Adafruit_DotStar(npix)                    # Use SPI (pins 10=MOSI, 11=SCLK)
#  Adafruit_DotStar(npix, 32000000)          # SPI @ ~32 MHz
#  Adafruit_DotStar()                        # SPI, No pixel buffer
#  Adafruit_DotStar(32000000)                # 32 MHz SPI, no pixel buf
# See image-pov.py for explanation of no-pixel-buffer use.
# Append "order='gbr'" to declaration for proper colors w/older DotStar strips)


def run_strip(brightness=255, mode="default"):
    # brightness is an integer from 1 to 255
    # mode, in time, should enable other things besides just being full on

    strip.begin()                       # Initialize pins for output
    strip.setBrightness(brightness)     # Limit brightness to ~1/4 duty cycle

    # Runs 10 LEDs at a time along strip, cycling through red, green and blue.
    # This requires about 200 mA for all the 'on' pixels + 1 mA per 'off' pixel.

    # used for mode: comet
    # head = 0               # Index of first 'on' pixel
    # tail = -10             # Index of last 'off' pixel
    color = 0xFFFFFF        # 'On' color (starts red)

    try:
        while True:                              # Loop forever

            for idx in range(numpixels):
                strip.setPixelColor(idx, color)

            # strip.setPixelColor(head, color) # Turn on 'head' pixel
            # strip.setPixelColor(tail, 0)     # Turn off 'tail'
            strip.show()                     # Refresh strip
            time.sleep(1.0 / 50)             # Pause 20 milliseconds (~50 fps)

            # head += 1                        # Advance head position
            # if(head >= numpixels):           # Off end of strip?
            #    head    = 0              # Reset to start
            #    color >>= 8              # Red->green->blue->black
            #    if(color == 0): color = 0xFF0000 # If black, reset to red

            # tail += 1                        # Advance tail position
            # if(tail >= numpixels): tail = 0  # Off end? Reset

    except KeyboardInterrupt:
        print "cleaning up"
        GPIO.cleanup()
        strip.clear()
        strip.show()
        print "done"


@app.route("/")
def main():
    mode_data = {"lamp_on": False,
                 "lamp_brigtness": 255}

    # For each pin, read the pin state and store it in the pins dictionary:
    # for pin in pins:
    #     pins[pin]['state'] = GPIO.input(pin)
    #
    # # Put the pin dictionary into the template data dictionary:
    # templateData = {'pins': pins}

    # Pass the template data into the template main.html and return it to the user
    return render_template('main.html', **mode_data)


# The function below is executed when someone requests a URL with the pin number and action in it:
@app.route("/<changePin>/<action>")
def action(changePin, action):
    # Convert the pin from the URL into an integer:
    changePin = int(changePin)
    # Get the device name for the pin being changed:
    deviceName = pins[changePin]['name']
    # If the action part of the URL is "on," execute the code indented below:
    if action == "on":
        # Set the pin high:
        GPIO.output(changePin, GPIO.HIGH)
        # Save the status message to be passed into the template:
        message = "Turned " + deviceName + " on."

    if action == "off":
        GPIO.output(changePin, GPIO.LOW)
        message = "Turned " + deviceName + " off."

    # For each pin, read the pin state and store it in the pins dictionary:
    for pin in pins:
        pins[pin]['state'] = GPIO.input(pin)

    # Along with the pin dictionary, put the message into the template data dictionary:
    templateData = {
        'pins' : pins
        }

    return render_template('main.html', **mode_data)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)
