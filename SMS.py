#!/usr/bin/python

import RPi.GPIO as GPIO
import serial
import time

ser = serial.Serial("/dev/ttyS0",115200)
ser.flushInput()

power_key = 6

def send_at(command,back,timeout):
	rec_buff = ''
	ser.write((command+'\r\n').encode())
	time.sleep(timeout)
	if ser.inWaiting():
		time.sleep(0.01 )
		rec_buff = ser.read(ser.inWaiting())
	if back not in rec_buff.decode():
		return [ 0, rec_buff.decode() ]
	else:
		return [ 1, rec_buff.decode() ]

def setSMSMode():
	print('Setting SMS mode...')
	send_at('AT+CMGF=1','OK',1)
	send_at('AT+CPMS=\"SM\",\"SM\",\"SM\"', 'OK', 1)

def ReceiveShortMessage():
	print('Checking sms')
	for currentSMS in range( 0, 26 ):
		answer = send_at('AT+CMGRD=' + str( currentSMS ),'+CMGRD',2)
		if answer[ 0 ] == 1:
			if 'OK' in answer[ 1 ]:
				answearClear = str( answer[ 1 ] ).strip()

				answearSplit = answearClear.splitlines()

				linesList = []

				for currentLine in answearSplit:
					lineClear = currentLine.strip()

					if len( lineClear ):
						linesList.append( lineClear )

				foundLineRec = 0

				for index, currentLine in enumerate(linesList):
					if 'REC UNREAD' in currentLine:
						foundLineRec = index + 1

						break

				smsCodeLines = linesList[ foundLineRec: len( linesList ) - 1 ]

				smsCode = ''.join( smsCodeLines )

				print( 'SMS Code' + smsCode )

def power_on(power_key):
	print('SIM7600X is starting:')
	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False)
	GPIO.setup(power_key,GPIO.OUT)
	time.sleep(0.1)
	GPIO.output(power_key,GPIO.HIGH)
	time.sleep(2)
	GPIO.output(power_key,GPIO.LOW)
	time.sleep(20)
	ser.flushInput()
	print('SIM7600X is ready')

def power_down(power_key):
	print('SIM7600X is loging off:')
	GPIO.output(power_key,GPIO.HIGH)
	time.sleep(3)
	GPIO.output(power_key,GPIO.LOW)
	time.sleep(18)
	print('Good bye')

try:
	power_on(power_key)
	print('Receive Short Message Test:\n')

	setSMSMode()
	
	while( True ):
		ReceiveShortMessage()

		time.sleep(20)

	power_down(power_key)
except Exception as error:
	print( error )
	if ser != None:
		ser.close()
	GPIO.cleanup()