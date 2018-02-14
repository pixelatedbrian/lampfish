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
import pika
import multiprocessing
import psutil

# Alternate ways of declaring strip:
#  Adafruit_DotStar(npix, dat, clk, 1000000) # Bitbang @ ~1 MHz
#  Adafruit_DotStar(npix)                    # Use SPI (pins 10=MOSI, 11=SCLK)
#  Adafruit_DotStar(npix, 32000000)          # SPI @ ~32 MHz
#  Adafruit_DotStar()                        # SPI, No pixel buffer
#  Adafruit_DotStar(32000000)                # 32 MHz SPI, no pixel buf
# See image-pov.py for explanation of no-pixel-buffer use.
# Append "order='gbr'" to declaration for proper colors w/older DotStar strips)


def callback(ch, method, properties, body):
    ''' data is a string that will be parsed by the receiving end and turned
        into light string commands.  String should be in the format of:
        mode_brightness
        ex: 'on_255' OR 'on_128' OR 'off_0'
    '''
    print("callback -> received:", body)

    mode = body.split("_")[0]
    brightness = int(body.split("_")[1])

    task_runner(mode, brightness)


def task_runner(mode, brightness):
    processes = psutil.Process().children()
    for p in processes:
        p.kill()
    process = multiprocessing.Process(target=run_strip, args=(mode, brightness,))
    process.start()


def consume_pika_queue():
    # consume messages from a queue using pika/rabbit-mq
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='lampfish')

    channel.basic_consume(callback,
                          queue="lampfish",
                          no_ack=True)

    channel.start_consuming()


def run_strip(mode="off", brightness=255):

    numpixels = 240     # Number of LEDs in strip

    print("run_strip inbound mode:", mode)
    # Here's how to control the strip from any two GPIO pins:
    # datapin = 10
    # clockpin = 11
    strip = Adafruit_DotStar(numpixels, 12000000)

    # brightness is an integer from 1 to 255
    # mode, in time, should enable other things besides just being full on

    # strip.begin()                       # Initialize pins for output
    # strip.setBrightness(brightness)     # Limit brightness to ~1/4 duty cycle

    # used for mode: comet
    # head = 0               # Index of first 'on' pixel
    # tail = -10             # Index of last 'off' pixel
    color = 0xFFFFFF        # 'On' color (starts red)

    # some control variables for light power on/off easing
    _pow = 3
    _frames = 50
    _maxb = 255    # _max_brightness, might change when brightness configuration is enabled

    if mode == "off":
        print("run_strip: turn off strip")

        try:
            count = 0
            const = _maxb**(1 /(_pow * 1.0))
            is_turning_off = True
            strip.begin()

            while is_turning_off:
                count += 1

                if count == _frames:
                    is_turning_off = False
                    strip.setBrightness(_maxb)  # now that ramping is done set
                                                # to max configured brightness
                else:
                    brightness = int(_maxb - (count / (_frames * 1.0) * const)**_pow)
                    strip.setBrightness(brightness)

                for idx in range(numpixels):
                    strip.setPixelColor(idx, color)

                strip.show()                     # Refresh strip
                time.sleep(1.0 / 50)

        except KeyboardInterrupt:
            print "cleaning up"
            GPIO.cleanup()
            strip.clear()
            strip.show()
            print "done"

        # try to set color to black/off before turning off to prevent final flash
        for idx in range(numpixels):
            strip.setPixelColor(idx, 0x000000)
        strip.setBrightness(0)

        # clean up interrupts?
        # GPIO.cleanup()
        # strip.clear()
        strip.show()
        # print("done")

    elif mode == "on":
        print("run_strip: starting strip")
        try:
            count = 0
            const = _maxb**(1 /(_pow * 1.0))
            is_turning_on = True

            strip.begin()

            while True:                              # Loop forever

                if is_turning_on:
                    count += 1.0

                    if count == _frames:
                        is_turning_on = False
                        strip.setBrightness(_maxb)  # now that ramping is done set
                                                    # to max configured brightness
                    else:
                        brightness = int((count / (_frames * 1.0) * const)**_pow)
                        strip.setBrightness(brightness)

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

        except SystemError as err:
            print("SystemError:", err)


if __name__ == "__main__":
    consume_pika_queue()
