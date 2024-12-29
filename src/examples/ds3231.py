#!/usr/bin/env python

from mpsse import *
from datetime import datetime


try:

    ds3231 = MPSSE(I2C, FOUR_HUNDRED_KHZ)

    print("%s initialized at %dHz (I2C) open: %d" % (ds3231.GetDescription(), ds3231.GetClock(), ds3231.context.open))

    try:

        now = datetime.now()

        b = bytes([0xD0, 0x00, 
                   ((now.second // 10) << 4) + (now.second % 10),
                   ((now.minute // 10) << 4) + (now.minute % 10),
                   ((now.hour   // 10) << 4) + (now.hour   % 10),
                   (now.isoweekday() % 7) + 1,
                   ((now.day    // 10) << 4) + (now.day    % 10),
                   ((now.month  // 10) << 4) + (now.month  % 10),
                   (((now.year % 100) // 10) << 4) + (now.year % 10),
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        print(b)

        ds3231.Start()
        ds3231.Write('\xD0\x00')

        if ds3231.GetAck() == ACK:
            ds3231.Start()
            ds3231.Write('\xD1')

            if ds3231.GetAck() == ACK:
                ds3231.SendAcks()
                data = ds3231.Read(18)
                ds3231.SendNacks()
                d = ds3231.Read(1)
                print(data, d)
            else:
                ds3231.Stop()
                raise Exception("Received read command NACK!")
            ds3231.Stop()
        else:
            raise Exception("Received write command NACK!")

    finally:
        ds3231.Close()

except Exception as e:
    print("MPSSE failure", e)

