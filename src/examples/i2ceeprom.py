#!/usr/bin/env python

import argparse, os, struct, sys, time

# Check if were running on Python2.7
if (sys.version[0:3] != "2.7"):
	print("This script is meant to be run on python2.7.x ! Exiting")
	exit(1)

found=False
# Check if MPSSE lib can be found in pythons path first
for path in range(len(sys.path)):
	if sys.path[path] != '' and os.path.exists(sys.path[path]) and os.path.isdir(sys.path[path]):
		mpssename = "%s/mpsse.pyc" % sys.path[path]
		if os.path.exists(mpssename) and os.path.isfile(mpssename):
			found = True
# Try to locate mpsse in typical default dirs, if not found.
if found != True :
	custom_paths = ['/usr/lib/python2.7/site-packages', '/usr/local/lib/python2.7/site-packages', '/usr/lib64/python2.7/site-packages', '/usr/local/lib64/python2.7/site-packages']
	for path in range(len(custom_paths)):
		if custom_path[path] != '' and os.path.exists(custom_path[path]) and os.path.isdir(custom_path[path]):
			mpssename = "%s/mpsse.pyc" % custom_path[path]
			if os.path.exists(mpssename) and os.path.isfile(mpssename):
				sys.path.append(custom_path[path])
				found = True
if found != True:
	print("MPSSE Library could not be found. Exiting")
	exit(1)

from fish import ProgressFish
from mpsse import *

parser = argparse.ArgumentParser(prog="i2c-eeprom", description="i2c-eeprom utility based on python-mpsse")
parser.add_argument("-a", "--addressbits", help="addresstype (8 / 16), default to 8bits for <=16kbit size, 16bits for eeprom > 16kbit", type=int, required=0, metavar="<8 / 16>", action="store", dest="addressbits")
parser.add_argument("-s", "--size", help="eeprom size in bytes", type=int, metavar="<eeprom size>", action="store", dest="eeprom_size", required=1)
parser.add_argument("-p", "--pagesize", help="count of bytes per page", type=int, metavar="<pagesize>", action="store", dest="page_size", required=1)
parser.add_argument("-e", "--erase", help="erase eeprom (to FFh Values)", action="store_true", dest="mode_erase")
parser.add_argument("-r", "--read", help="read eeprom to <filename>", type=str, metavar="<filename>", action="store", dest="readfilename")
parser.add_argument("-w", "--write", help="write <filename> to eeprom", type=str, metavar="<filename>", action="store", dest="writefilename")
parser.add_argument("-d", "--eeprom-id", help="3bit device-address of eeprom, hardwired, default = 0", metavar="<0-7>", type=int, default=0, action="store", dest="devaddress")
parser.add_argument("-c", "--count", help="number of bytes to read in read-mode. default = full eeprom-size", metavar="<0-524288>", type=long, action="store", dest="bytecount")
parser.add_argument("-o", "--offset", help="bytenumber to start reading at. default = 0", metavar="<0-524287>", type=long, default=0, action="store", dest="offset")
parser.add_argument("-S", "--speed", help="I2C bus frequency. default = 100000KHz", metavar="<ONE_HUNDRED_KHZ / FOUR_HUNDRED_KHZ/ ONE_MHZ>", type=str, action="store", dest="speed")
parser.add_argument("-i", "--devicecode", help="Vendor_ID:Product_ID default = 0403:6010", metavar="<vendor_id:product_id>", type=str, default="0403:6010", action="store", dest="devid")
parser.add_argument("-I", "--interface", help="Interface to use (if FTDI-device has multiple UART-interfaces). default = A", metavar="<A/B/C/D>", type=str, default="A", action="store", dest="iface")
parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")

args = parser.parse_args()

if (args.devid != "0403:6010"):
	vendor_id = int(args.devid.split(':')[0], 16)
	product_id = int(args.devid.split(':')[1], 16)
else:
	vendor_id = int("0403", 16)
	product_id = int("6010", 16)

if (args.iface == "A"):
	IFACE=IFACE_A
elif (args.iface == "B"):
        IFACE=IFACE_B
elif (args.iface == "C"):
        IFACE=IFACE_C
elif (args.iface == "D"):
        IFACE=IFACE_D
else:
	parser.print_help()
	print("This script supports interfaces A to D only !")
	sys.exit(1)

if ((args.mode_erase == False) and (args.readfilename == None) and (args.writefilename == None)):
	parser.print_help()
	print("\nYou need to specify either erase or read/write - mode!")
	sys.exit(1)

if (((args.mode_erase == True) and (args.readfilename != None)) or ((args.mode_erase == True) and (args.writefilename != None)) or ((args.writefilename != None) and (args.readfilename != None))):
	parser.print_help()
	print ("\nYou can only read OR write OR erase at a time ;) !")
	sys.exit(1)

if (args.addressbits != None):
	addressbits = args.addressbits
elif ((args.addressbits == None) and (args.eeprom_size <= 2048)):
	addressbits = 8
else:
	addressbits = 16

FLASHSIZE = args.eeprom_size
PAGESIZE = args.page_size
PAGECOUNT = FLASHSIZE / PAGESIZE
MODE = None
DATA = ''

