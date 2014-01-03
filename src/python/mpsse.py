import os
import sys
import glob
import ctypes
import ctypes.util

MPSSE_OK   = 0
MPSSE_FAIL = -1
	
MSB = 0x00
LSB = 0x08

ACK  = 0
NACK = 1

SPI0 	= 1
SPI1 	= 2
SPI2 	= 3
SPI3 	= 4
I2C 	= 5
GPIO 	= 6
BITBANG = 7

GPIOL0 = 0
GPIOL1 = 1
GPIOL2 = 2
GPIOL3 = 3
GPIOH0 = 4
GPIOH1 = 5
GPIOH2 = 6
GPIOH3 = 7
GPIOH4 = 8
GPIOH5 = 9
GPIOH6 = 10
GPIOH7 = 11

IFACE_ANY = 0
IFACE_A   = 1
IFACE_B   = 2
IFACE_C   = 3
IFACE_D   = 4

ONE_HUNDRED_KHZ  = 100000
FOUR_HUNDRED_KHZ = 400000
ONE_MHZ          = 1000000
TWO_MHZ          = 2000000
FIVE_MHZ         = 5000000
SIX_MHZ          = 6000000
TEN_MHZ          = 10000000
TWELVE_MHZ       = 12000000
FIFTEEN_MHZ      = 15000000
THIRTY_MHZ       = 30000000
SIXTY_MHZ        = 60000000

