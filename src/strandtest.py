#!/usr/bin/python

# Simple strand test for Adafruit Dot Star RGB LED strip.
# This is a basic diagnostic tool, NOT a graphics demo...helps confirm
# correct wiring and tests each pixel's ability to display red, green
# and blue and to forward data down the line.  By limiting the number
# and color of LEDs, it's reasonably safe to power a couple meters off
# USB.  DON'T try that with other code!

import time
import RPi.GPIO as GPIO
from dotstar import Adafruit_DotStar

numpixels = 240 # Number of LEDs in strip

# Here's how to control the strip from any two GPIO pins:
datapin  = 23
clockpin = 24
strip    = Adafruit_DotStar(numpixels, 12 * 1000 * 1000)

# Alternate ways of declaring strip:
#  Adafruit_DotStar(npix, dat, clk, 1000000) # Bitbang @ ~1 MHz
#  Adafruit_DotStar(npix)                    # Use SPI (pins 10=MOSI, 11=SCLK)
#  Adafruit_DotStar(npix, 32000000)          # SPI @ ~32 MHz
#  Adafruit_DotStar()                        # SPI, No pixel buffer
#  Adafruit_DotStar(32000000)                # 32 MHz SPI, no pixel buf
# See image-pov.py for explanation of no-pixel-buffer use.
# Append "order='gbr'" to declaration for proper colors w/older DotStar strips)

strip.begin()           # Initialize pins for output
strip.setBrightness(255) # Limit brightness to ~1/4 duty cycle

# Runs 10 LEDs at a time along strip, cycling through red, green and blue.
# This requires about 200 mA for all the 'on' pixels + 1 mA per 'off' pixel.

trail_length = 237	# how many lights in the trail are turned on?
head_index  = 0               			# Index of first 'on' pixel
tail_index  = head_index - trail_length 	# Index of last 'off' pixel
color = 0xFFFFFF        # 'On' color (starts red)

try:
	going_up = True
	_brightness = 0.0
	_brightness_interval = 255.0/(numpixels * 20 * 2)
	_max_brightness = 255
	_min_brightness = 0

	count = 0
	while True:                              # Loop forever
		count += 1		

		#if going_up == True and _brightness <= _max_brightness:
		#	_brightness += _brightness_interval
		#	if _brightness > _max_brightness:
		#		going_up = False
		#		_brightness = _max_brightness

		#if going_up == False and _brightness >= 0.0:
		#	_brightness -= _brightness_interval
		#	if _brightness < _min_brightness:
		#		going_up = True
		#		_brightness = _min_brightness

		#_int_bright = int(_brightness)		

		#for idx in range(numpixels):
		#	strip.setPixelColor(idx, color)

		###############
		#### Comet ####
		###############
		color_slice = (255.0 / (trail_length * 1.0))

		for idx in range(numpixels):
			current_index = idx
			if idx >= head_index and idx <= head_index + trail_length:
				color_int = int(255 - (idx - head_index) * color_slice)
			       	color = (color_int * 2**16) + (color_int * 2**8) + color_int
			else:
				color = 0x000000
			
			if current_index >= numpixels:
				current_index -= numpixels
				strip.setPixelColor(current_index, color)
			else:
				strip.setPixelColor(current_index, color)				

		#print "_int_bright: " + str(_int_bright)		
		#strip.setPixelColor(head_index, color) # Turn on 'head' pixel
		#strip.setPixelColor(tail_index, 0)     # Turn off 'tail'
		
		#strip.setBrightness(_int_bright)
		strip.show()                     # Refresh strip
		
		#if count < 250:
		#	fps = (1.0 / 50.0)
		#else:
		#	fps = (1.0 / 150.0)

		fps = (1.0 / 50.0)
		time.sleep(fps)             # Pause 20 milliseconds (~50 fps)

		#head_index += 1                        # Advance head position
		#if(head_index >= numpixels):           # Off end of strip?
		#	head_index    = 0              # Reset to start
			# color >>= 8              # Red->green->blue->black
			# if(color == 0): color = 0xFF0000 # If black, reset to red

		#tail_index += 1                        # Advance tail position
		#if(tail_index >= numpixels): tail_index = 0  # Off end? Reset

except KeyboardInterrupt:
	print "cleaning up"
	# GPIO.cleanup()
	strip.clear()
	strip.show()
	print "done"
