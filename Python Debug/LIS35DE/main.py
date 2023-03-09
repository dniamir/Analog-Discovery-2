from ctypes import *
import sys
import time


import LIS35DE
import LIS35DEreg

import matplotlib as mpl
import matplotlib.pyplot as plt


def main():
    # (1) loading Waveforms SDK
    if sys.platform.startswith("win"):
        dwf = cdll.LoadLibrary("dwf.dll")
    elif sys.platform.startswith("darwin"):
        dwf = cdll.LoadLibrary("/Library/Frameworks/dwf.framework/dwf")
    else:
        dwf = cdll.LoadLibrary("libdwf.so")

    #declare ctype variables
    hdwf = c_int()

    # (2) open device
    print "Opening first device"
    dwf.FDwfDeviceOpen(c_int(-1), byref(hdwf))

    if hdwf.value == 0:
        print "failed to open device"
        szerr = create_string_buffer(512)
        dwf.FDwfGetLastErrorMsg(szerr)
        print szerr.value
        quit()

    # (3) enable 3.3V power supply
    # this need to be changed for use with AD or AD2
    print "Powering UP"
    # set voltage to 3.3 V (DD)
    dwf.FDwfAnalogIOChannelNodeSet(hdwf, c_int(0), c_int(1), c_double(3.3))
    # master enable
    dwf.FDwfAnalogIOEnableSet(hdwf, c_int(True))
    # wait for the sensor to power up
    time.sleep(0.1)

    # (4) configure I2C

    print "Configuring I2C..."

    iNak = c_int()

    # set I2C frequency and pins
    dwf.FDwfDigitalI2cRateSet(hdwf, c_double(1e5)) # 100kHz
    # pin numbers need to be checked for use with AD or AD2 device
    dwf.FDwfDigitalI2cSclSet(hdwf, c_int(32-24)) # SCL = DIO-32
    dwf.FDwfDigitalI2cSdaSet(hdwf, c_int(33-24)) # SDA = DIO-33

    # initialize I2C (check for correct pull-ups)
    dwf.FDwfDigitalI2cClear(hdwf, byref(iNak))
    if iNak.value == 0:
        print "I2C bus error. Check the pull-ups."
        quit()
    time.sleep(0.1)

    # (5) initialise sensor & display

    # initialize the sensor
    LIS35DE.initSensor(dwf, hdwf)

    # empty arrays for data & index
    timeX = []
    accelX = []
    accelY = []
    accelZ = []
    i = 0

    # initialize plot with two subplots, interactive drawing and no toolbar
    mpl.rcParams['toolbar'] = 'None'
    plt.ion()
    f, (ax1, ax2) = plt.subplots(2, sharex=False)
    # set window size
    size = 7
    f.set_size_inches(size / 2, size)

    # prepare four circles to form background for a "leveler"
    circle1 = plt.Circle((0, 0), 5, fill=False)
    circle2 = plt.Circle((0, 0), 16, fill=False)
    circle3 = plt.Circle((0, 0), 32, fill=False)
    circle4 = plt.Circle((0, 0), 64, fill=False)

    # x and y acceleration for a spirit level calibration
    xZero = 0
    yZero = 0

    # (6) read sensor data and update plots as long as the plot window is open

    while True:
        # read acceleration from a sensor and append it to arrays
        data = LIS35DE.readSensorXYZ(dwf, hdwf, LIS35DEreg.I2C_ADDR)
        accelX.append(data[0])
        accelY.append(data[1])
        accelZ.append(data[2])
        timeX.append(i)

        # remove oldest measurement, when more than 100 points
        if len(timeX) >= 100:
            timeX.pop(0)
            accelX.pop(0)
            accelY.pop(0)
            accelZ.pop(0)

        # remember first measurement result as a level reference
        if len(timeX) == 1:
            xZero = data[0]
            yZero = data[1]

        # count samples
        i += 1

        # clear first plot, and plot three axes as linear plot
        ax1.clear()
        ax1.plot(timeX, accelX)
        ax1.plot(timeX, accelY)
        ax1.plot(timeX, accelZ)

        # clear second plot and plot point at position according to the last X and Y acceleration
        # also taking into account "reference" measurement
        ax2.clear()
        ax2.plot(accelX[len(accelX)-1] - xZero, accelY[len(accelY)-1] - yZero, '*')
        # draw additional circles as a "guide"
        ax2.add_artist(circle1)
        ax2.add_artist(circle2)
        ax2.add_artist(circle3)
        ax2.add_artist(circle4)

        # set fixed plot scale
        ax2.set_xlim((-70, 70))
        ax2.set_ylim((-70, 70))

        # a little time to process plot
        plt.pause(0.0001)

        # if the plot is closed break the loop
        if not plt.get_fignums():
            print "CLOSED"
            break

    # (7) disable all devices
    # disable power supply
    dwf.FDwfAnalogIOEnableSet(hdwf, c_int(False))

    # disconnect all connected devices
    dwf.FDwfDeviceCloseAll()

main()
print "END"