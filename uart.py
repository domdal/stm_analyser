import subprocess
import os
import shutil
import time
import serial
import base64

ser = serial.Serial(
    port='COM7',
    baudrate=209700,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.SEVENBITS)

while(1):
    line = ser.readline().decode()
    print(line)