if (args.speed != None):
	if (args.speed == "ONE_HUNDRED_KHZ"):
		SPEED = ONE_HUNDRED_KHZ
	elif (args.speed == "FOUR_HUNDRED_KHZ"):
		SPEED = FOUR_HUNDRED_KHZ
	elif (args.speed == "ONE_MHZ"):
		SPEED = ONE_MHZ
	else:
		parser.print_help()
		print('Speed must be set to "ONE_HUNDRED_KHZ" or "FOUR_HUNDRED_KHZ" or "ONE_MHZ" (Default : ONE_HUNDRED_KHZ)!')
		sys.exit(1)
else:
	SPEED=ONE_HUNDRED_KHZ

if (args.devaddress <= 7):
	DEVADDR = args.devaddress
else:
	parser.print_help()
	print("\nOnly 8 chained i2c-eeprom-devices on one i2c-bus possible !")

if (args.mode_erase == True):
	HEXDATA = chr(255)*PAGESIZE
	MODE = "erase"

if (args.writefilename != None):
	HEXDATA = open(args.writefilename, 'rb').read()
	PAGECOUNT = len(HEXDATA) / PAGESIZE
	MODE = "write"

if (args.readfilename != None):
	readfilename = args.readfilename
	MODE = "read"

if (args.bytecount != None):
	bytecount = args.bytecount
else:
	bytecount = FLASHSIZE

fish= ProgressFish(total=PAGECOUNT)

try:
	if (MODE == "read"):
		eeprom = MPSSE(None)
		eeprom.Open(vendor_id, product_id, I2C, SPEED, MSB, IFACE)
                print "FTDI I2C initialized at %dHz" % (eeprom.GetClock())
		addressbyte = args.offset 	
		addressbyte = 0
		if (addressbits == 8):
			addr = divmod(addressbyte, 256)
			byteaddress = struct.pack('BB', (160 + ((addr[0] + DEVADDR) * 2)), addr[1])
		else:
			addr = divmod(addressbyte, 65536)
			byteaddress = struct.pack('B', (160 + ((addr[0] + DEVADDR) * 2))) + struct.pack('>H', addr[1])
		eeprom.Start()
		if (args.verbose == True):
			print("Writing byteaddress %s" % byteaddress.encode('hex'))
		eeprom.Write(byteaddress)
		if eeprom.GetAck() != ACK:
                                print "Error writing byteaddress !"
		else:
			if (args.verbose == True):
				print("Eeprom acknowledged byteaddress.")
			eeprom.Start()
	                eeprom.Write(struct.pack('B', (161 + (DEVADDR * 2))))
        	        if eeprom.GetAck() != ACK:
                	        print "Error writing readcommand!"
			else:
				if (args.verbose == True):
	                                print("Eeprom acknowledged readcommand, start reading %d bytes from eeprom." % bytecount)
				DATA = eeprom.Read(bytecount)
				eeprom.SendNacks()
		eeprom.Stop()
		eeprom.Close()
		open(readfilename, "wb").write(DATA)
	        print "Dumped %d bytes to %s" % (len(DATA), readfilename)
	else:
		eeprom = MPSSE(None)
		eeprom.Open(vendor_id, product_id, I2C, SPEED, MSB, IFACE)
		print "FTDI I2C initialized at %dHz" % (eeprom.GetClock())
		for PAGENUM in range(PAGECOUNT):
			BYTENUM = PAGENUM * PAGESIZE
			if (addressbits == 8):
				address = divmod(BYTENUM, 256)
				pageaddress = struct.pack('BB', (160 + ((DEVADDR + address[0]) * 2)), address[1])
			else:
				address = divmod(BYTENUM, 65536)
				pageaddress = struct.pack('B', (160 + ((DEVADDR + address[0]) * 2))) + struct.pack('>H', address[1])
			eeprom.Start()
			eeprom.Write(pageaddress)
			if eeprom.GetAck() != ACK:
				print "Error writing pageaddress for page %d" % PAGENUM
	                        break
			else:
				if (MODE == "write"):
					data = HEXDATA[BYTENUM:(BYTENUM+PAGESIZE)]
					if (args.verbose == True):
	                               		print("Eeprom acknowledged pageaddress %s, start writing data to eeprom.\nData = \n%s" % ('\\x' + '\\x'.join(x.encode('HEX') for x in pageaddress), data.encode('hex')))
					eeprom.Write(data)
					if eeprom.GetAck() != ACK:
        	       		       		print "Error writing page %d" % PAGENUM
	        	        		break
					else:
						if (args.verbose == True):
        	                                        print("Eeprom acknowledged pagewrite for page %d" % PAGENUM)
				elif (MODE == "erase"):
					if (args.verbose == True):
                                                print("Eeprom acknowledged pageaddress %s, start erasing page %d with \\xFF * %d" % ('\\x' + '\\x'.join(x.encode('HEX') for x in pageaddress), PAGENUM, PAGESIZE))
					eeprom.Write(HEXDATA)
					if eeprom.GetAck() != ACK:
        	                                print "Error erasing page %d" % PAGENUM
                	                        break
					else:
						if (args.verbose == True):
	                                                print("Eeprom acknowledged erase of page %d" % PAGENUM)
			eeprom.Stop()
			time.sleep(1/1000.0 * 5)
			if (args.verbose == False):
				fish.animate(amount=(PAGENUM + 1))
		if (MODE == "write"):
			print("Finished writing %s to eeprom !" % args.writefilename)
                elif (MODE == "erase"):
			print("Erase of flash finished !")
		eeprom.Close()

except Exception, e:
	print "MPSSE failure:", e
sys.exit(0)
