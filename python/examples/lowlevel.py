# Example of low-level rpi_ws281x Python module.
#
# This is an example of how to use the SWIG-generated _rpi_ws281x module.
# You probably don't want to use this unless you are building your own library,
# because the SWIG generated module is clunky and verbose.  Instead look at the
# high level Python wrapper around the SWIG module in rainbow.py.
#
# This code will animate a number of WS281x LEDs displaying rainbow colors.

import time

# Import the low level library and give it a smaller name.
import _rpi_ws281x as ws

# LED configuration.
LED_COUNT      = 16        # How many LEDs to light.
LED_FREQ_HZ    = 800000    # Frequency of the LED signal.  Should be 800khz or 400khz.
LED_DMA_NUM    = 5         # DMA channel to use, can be 0-14.
LED_GPIO       = 18        # GPIO connected to the LED signal line.  Must support PWM!
LED_INVERT     = 0         # Set to 1 to invert the LED signal, good if using NPN
                           # transistor as a 3.3V->5V level converter.  Keep at 0
                           # for a normal/non-inverted signal.

# Define colors which will be used by the example.  Each color is an unsigned
# 32-bit value where the lower 24 bits define the red, green, blue data (each
# being 8 bits long).
DOT_COLORS = [ 0x200000,   # red
               0x201000,   # orange
               0x202000,   # yellow
               0x002000,   # green
               0x002020,   # lightblue
               0x000020,   # blue
               0x100010,   # purple
               0x200010 ]  # pink


# Create a ws2811_t structure from the LED configuration.
# Note that this structure will be created on the heap so you need to be careful
# that you delete its memory by calling delete_ws2811_t when it's not needed.
leds = ws.new_ws2811_t()
ws.ws2811_t_count_set(leds, LED_COUNT)
ws.ws2811_t_freq_set(leds, LED_FREQ_HZ)
ws.ws2811_t_dmanum_set(leds, LED_DMA_NUM)
ws.ws2811_t_gpionum_set(leds, LED_GPIO)
ws.ws2811_t_invert_set(leds, LED_INVERT)

# Create an array of LED data. You don't need to clean this up because the fini
# function will free it automatically.
led_data = ws.new_led_data(LED_COUNT)

# Initialize library with LED configuration.
resp = ws.ws2811_init(leds)
if resp != 0:
  raise RuntimeError('ws2811_init failed with code {0}'.format(resp))

# Wrap following code in a try/finally to ensure cleanup functions are called
# after library is initialized.
try:
  # Set LED data array on the ws2811_t structure.  Be sure to do this AFTER the
  # init function is called as it clears out the LEDs.
  ws.ws2811_t_leds_set(leds, led_data)
  # Loop forever or until ctrl-c is pressed.
  offset = 0
  while True:
    # Update each LED color in the buffer.
    for i in range(LED_COUNT):
      # Pick a color based on LED position and an offset for animation.
      color = DOT_COLORS[(i + offset) % len(DOT_COLORS)]
      # Set the LED color buffer value.
      ws.led_data_setitem(led_data, i, color)
    # Send the LED color data to the hardware.
    resp = ws.ws2811_render(leds)
    if resp != 0:
      raise RuntimeError('ws2811_render failed with code {0}'.format(resp))
    # Delay for a small period of time.
    time.sleep(0.25)
    # Increase offset to animate colors moving.  Will eventually overflow, which
    # is fine.
    offset += 1
finally:
  # Ensure ws2811_fini is called before the program quits.
  ws.ws2811_fini(leds)
  # Example of calling delete function to clean up structure memory.  Isn't
  # strictly necessary at the end of the program execution here, but is good practice.
  ws.delete_ws2811_t(leds)