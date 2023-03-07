import subprocess
import os
import shutil
import time
import serial
import base64

# stm_port = "COM7"
# baudrate = 115200
# parity = serial.PARITY_NONE
# stopbits = serial.STOPBITS_ONE
# bytesize = serial.EIGHTBITS

stm_port = "COM9"
baudrate = 115200
parity = serial.PARITY_NONE
stopbits = serial.STOPBITS_ONE
bytesize = serial.EIGHTBITS

# ser = serial.Serial(
#     port='COM9',
#     baudrate=115200,
#     parity=serial.PARITY_NONE,
#     stopbits=serial.STOPBITS_ONE,
#     bytesize=serial.EIGHTBITS)

ser = serial.Serial(
    port=stm_port,
    baudrate=baudrate,
    parity=parity,
    stopbits=stopbits,
    bytesize=bytesize)


# ser = serial.Serial(
#     port='COM9',
#     baudrate=115200,
#     parity=serial.PARITY_NONE,
#     stopbits=serial.STOPBITS_ONE,
#     bytesize=serial.EIGHTBITS)

while(1):
    line = ser.readline().decode()
    print(line)