class MPSSE(object):
	"""
	Python class wrapper for libmpsse.
	"""

        LIBRARY = b'mpsse'

	def __init__(self, mode=None, frequency=ONE_HUNDRED_KHZ, endianess=MSB):
		"""
		Class constructor.

		@mode      - The MPSSE mode to use, one of: SPI0, SPI1, SPI2, SPI3, I2C, GPIO, BITBANG, None.
                             If None, no attempt will be made to connect to the FTDI chip. Use this if you want to call the Open method manually.
		@frequency - The frequency to use for the specified serial protocol, in hertz (default: 100KHz).
		@endianess - The endianess of data transfers, one of: MSB, LSB (default: MSB).

		Returns None.
		"""
		self.context = None
		self.libmpsse = self._load_library(self.LIBRARY)
		if not self.libmpsse:
			raise Exception("Failed to load library 'lib$s'" % self.LIBRARY)

		self._ctypes_init()

                if mode is not None:
			self.context = self.libmpsse.MPSSE(mode, frequency, endianess)
			if not self.libmpsse.IsOpen(self.context):
				raise Exception("Failed to initialize MPSSE: " + self.ErrorString())

	def __enter__(self):
		return self

	def __exit__(self, t, v, traceback):
		if self.context:
			self.Close()

	def __del__(self):
		if self.context:
			self.Close()

	def _ctypes_init(self):
		self.libmpsse.MPSSE.restype = ctypes.c_void_p
		self.libmpsse.OpenIndex.restype = ctypes.c_void_p

		self.libmpsse.Read = ctypes.c_char_p
		self.libmpsse.Transfer = ctypes.c_char_p
		self.libmpsse.ErrorString.restype = ctypes.c_char_p
		self.libmpsse.GetDescription.restype = ctypes.c_char_p

	def _load_library(self, library):
		'''
		Locates and loads the specified library.

		@library - Library name (e.g., 'magic' for libmagic).
 
		Returns a handle to the library.
		'''
		lib_path = None
		system_paths = {
			'linux'  : ['/usr/local/lib/lib%s.so' % library],
			'linux2' : ['/usr/local/lib/lib%s.so' % library],
			'linux3' : ['/usr/local/lib/lib%s.so' % library],
			'darwin' : ['/opt/local/lib/lib%s.dylib' % library,
				    '/usr/local/lib/lib%s.dylib' % library,
				   ] + glob.glob('/usr/local/Cellar/lib%s/*/lib/lib%s.dylib' % (library, library)),

			'win32'  : ['%s.dll' % library]
		}

		try:
			lib = ctypes.cdll.LoadLibrary(ctypes.util.find_library(library))
			if lib:
				return lib
		except OSError:
			pass

		for path in system_paths[sys.platform]:
			if os.path.exists(path):
				lib_path = path
				break

		if not lib_path:
			raise Exception("Failed to locate library '%s'" % library)

		return ctypes.cdll.LoadLibrary(lib_path)

	def Open(self, vid, pid, mode, frequency=ONE_HUNDRED_KHZ, endianess=MSB, interface=IFACE_A, description=None, serial=None, index=0):
		"""
		Opens the specified FTDI device.
		Called internally by __init__ if the __init__ mode is not None.

		@vid         - FTDI USB vendor ID.
		@pid         - FTDI USB product ID.
		@mode        - The MPSSE mode to use, one of: SPI0, SPI1, SPI2, SPI3, I2C, GPIO, BITBANG.
		@frequency   - The frequency to use for the specified serial protocol, in hertz (default: 100KHz).
		@endianess   - The endianess of data transfers, one of: MSB, LSB (default: MSB).
		@interface   - The interface to use on the FTDI chip, one of: IFACE_A, IFACE_B, IFACE_C, IFACE_D, IFACE_ANY (default: IFACE_A).
		@description - FTDI device product description (default: None).
		@serial      - FTDI device serial number (default: None).
		@index       - Number of matching device to open if there are more than one, starts with zero (default: 0).

		Returns MPSSE_OK on success.
		Raises an exeption on failure.
		"""
		self.context = self.libmpsse.OpenIndex(vid, pid, mode, frequency, endianess, interface, description, serial, index)
		if self.context.open == 0:
			raise Exception("Failed to open MPSSE: " + self.ErrorString())
		return MPSSE_OK

	def Close(self):
		"""
		Closes the FTDI device connection, deinitializes libftdi, and frees the libmpsse context.

		Returns None.
		"""
		retval = self.libmpsse.Close(self.context)
		self.context = None
	
	def ErrorString(self):
		"""
		Returns the last libftdi error string.
		"""
		return self.libmpsse.ErrorString(self.context)

	def SetMode(self, mode, endianess):
		"""
		Sets the appropriate transmit and receive commands based on the requested mode and byte order.
		Called internally by __init__ and Open.

		@mode      - The MPSSE mode to use, one of: SPI0, SPI1, SPI2, SPI3, I2C, GPIO, BITBANG.
		@endianess - The endianess of data transfers, one of: MSB, LSB.
		
		Returns MPSSE_OK on success.
		Raises an exception on failure.
		"""
		if self.libmpsse.SetMode(self.context, mode, endianess) == MPSSE_FAIL:
			raise Exception("Failed to set mode: " + self.ErrorString())
		return MPSSE_OK

	def EnableBitmode(self, tf):
		"""
		Enables/disables bitwise data transfers.
		Called internally by ReadBits and WriteBites.

		@tf - Set to 1 to enable bitwise transfers, 0 to disable.

		Returns None.
		"""
		self.libmpsse.EnableBitmode(self.context, tf)

	def FlushAfterRead(self, tf):
		"""
		Enables / disables the explicit flushing of the recieve buffer after each read operation.

		@tf - Set to 1 to enable flushing, 0 to disable (disabled by default).

		Returns None.
		"""
		return self.libmpsse.FlushAfterRead(self.context, tf)

	def SetClock(self, frequency):
		"""
		Sets the appropriate divisor for the desired clock frequency.
		Called internally by __init__ and Open.

		@frequency - The desired clock frequency, in hertz.

		Returns MPSSE_OK on success.
		Raises an exception on failure.
		"""
		if self.libmpsse.SetClock(self.context, frequency) == MPSSE_FAIL:
			raise Exception("Failed to set clock:" + self.ErrorString())
		return MPSSE_OK

	def GetClock(self):
		"""
		Returns the currently configured clock rate, in hertz.
		"""
		return self.libmpsse.GetClock(self.context)

	def GetVid(self):
		"""
		Returns the vendor ID of the FTDI chip.
		"""
		return self.libmpsse.GetVid(self.context)

	def GetPid(self):
		"""
		Returns the product ID of the FTDI chip.
		"""
		return self.libmpsse.GetPid(self.context)

	def GetDescription(self):
		"""
		Returns the description of the FTDI chip, if any. 
		This will only be populated if __init__ was used to open the device.
		"""
		return self.libmpsse.GetDescription(self.context)

	def SetLoopback(self, enable):
		"""
		Enable / disable internal loopback. Loopback is disabled by default.

		@enable - Set to 1 to enable loopback, 0 to disable (disabled by default).

		Returns MPSSE_OK on success.
		Raises an exception on failure.
		"""
		if self.libmpsse.SetLoopback(self.context, enable) == MPSSE_FAIL:
			raise Exception("Failed to set loopback: " + self.ErrorString())
		return MPSSE_OK

	def SetCSIdle(self, idle):
		"""
		Sets the idle state of the chip select pin.

		@idle - Set to 1 to idle high, 0 to idle low (CS idles high by default).

		Returns None.
		"""
		self.libmpsse.SetCSIdle(self.context, idle)

	def Start(self):
		"""
		Send data start condition.

		Returns MPSSE_OK on success.
		Raises an exception on failure.
		"""
		if self.libmpsse.Start(self.context) == MPSSE_FAIL:
			raise Exception("Failed to send start signal: " + self.ErrorString())
		return MPSSE_OK

	def Stop(self):
		"""
		Send data stop condition.

		Returns MPSSE_OK on success.
		Raises an exception on failure.
		"""
		if self.libmpsse.Stop(self.context) == MPSSE_FAIL:
			raise Exception("Failed to send stop signal: " + self.ErrorString())
		return MPSSE_OK

	def Write(self, data):
		"""
		Writes bytes out via the selected serial protocol.
		
		@data - A string of bytes to be written.

		Returns MPSSE_OK on success.
		Raises an exception on failure.
		"""
		if self.libmpsse.Write(self.context, data) == MPSSE_FAIL:
			raise Exception("Failed to write data: " + self.ErrorString())
		return MPSSE_OK

	def Read(self, size):
		"""
		Reads bytes over the selected serial protocol.

		@size - Number of bytes to read.

		Returns a string of size bytes.
		"""
		return self.libmpsse.Read(self.context, size)

	def Transfer(self, data):
		"""
		Transfers data over the selected serial protocol.
		For use only in SPI0, SPI1, SPI2, SPI3 modes.

		@data - A string of bytes to be written.

		Returns a string of len(data) bytes.
		"""
		return self.libmpsse.Transfer(self.context, data)

	def SetAck(self, ack):
		"""
		Sets the transmitted ACK bit.
		For use only in I2C mode.

		@ack - One of: ACK, NACK.

		Returns None.
		"""
		self.libmpsse.SetAck(self.context, ack)

	def SendAcks(self):
		"""
		Causes all subsequent I2C read operations to respond with an acknowledgement.

		Returns None.
		"""
		self.libmpsse.SendAcks(self.context)

	def SendNacks(self):
		"""
		Causes all subsequent I2C read operations to respond with a no-acknowledgement.

		Returns None.
		"""
		return self.libmpsse.SendNacks(self.context)

	def GetAck(self):
		"""
		Returns the last received ACK bit.

		Returns one of: ACK, NACK.
		"""
		return self.libmpsse.GetAck(self.context)

	def PinHigh(self, pin):
		"""
		Sets the specified GPIO pin high.
		
		@pin - Pin number 0 - 11 in GPIO mode.
		       In all other modes, one of: GPIOL0, GPIOL1, GPIOL2, GPIOL3, GPIOH0, GPIOH1, GPIOH2, GPIOH3, GPIOH4, GPIOH5, GPIOH6, GPIOH7.

		Returns MPSSE_OK on success.
		Raises an exception on failure.
		"""
		if self.libmpsse.PinHigh(self.context, pin) == MPSSE_FAIL:
			raise Exception("Failed to set pin high: " + self.ErrorString())
		return MPSSE_OK

	def PinLow(self, pin):
		"""
		Sets the specified GPIO pin low.
		
		@pin - Pin number 0 - 11 in GPIO mode.
		       In all other modes, one of: GPIOL0, GPIOL1, GPIOL2, GPIOL3, GPIOH0, GPIOH1, GPIOH2, GPIOH3, GPIOH4, GPIOH5, GPIOH6, GPIOH7.
		
		Returns MPSSE_OK on success.
		Raises an exception on failure.
		"""
		if self.libmpsse.PinLow(self.context, pin) == MPSSE_FAIL:
			raise Exception("Failed to set pin low: " + self.ErrorString())
		return MPSSE_OK

	def SetDirection(self, direction):
		"""
		Sets the input/output direction of pins as determined by direction (1 = Output, 0 = Input). 
		For use in BITBANG mode only.

		@direction -  Byte indicating input/output direction of each bit (1 is output, 0 is input). 

		Returns MPSSE_OK on success.
		Raises an exception on failure.
		"""
		if self.libmpsse.SetDirection(self.context, direction) == MPSSE_FAIL:
			raise Exception("Failed to set direction: " + self.ErrorString())
		return MPSSE_OK

	def WriteBits(self, bits, n):
		"""
		Performs a bitwise write of up to 8 bits at a time.
		
		@bits - An integer of bits to be written.
		@n    - Transmit n number of least-significant bits.

		Returns MPSSE_OK on success.
		Raises an exception on failure.
		"""
		if self.libmpsse.WriteBits(self.context, bits, n) == MPSSE_FAIL:
			raise Exception("Failed to write bits: " +self.ErrorString())
		return MPSSE_OK

	def ReadBits(self, n):
		"""
		Performs a bitwise read of up to 8 bits at a time.

		@n - Number of bits to read.

		Returns an integer value with the read bits set.
		"""
		return ord(self.libmpsse.ReadBits(self.context, n))

	def WritePins(self, data):
		"""
		Writes a new state to the chip's pins.
		For use in BITBANG mode only.

		@data - An integer with the bits set to the desired pin states (1 = output, 0 = input).

		Returns MPSSE_OK on success.
		Raises an exception on failure.
		"""
		if self.libmpsse.WritePins(self.context, data) == MPSSE_FAIL:
			raise Exception("Failed to write pins: " + self.ErrorString())
		return MPSSE_OK

	def ReadPins(self):
		"""
		Reads the current state of the chip's pins.
		For use in BITBANG mode only.

		Returns an integer with the corresponding pin's bits set.
		"""
		return self.libmpsse.ReadPins(self.context)

	def PinState(self, pin, state=-1):
		"""
		Checks the current state of the pins.
		For use in BITBANG mode only.

		@pin   - The pin number whose state you want to check. 
		@state - The value returned by ReadPins. If not specified, ReadPins will be called automatically.

		Returns a 1 if the pin is high, 0 if the pin is low.
		"""
		return self.libmpsse.PinState(self.context, pin, state)

	def Tristate(self):
		"""
		Puts all I/O pins into a tristate mode (FT232H only).
		"""
		return self.libmpsse.Tristate(self.context)

	def Version(self):
		"""
		Returns the libmpsse version number.
		High nibble is major, low nibble is minor.
		"""
		return self.libmpsse.Version()
