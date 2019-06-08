import sys
import time
import os.path
sys.path.append('/home/pi/Dexter/GrovePi/Software/Python')
import grovepi
import grove_rgb_lcd as lcd
import smtplib
import json
import requests
import _thread
from twilio.rest import Client

PORT_BUTTON = 3
PORT_BUZZER = 4
PORT_ROTARY = 2
PORT_RANGE = 7
PORT_RED_LED = 5
PORT_GREEN_LED = 6 

account_ssid = 'AC32c39154f82d33309f2001ef3614fd57'
auth_token = ''

ADDRESS = ''

grovepi.pinMode(PORT_BUZZER, "OUTPUT")
grovepi.pinMode(PORT_BUTTON, "INPUT")
grovepi.pinMode(PORT_ROTARY,"INPUT") 
grovepi.pinMode(PORT_RED_LED, "OUTPUT")
grovepi.pinMode(PORT_GREEN_LED, "OUTPUT")
lcd.setRGB(255,255,255)

def get_value(max=300):
	sensor_value = grovepi.analogRead(PORT_ROTARY)
	slope = max/1023
	key_f = round(sensor_value*slope)
	return int(key_f)

def validateInput(type, userInput):
	if (type == 1):
		try:
			if(int(userInput)):
				if(int(userInput) <= 300 and int(userInput) >= 0):
					return True
		except: 
			return False
	elif(type == 2):
		try:
			if(int(userInput)):
				if(int(userInput) <= 513 and int(userInput) >= 0):
					return True
		except: 
			return False
	elif(type == 3):
		if("@gmail.com" in userInput):
			return True
	return False		

def send_config(email, number):
	headers = {
		'Content-Type': 'application/json',
		'Authorization': None   # not using HTTP secure
	}
	payload = {
		'email': email,
		'number' : number
	}
	requests.post("http://{}/configure".format(ADDRESS), headers=headers, data=json.dumps(payload))
def send_alarm():
	headers = {
		'Content-Type': 'application/json',
		'Authorization': None   # not using HTTP secure
	}
	payload = {
		'time' : str(time.time())
	}
	requests.post("http://{}/alarm_triggered".format(ADDRESS),headers=headers,data=json.dumps(payload))
def send_disarm():
	headers = {
		'Content-Type': 'application/json',
		'Authorization': None   # not using HTTP secure
	}
	payload = {
		'time' : str(time.time())
	}
	requests.post("http://{}/disarm".format(ADDRESS), headers=headers, data=json.dumps(payload))
def configureDevice(keys=["0","0","0"], distance="0", number="", email="", option=0):
	print(keys, distance, number, email)
	isConfigured = False
	configState = 1
	currentKey = 1
	#have user create combination lock
	while(not isConfigured):
		if(configState == 1):
			#Change key one by one by pressing button
			if(option == 0 or option == 2):
				lcd.setText_norefresh("Set Combination:\n{:>3} {:>3} {:>3}".format(keys[0], keys[1], keys[2]))
				temp = input("Enter a key value between 0 and 300: ")
				while(not validateInput(1, temp) and currentKey <= 4):
					print("Invalid input. Keys must be between 0 and 300.")
					temp = input("Enter a key value between 0 and 300: ")
				if(currentKey == 1):
					keys[0] = temp
				elif(currentKey == 2):
					keys[1] = temp
				elif(currentKey == 3):
					keys[2] = temp
			currentKey += 1
			if(currentKey > 3 or option != 0 and option != 2):
				configState += 1
				lcd.setText("")

		elif(configState == 2):
			#set distance the device will be away from the door frame
			if(option == 0 or option == 3):
				lcd.setText_norefresh("Set Distance:\n{}".format(distance))
				distance = input("Enter a distance value between 0 and 513: ")
				while (not validateInput(2, distance)):
					print("Invalid input. Distance must be between 0 and 513.")
					distance = input("Enter a distance value between 0 and 513: ")
			configState += 1
			lcd.setText("")
		elif(configState == 3):
			if(option == 0 or option == 4):
				lcd.setText_norefresh("Set Phone:\n{}".format(number))
				number = input("Enter a phone number to send sms alerts to: ")
			configState += 1
			lcd.setText("")
		else:
			if(option == 0 or option == 5):
				lcd.setText_norefresh("Set Email:\n{}".format(email))
				email = input("Enter a gmail address to send smtp alerts to: ")
				while (not validateInput(3, email)):
					print("Please enter a gmail address.")
					email = input("Enter a gmail address to send smtp alerts to: ")
			lcd.setText("")
			isConfigured = True
		grovepi.digitalWrite(PORT_BUZZER,1)
		time.sleep(0.2)
		grovepi.digitalWrite(PORT_BUZZER,0)
	#write to the config file and clear display
	lcd.setText("")
	configFile = open("security_config.txt", "w+")
	for key in keys:
		configFile.write(str(key) +"\n")
	configFile.write(str(distance.rstrip()) + "\n")
	configFile.write(str(number.rstrip()) + "\n")
	configFile.write(str(email.rstrip()) + "\n")
	send_config(email.rstrip(), number.rstrip())
	configFile.close()
