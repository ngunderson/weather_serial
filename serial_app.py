#################################################################
# This file is a tester to attempt to get the data from the arduino
# to the server, but I really don't know what I'm doing here yet
#################################################################
from weather_server.db.model import db, Weather, Device
from weather_server.server import create_app

create_app().app_context().push()

import sys
import glob
import serial
import serial.tools.list_ports
import io
import json
from datetime import datetime, timezone

noValidPortSelected = True
ser = None

class NoDeviceException(Exception):
    pass

def serial_ports():
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux'):
        ports = glob.glob('/dev/tty[A-Za-z]*')
    else:
        raise EnvironmentError('Unsupported platform')
    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except  serial.SerialException:
            pass
    return result

'''
set a port to one selected port
'''
def setup(noValidPortSelected):
    while(noValidPortSelected):
        input('ensure the host node is not plugged in yet and press enter.')
        myPorts1 = serial_ports()
        input('plug the host node in (and do not remove any other USB connections) and press enter.')
        myPorts2 = serial_ports()
        for x in myPorts2:
            if x not in myPorts1:
                arduino = x
        try:
            global ser
            ser = serial.Serial(port = arduino, baudrate = 9600,
            parity = serial.PARITY_NONE, stopbits = serial.STOPBITS_ONE,
            bytesize = serial.EIGHTBITS, timeout = 5)
            print(ser.port)
            noValidPortSelected = False
        except:
            print("Connection failed, read all instructions carefully")

'''
read from arduino, checks if there is anything in the buffer
'''
def readFromArduino():
    line = ""
    while(True):
        global ser
        c = ser.read()
        a = c.decode('utf-8')
        if a not in {' ', '\t', '\n', '\r'}:
            line += a
        if (a == '\n' or a == '\r') and line:
            try:
                message = json.loads(line)
                devId = int(message['id'])
                dev = Device.query.get(devId)
                if dev:
                    print("dev found")
                else:
                    raise NoDeviceException

                weather = Weather(
                    device_id=devId,
                    time=datetime.utcnow(),
                    temp=float(message["temp"])
                )
                db.session.add(weather)
                db.session.commit()
                print("weather added to the db")
                response = str(devId) + ":ACK"
                ser.write(response.encode('utf-8'))

            except (ValueError, KeyError, NoDeviceException) as e:
                print("exception is")
                print(e)
                print("device ignored")

            # clear line
            line = ""

setup(noValidPortSelected)
readFromArduino()
