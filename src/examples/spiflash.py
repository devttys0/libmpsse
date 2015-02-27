#!/usr/bin/env python

from mpsse import *
from time import sleep

class SPIFlash(object):

	WCMD = "\x02"		# Standard SPI flash write command (0x02)
	RCMD = "\x03"		# Standard SPI flash read command (0x03)
	WECMD = "\x06"		# Standard SPI flash write enable command (0x06)
	CECMD = "\xc7"		# Standard SPI flash chip erase command (0xC7)
	IDCMD = "\x9f"		# Standard SPI flash chip ID command (0x9F)

	ADDRESS_LENGTH = 3	# Normal SPI flash address length (24 bits, aka, 3 bytes)
	PP_PERIOD = .025	# Page program time, in seconds
	
	def __init__(self, speed=FIFTEEN_MHZ):

		# Sanity check on the specified clock speed
		if not speed:
			speed = FIFTEEN_MHZ
		
		self.flash = MPSSE(SPI0, speed, MSB)
		self.chip = self.flash.GetDescription()
		self.speed = self.flash.GetClock()
		self._init_gpio()

	def _init_gpio(self):
		# Set the GPIOL0 and GPIOL1 pins high for connection to SPI flash WP and HOLD pins.
		self.flash.PinHigh(GPIOL0)
		self.flash.PinHigh(GPIOL1)

	def _addr2str(self, address):
        	addr_str = ""

        	for i in range(0, self.ADDRESS_LENGTH):
        	        addr_str += chr((address >> (i*8)) & 0xFF)

        	return addr_str[::-1]

	def Read(self, count, address=0):
		data = ''

		self.flash.Start()
		self.flash.Write(self.RCMD + self._addr2str(address))
		data = self.flash.Read(count)
		self.flash.Stop()

		return data

	def Write(self, data, address=0, blocksize=256):
		count = 0

		while count < len(data):

			self.flash.Start()
        		self.flash.Write(self.WECMD)
        		self.flash.Stop()

			self.flash.Start()
			self.flash.Write(self.WCMD + self._addr2str(address) + data[address:address+blocksize])
			self.flash.Stop()

			sleep(self.PP_PERIOD)
			address += blocksize
			count += blocksize

	def Erase(self):
		self.flash.Start()
		self.flash.Write(self.WECMD)
		self.flash.Stop()

		self.flash.Start()
		self.flash.Write(self.CECMD)
		self.flash.Stop()

	def ChipID(self, idlen):
		self.flash.Start()
		self.flash.Write(self.IDCMD)
		chipid = self.flash.Read(idlen)
		self.flash.Stop()
		return chipid

	def Close(self):
		self.flash.Close()


if __name__ == "__main__":

	import sys
	from getopt import getopt as GetOpt, GetoptError

	def pin_mappings():
		print """
           Common Pin Mappings for 8-pin SPI Flash Chips       
--------------------------------------------------------------------
| Description | SPI Flash Pin | FTDI Pin | C232HM Cable Color Code |
--------------------------------------------------------------------
| CS          | 1             | ADBUS3   | Brown                   |
| MISO        | 2             | ADBUS2   | Green                   |
| WP          | 3             | ADBUS4   | Grey                    |
| GND         | 4             | N/A      | Black                   |
| MOSI        | 5             | ADBUS1   | Yellow                  |
| CLK         | 6             | ADBUS0   | Orange                  |
| HOLD        | 7             | ADBUS5   | Purple                  |
| Vcc         | 8             | N/A      | Red                     |
--------------------------------------------------------------------
"""
		sys.exit(0)

	def usage():
		print ""
		print "Usage: %s [OPTIONS]" % sys.argv[0]
		print ""
		print "\t-r, --read=<file>      Read data from the chip to file"
		print "\t-w, --write=<file>     Write data from file to the chip"
		print "\t-s, --size=<int>       Set the size of data to read/write"
		print "\t-b, --blocksize=<int>  Set the block/page - size of data to read/write"
		print "\t-a, --address=<int>    Set the starting address for the read/write operation [0]"
		print "\t-f, --frequency=<int>  Set the SPI clock frequency, in hertz [15,000,000]"
		print "\t-i, --id=<int>         Read the chip ID, requires Length of ID in bytes"
		print "\t-v, --verify           Verify data that has been read/written"
		print "\t-e, --erase            Erase the entire chip"
		print "\t-p, --pin-mappings     Display a table of SPI flash to FTDI pin mappings"
		print "\t-h, --help             Show help"
		print ""

		sys.exit(1)

	def main():
		fname = None
		freq = None
		action = None
		verify = False
		address = 0
		size = 0
		data = ""

		try:
			opts, args = GetOpt(sys.argv[1:], "f:s:b:i:a:r:w:epvh", ["frequency=", "size=", "blocksize=", "id_len=","address=", "read=", "write=", "erase", "verify", "pin-mappings", "help"])
		except GetoptError, e:
			print e
			usage()

		for opt, arg in opts:
			if opt in ('-f', '--frequency'):
				freq = int(arg)
			elif opt in ('-s', '--size'):
				size = int(arg)
			elif opt in ('-b', '--blocksize'):
				blocksize = int(arg)
			elif opt in ('-a', '--address'):
				address = int(arg)
			elif opt in ('-r', '--read'):
				action = "read"
				fname = arg
			elif opt in ('-w', '--write'):
				action = "write"
				fname = arg
			elif opt in ('-i', '--id'):
				action = "id"
				id_len = int(arg)
			elif opt in ('-e', '--erase'):
				action = "erase"
			elif opt in ('-v', '--verify'):
				verify = True
			elif opt in ('-h', '--help'):
				usage()
			elif opt in ('-p', '--pin-mappings'):
				pin_mappings()

		if action is None:
			print "Please specify an action!"
			usage()

		spi = SPIFlash(freq)
		print "%s initialized at %d hertz" % (spi.chip, spi.speed)

		if action == "read":
			if fname is None or not size:
				print "Please specify an output file and read size!"
				usage()
			
			sys.stdout.write("Reading %d bytes starting at address 0x%X..." % (size, address))
			sys.stdout.flush()
			data = spi.Read(size, address)
			open(fname, 'wb').write(data)
			print "saved to %s." % fname
		
		elif action == "write":
			if fname is None:
				print "Please specify an input file!"
				usage()

			data = open(fname, 'rb').read()
			if not size:
				size = len(data)
			if not blocksize:
				blocksize = 256
			sys.stdout.write("Writing %d bytes from %s to the chip starting at address 0x%X using a blocksize of %d ..." % (size, fname, address, blocksize))
			sys.stdout.flush()
			spi.Write(data[0:size], address)
			print "done."

		elif action == "id":
			if not id_len:
				id_len = 3
			for byte in spi.ChipID(id_len):
				print ("%.2X" % ord(byte)),
			print ""

		elif action == "erase":
			
			data = "\xFF" * size
			sys.stdout.write("Erasing entire chip...")
			sys.stdout.flush()
			spi.Erase()
			print "done."

		if verify and data:
			sys.stdout.write("Verifying...")
			sys.stdout.flush()

			vdata = spi.Read(size, address)
			if vdata == data:
				if data == ("\xFF" * size):
					print "chip is blank."
				elif data == ("\x00" * size):
					print "read all 0x00's."
				else:
					print "reads are identical, verification successful."
			else:
				print "reads are not identical, verification failed."

		spi.Close()

	main()
