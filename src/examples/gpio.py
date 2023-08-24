#!/usr/bin/env python

from mpsse import *
from time import sleep

# Open mpsse in GPIO mode

io = MPSSE()
io.Open(0x403,0x6010, GPIO, interface=IFACE_B)

pin = GPIOH7
# Toggle the first GPIO pin on/off 10 times
for i in range(0, 10):
	print "set direction BCBUS7,6 output, other input", io.SetDirectionHigh(0xC0)
	print "set direction BDBUS7,6 output, other input", io.SetDirection(0xC0)
	io.PinHigh(pin)
	print "GPIO State:", io.PinState(pin)
	sleep(0.2)

	io.PinLow(pin)
	print "GPIO State:", io.PinState(pin)
	sleep(0.2)

print bin(io.ReadPins())
print bin(io.ReadPinsHigh())

io.Close()
