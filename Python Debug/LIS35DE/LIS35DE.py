from ctypes import *
import LIS35DEreg

# basic LIS35DE communication routines, based on:
# https://github.com/krzychb/esp-lis35de/blob/master/components/lis35de/lis35de.c
iNak = c_int()
rgRX = (c_ubyte*6)()

def writeSensor(dwf, hdwf, address, register, value):
    dwf.FDwfDigitalI2cWrite(hdwf, c_int(address << 1), (c_ubyte*2)(register, value), c_int(2), byref(iNak))


def readSensor(dwf, hdwf, address, register):
    dwf.FDwfDigitalI2cWriteRead(hdwf, c_int(address << 1), (c_ubyte*1)(register), c_int(1), rgRX, c_int(1), byref(iNak))
    return rgRX[0]


def readSensorXYZ(dwf, hdwf, address):
    dwf.FDwfDigitalI2cWriteRead(hdwf, c_int(address << 1), (c_ubyte*1)(LIS35DEreg.REG_OUTX | LIS35DEreg.READ_INC),
                                c_int(1), rgRX, c_int(5), byref(iNak))
    return (c_byte*3)(twos_comp(rgRX[0],8), twos_comp(rgRX[2],8), twos_comp(rgRX[4],8))


def initSensor(dwf, hdwf):
    #reset sensor
    writeSensor(dwf, hdwf, LIS35DEreg.I2C_ADDR, LIS35DEreg.REG_CR2, LIS35DEreg.REG_CR2_BOOT)
    #enable sensor
    writeSensor(dwf, hdwf, LIS35DEreg.I2C_ADDR, LIS35DEreg.REG_CR1, LIS35DEreg.REG_CR1_ACTIVE |
                LIS35DEreg.REG_CR1_XEN | LIS35DEreg.REG_CR1_YEN | LIS35DEreg.REG_CR1_ZEN)

# two's complement to signed integer conversion, according to:
# https://stackoverflow.com/questions/1604464/twos-complement-in-python
def twos_comp(val, bits):
    """compute the 2's complement of int value val"""
    if (val & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
        val = val - (1 << bits)        # compute negative value
    return val                         # return positive value as is