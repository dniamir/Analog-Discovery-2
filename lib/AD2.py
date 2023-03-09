"""Class for Digilent Analog Discovery 2"""
from ctypes import *
import sys

iNak = c_int()
rgRX = (c_ubyte * 6)()

hdwf = c_int()

# if sys.platform.startswith("win"):
#     dwf = cdll.LoadLibrary("dwf.dll")
# elif sys.platform.startswith("darwin"):
#     dwf = cdll.LoadLibrary("/Library/Frameworks/dwf.framework/dwf")
# else:
#     dwf = cdll.LoadLibrary("libdwf.so")

dwf = cdll.LoadLibrary("dwf.dll")

class AD2_I2C:
	"""Class for using I2C on the Digilent Analog Discovery 2
	
	Device is capable of supplying voltages, operating as a I2C/SPI interface,
	acting as a voltage supply, acting as an oscilloscope, ect...
	"""
	
	def __init__(self, voltage=None, pin=0):
		"""Initialize device"""
		self.dwf = dwf
		self.dwf.FDwfDeviceOpen(c_int(-1), byref(hdwf))
		
		if voltage is not None:
			self.SetAnalogOut(voltage, pin)
	
	def SetAnalogOut(self, voltage, pin=0):
		"""Set analog voltage output
		
		Inputs:
			voltage: Float. Votlage to set [volts]
			pin: int. Int. Pin #. Either 0 (positive) or 1 (negative)
		"""
		self.dwf.FDwfAnalogIOChannelNodeSet(hdwf, c_int(pin), c_int(0), c_double(
			True))  # enable positive supply
		self.dwf.FDwfAnalogIOChannelNodeSet(hdwf, c_int(pin), c_int(1),
		                                    c_double(voltage))
		self.dwf.FDwfAnalogIOEnableSet(hdwf, c_int(True))  # master enable
	
	def SetupI2C(self, scl_pin, sda_pin):
		"""Setup I2C communication
		
		Inputs:
			scl_pin: Int. Pin # for SCL
			sda_pin: Int. Pin # for SDA
		"""
		# set I2C frequency and pins
		self.dwf.FDwfDigitalI2cRateSet(hdwf, c_double(1e5))  # 100kHz
		
		# pin numbers need to be checked for use with AD or AD2 device
		self.dwf.FDwfDigitalI2cSclSet(hdwf, c_int(scl_pin - 24))
		self.dwf.FDwfDigitalI2cSdaSet(hdwf, c_int(sda_pin - 24))
		
		# initialize I2C (check for correct pull-ups)
		self.dwf.FDwfDigitalI2cClear(hdwf, byref(iNak))
		if iNak.value == 0:
			print('I2C bus error. Check the pull-ups')
		time.sleep(0.1)
	
	def ReadRegister(self, address, register, bytes_to_read=1):
		"""Read I2C register

		Inputs:
			address: Value of device's I2C address
			register: Value of register address to read
			bytes_to_read: int. Number of bytes to read in a row
		"""
		rgRX = (c_ubyte * bytes_to_read)()
		self.dwf.FDwfDigitalI2cWriteRead(hdwf, c_int(address << 1),
		                                 (c_ubyte * 1)(register),
                                   c_int(1),
                                   rgRX,
                                   c_int(bytes_to_read),
                                   byref(iNak))
		return rgRX[:]
	
	def WriteRegister(self, address, register, value):
		"""Write I2C register

		Inputs:
			address: Value of device's I2C address
			register: Value of register address to write to
			value: Value to write to the register
		"""
		self.dwf.FDwfDigitalI2cWrite(hdwf,
                               c_int(address << 1),
		                             (c_ubyte * 2)(register, value),
                               c_int(2),
                               byref(iNak))

	def WriteRegister16(self, address, register, value):
		"""Write I2C register

		Inputs:
			address: Value of device's I2C address
			register: Value of register address to write to
			value: Value to write to the register
		"""
		byte_msb = value >> 8
		byte_lsb = value & 0b11111111
		self.dwf.FDwfDigitalI2cWrite(hdwf,
                               c_int(address << 1),
		                             (c_ubyte * 3)(register, byte_lsb, byte_msb),
                               c_int(3),
                               byref(iNak))
	
	def Close(self):
		# disable power supply
		self.dwf.FDwfAnalogIOEnableSet(hdwf, c_int(False))
		
		# disconnect all connected devices
		self.dwf.FDwfDeviceCloseAll()
		