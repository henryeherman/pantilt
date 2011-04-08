#! /usr/bin/env python
import os
import sys
import logging
import serial
from optparse import OptionParser


my_logger = logging.Logger('Pan-tilt ')
hand = logging.StreamHandler()
format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
hand.setFormatter(format)
my_logger.addHandler(hand)

usage = "usage: %prog -p PORT [options] a-axis b-axis"
parser = OptionParser(usage=usage, version="%prog 0.1")

parser.add_option("-p", "--port",
                    action="store", type="string", dest="port",
                    help="com port which is connected to the pan and tilt module, mandatory")
parser.add_option("-b","--baud", type="int", dest="baud", default=9600,
                    help="baud rate, default 9600")
parser.add_option("-v", "--verbose",
                    action="store_true", dest="verbose", default=False,
                    help="very noisy")
                    
parser.add_option("-s", "--speed", 
                    action="store", type="int", dest="speed",
                    help="Set speed of pan tilt")
                    
parser.add_option("-w", "--wait",
                    action="store_true", dest="wait",
                    help= "Return only motion complete", default=False)
    
(options, args) = parser.parse_args()


if len(args) != 2:
    parser.error("incorrect number of arguments, requires both a-axis and b-axis")
else:
    try:
        aaxis = int(args[0])
        baxis = int(args[1])
    except (NameError, ValueError):
        parser.error("a-axis and b-axis angle should be integer values")
    
bauds = [2400,4800,9600,19200,38400,57600,115200,31250]

speed = options.speed


try:
    baud = options.baud
    if not baud in bauds:
        raise serial.SerialException
except serial.SerialException:
    parser.error("invalid baud rate: %s" % baud)
    
try:
    port = options.port
    if port is None or not os.path.exists(port):
        raise serial.SerialException
except serial.SerialException:
    parser.error("serial port does not exist %s" % port)

try:
    con = serial.Serial(port=options.port,baudrate=baud,timeout=10)
except serial.SerialException, e:
    parser.error("Could not open serial port %s" % e)

if options.verbose:
    my_logger.setLevel(logging.DEBUG)
else:
    my_logger.setLevel(logging.INFO)

def sendA(val):
    s = "PP%d\r\n" % val
    con.write(s)
    my_logger.debug("SEND:%s" % s)
    readResp()
    
def sendB(val):
    s = "TP%d\r\n" % val
    con.write(s)
    my_logger.debug("SEND:%s" % s)
    readResp()
    
def sendSpeed(val):
    s = "TS%d\r\n" % speed 
    my_logger.debug("SEND:%s" % s)
    t = "PS%d\r\n" % speed
    my_logger.debug("SEND:%s" % t)
    con.write(s)
    readResp()
    con.write(t)
    readResp()

def wait():
    s = "A\r\n"
    my_logger.debug("SEND:%s" % s)
    con.write(s)
    
    resp = con.readline()
    while not "*" in resp:
        resp=con.readline()
    my_logger.debug("RESP:%s" % resp.strip())

def readResp():
    resp = con.readline()
    my_logger.debug("RESP:%s" % resp.strip())
    

def main():
    if not speed is None:
        sendSpeed(speed)
    sendA(aaxis)
    sendB(baxis)
    if options.wait:
        wait()
    
if __name__ == '__main__':
    pass
    main()


