import sys
import time
import keyboard
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

def get_keypress():
	userInput = keyboard.record(until = 'enter')
	print("recorded!")
	return str(userInput)

def configureDevice():
	isConfigured = False
	configState = 1
	currentKey = 1
	keys = ["","",""]
	distance = ""
	#have user create combination lock
	while(not isConfigured):
		if(configState == 1):
			lcd.setText_norefresh("Set Combination:\n{:>3} {:>3} {:>3}".format(keys[0], keys[1], keys[2]))
			#Change key one by one by pressing button
			if(currentKey == 1):
				keys[0] = get_keypress()
			elif(currentKey == 2):
				keys[1] = get_keypress()
			elif(currentKey == 3):
				keys[2] = get_keypress()
			else:
				configState += 1
				lcd.setText("")
			if(grovepi.digitalRead(PORT_BUTTON)):
				currentKey += 1
				grovepi.digitalWrite(PORT_BUZZER,1)
		elif(configState == 2):
			#set distance the device will be away from the door frame
			distance = get_keypress()
			lcd.setText_norefresh("Set Distance:\n{:>3}".format(distance))
			if(grovepi.digitalRead(PORT_BUTTON)):
				currentKey += 1
				grovepi.digitalWrite(PORT_BUZZER,1)
		else:
			number = get_keypress()
			lcd.setText_norefresh("Set Phone:\n{:>3}".format(number))
			if(grovepi.digitalRead(PORT_BUTTON)):
				grovepi.digitalWrite(PORT_BUZZER,1)
				isConfigured = True
		time.sleep(0.2)
		grovepi.digitalWrite(PORT_BUZZER,0)
	#write to the config file and clear display
	lcd.setText("")
	lcd.setRGB(0,0,0)
	configFile = open("security_config.txt", "w+")
	for key in keys:
		configFile.write(str(key)+"\n")
	configFile.write(str(distance) + "\n")

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
	# configFile = open("security_config.txt", "r+")
	# lines = configFile.readlines()
	# combo = [int(lines[0]), int(lines[1]), int(lines[2])]
	# distance = int(lines[3])
	# # print(combo)
	# alarm = False
	# #main loop logic
	# keys = [0,0,0]
	# currentKey = 1
	# while True:
	# 	if(not alarm):
	# 		measured_distance = grovepi.ultrasonicRead(PORT_RANGE)
	# 		if(measured_distance < distance -5 or measured_distance > distance + 5):
	# 			alarm = True
	# 		start = time.time()
	# 	else:
	# 		timeDiff = int(time.time()) - int(start)
	# 		lcd.setText_norefresh("{:>2} S UNTIL ALARM\n{:>3} {:>3} {:>3}".format(timeDiff, keys[0], keys[1], keys[2]))
	# 		if(currentKey == 1):
	# 			keys[0] = get_value()
	# 		elif(currentKey == 2):
	# 			keys[1] = get_value()
	# 		elif(currentKey == 3):
	# 			keys[2] = get_value()
	# 		# else:
	# 		# 	if(validateCombo(keys, combo)):
	# 		# 		disarm()
	# 		# 	else:
	# 		# 		#send notification to user
	# 		grovepi.digitalWrite(PORT_BUZZER,1)
	# 		grovepi.digitalWrite(PORT_RED_LED, 1)
	# 		#if(timeDiff  >= 30):
	# 			#send sms and email

	# 	time.sleep(0.2)
	# 	grovepi.digitalWrite(PORT_BUZZER,0)
	# 	grovepi.digitalWrite(PORT_RED_LED,0)
