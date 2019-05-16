import sys
import time
import os.path
sys.path.append('/home/pi/Dexter/GrovePi/Software/Python')
import grovepi
import grove_rgb_lcd as lcd

PORT_BUTTON = 3
PORT_BUZZER = 4
PORT_ROTARY = 2
PORT_RANGE = 7
PORT_RED_LED = 5
PORT_GREEN_LED = 6 

grovepi.pinMode(PORT_BUZZER, "OUTPUT")
grovepi.pinMode(PORT_BUTTON, "INPUT")
grovepi.pinMode(PORT_ROTARY,"INPUT") 
grovepi.pinMode(PORT_RED_LED, "OUTPUT")
grovepi.pinMode(PORT_GREEN_LED, "OUTPUT")
lcd.setRGB(255,255,255)

def get_value():
	sensor_value = grovepi.analogRead(PORT_ROTARY)
	key_f = 0
	slope = 300/1023
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

def configureDevice():
	isConfigured = False
	configState = 1
	currentKey = 1
	keys = ["0","0","0"]
	distance = "0"
	number, email = "", ""
	#have user create combination lock
	while(not isConfigured):
		if(configState == 1):
			lcd.setText_norefresh("Set Combination:\n{:>3} {:>3} {:>3}".format(keys[0], keys[1], keys[2]))
			#Change key one by one by pressing button
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
			if(currentKey > 3):
				configState += 1
				lcd.setText("")
		elif(configState == 2):
			#set distance the device will be away from the door frame
			lcd.setText_norefresh("Set Distance:\n{}".format(distance))
			distance = input("Enter a distance value between 0 and 513: ")
			while (not validateInput(2, distance)):
				print("Invalid input. Distance must be between 0 and 513.")
				distance = input("Enter a distance value between 0 and 513: ")
			configState += 1
			lcd.setText("")
		elif(configState == 3):
			lcd.setText_norefresh("Set Phone:\n{}".format(number))
			number = input("Enter a phone number to send sms alerts to: ")
			configState += 1
			lcd.setText("")
		else:
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
	lcd.setRGB(0,0,0)
	configFile = open("security_config.txt", "w+")
	for key in keys:
		configFile.write(str(key) +"\n")
	configFile.write(str(distance) + "\n")
	configFile.write(str(number) + "\n")
	configFile.write(str(email) + "\n")

def validateCombo(userKeys, keys):
	for i in range(3):
		if(userKeys[i] != keys[i]):
			return False
	return True

if __name__ == '__main__':
	#configuration setup
	if(not os.path.isfile("security_config.txt")):
		configureDevice()
	#import user settings
	configFile = open("security_config.txt", "r+")
	lines = configFile.readlines()
	combo = [int(lines[0]), int(lines[1]), int(lines[2])]
	distance = int(lines[3])
	deviceState = 1
	#main loop logic
	keys = [0,0,0]
	currentKey = 1
	lcd.setRGB(0,0,0)
	while True:
		if(deviceState == 1):
			grovepi.digitalWrite(PORT_GREEN_LED,1)
			measured_distance = grovepi.ultrasonicRead(PORT_RANGE)
			if(measured_distance < distance -5 or measured_distance > distance + 5):
				deviceState = 2
			start = time.time()
		elif(deviceState == 2):
			lcd.setRGB(255,255,255)
			timeDiff = int(time.time()) - int(start)
			lcd.setText_norefresh("{:>2} S UNTIL ALARM\n{:>3} {:>3} {:>3}".format(timeDiff, keys[0], keys[1], keys[2]))
			if(currentKey == 1):
				keys[0] = get_value()
			elif(currentKey == 2):
				keys[1] = get_value()
			elif(currentKey == 3):
				keys[2] = get_value()
			else:
				if(validateCombo(keys, combo)):
					deviceState = 3
				else:
					currentKey = 1
					lcd.setRGB(255,0,0)
			if(grovepi.digitalRead(PORT_BUTTON)):
				currentKey += 1
			grovepi.digitalWrite(PORT_BUZZER,1)
			grovepi.digitalWrite(PORT_RED_LED,1)
			if(timeDiff  >= 30):
				deviceState = 4
		elif(deviceState == 3):
			count = 0
			index = 0
			msg = "HOLD BTN 5 SEC TO DISARM"
			lcd.setText("")
			lcd.setText_norefresh("DEVICE DISARMED")
			lcd.setText_norefresh(msg[index:index+15])
			while(grovepi.digitalRead(PORT_BUTTON)):
				count += 1
				if(count == 25):
					deviceState = 1
			index += 1
			if(index > len(msg)):
				index  = 0

		time.sleep(0.2)
		grovepi.digitalWrite(PORT_BUZZER,0)
		grovepi.digitalWrite(PORT_RED_LED,0)
		grovepi.digitalWrite(PORT_GREEN_LED,0)