def validateCombo(userKeys, keys):
	for i in range(3):
		if(userKeys[i] != keys[i]):
			return False
	return True

if __name__ == '__main__':
	#device info
	deviceState = 1
	count = 0
	index = 0
	option = 1
	#configuration setup
	if(not os.path.isfile("security_config.txt")):
		configureDevice()
		deviceState = 3
	#import user settings
	configFile = open("security_config.txt", "r+")
	lines = configFile.readlines()
	combo = [int(lines[0]), int(lines[1]), int(lines[2])]
	distance = int(lines[3])
	number = lines[4]
	email = lines[5]
	#main loop logic
	keys = ["_","_","_"]
	currentKey = 1
	alarm_sent = False
	disarm_sent = False
	while True:
		print(deviceState)
		if(deviceState == 1):
			lcd.setRGB(0,0,0)
			grovepi.digitalWrite(PORT_GREEN_LED,1)
			measured_distance = grovepi.ultrasonicRead(PORT_RANGE)
			if(measured_distance < distance -5 or measured_distance > distance + 5):
				deviceState = 2
				lcd.setText("")
				start = time.time()
		elif(deviceState == 2):
			lcd.setRGB(255,255,255)
			timeDiff = int(time.time()) - int(start)
			lcd.setText_norefresh("{:>2} S UNTIL ALARM\n{:>3} {:>3} {:>3}".format(60-timeDiff, keys[0], keys[1], keys[2]))
			if(not alarm_sent):
				_thread.start_new_thread(send_alarm,())
				alarm_sent = True
			if(currentKey == 1):
				keys[0] = get_value()
			elif(currentKey == 2):
				keys[1] = get_value()
			elif(currentKey == 3):
				keys[2] = get_value()
			else:
				if(validateCombo(keys, combo)):
					deviceState = 3
					index = 0
					lcd.setText("")
				else:
					currentKey = 1
					lcd.setRGB(255,0,0)
			if(grovepi.digitalRead(PORT_BUTTON)):
				currentKey += 1
			grovepi.digitalWrite(PORT_BUZZER,1)
			grovepi.digitalWrite(PORT_RED_LED,1)
			if(timeDiff  >= 60):
				lcd.setRGB(255,0,0)
				client = Client(account_ssid, auth_token)
				message = client.messages.create(from_ = '+14245810952',body = 'Your alarm has been triggered!', to = number)
				s = smtplib.SMTP('smtp.gmail.com', 587)
				s.starttls()
				s.login("rpimotionalarmdevice", "")
				message = "Your alarm has been triggered!"
				s.sendmail("rpimotionalarmdevice", email, message)
				s.quit()
				alarm_sent = False
				deviceState = 4
				keys = ["_","_","_"]
				lcd.setText("")
		elif(deviceState == 3):
			if(not disarm_sent):
				_thread.start_new_thread(send_disarm,())
				disarm_sent = True
			msg_option = ""
			option = get_value(5)
			if(option <= 1):
				msg_option = "ARM                "
			elif(option == 2):
				msg_option = "CHANGE COMBO                "
			elif(option == 3):
				msg_option = "CHANGE DISTANCE                "
			elif(option == 4):
				msg_option = "CHANGE NUMBER                "
			elif(option == 5):
				msg_option = "CHANGE EMAIL                "
			msg = "PRESS BTN TO "+ msg_option
			end = min(index+15, len(msg))
			lcd.setText_norefresh("DEVICE DISARMED\n"+msg[index:end])
			if(grovepi.digitalRead(PORT_BUTTON) and option <= 1):
				deviceState = 1
				keys = ["_","_","_"]
				lcd.setText("")
				disarm_sent = False
			elif(grovepi.digitalRead(PORT_BUTTON) and option > 1):
				configureDevice(combo, distance, number, email, option)
				configFile = open("security_config.txt", "r+")
				lines = configFile.readlines()
				combo = [int(lines[0]), int(lines[1]), int(lines[2])]
				distance = int(lines[3])
				number = lines[4]
				email = lines[5]
			index += 1
			if(index > len(msg)-16):
				index = 0
		elif(deviceState == 4):
			msg = "NOTIFIED OWNER, ENTER COMBO TO RESET DEVICE                "
			end = min(index+15, len(msg))
			lcd.setText_norefresh(msg[index:end]+"\n{:>3} {:>3} {:>3}".format(keys[0], keys[1], keys[2]))
			if(currentKey == 1):
				keys[0] = get_value()
			elif(currentKey == 2):
				keys[1] = get_value()
			elif(currentKey == 3):
				keys[2] = get_value()
			else:
				if(validateCombo(keys, combo)):
					deviceState = 3
					lcd.setRGB(255,255,255)
					lcd.setText("")
					keys = ["_","_","_"]
				else:
					currentKey = 1
			if(grovepi.digitalRead(PORT_BUTTON)):
				currentKey += 1
			index += 1
			if(index > len(msg)-16):
				index = 0
		time.sleep(0.2)
		grovepi.digitalWrite(PORT_BUZZER,0)
		grovepi.digitalWrite(PORT_RED_LED,0)
		grovepi.digitalWrite(PORT_GREEN_LED,0)
