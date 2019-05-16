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

def configureDevice():
	isConfigured = False
	configState = 1
	currentKey = 1
	keys = [0,0,0]
	distance = 0
	#have user create combination lock
	while(not isConfigured):
		if(configState == 1):
			lcd.setText_norefresh("Set Combination:\n{:>3} {:>3} {:>3}".format(keys[0], keys[1], keys[2]))
			#Change key one by one by pressing button
			if(currentKey == 1):
				keys[0] = get_value()
			elif(currentKey == 2):
				keys[1] = get_value()
			elif(currentKey == 3):
				keys[2] = get_value()
			else:
				configState += 1
				lcd.setText("")
			if(grovepi.digitalRead(PORT_BUTTON)):
				currentKey += 1
				grovepi.digitalWrite(PORT_BUZZER,1)
		else:
			#set distance the device will be away from the door frame
			distance = get_value()
			lcd.setText_norefresh("Set Distance:\n{:>3}".format(distance))
			if(grovepi.digitalRead(PORT_BUTTON)):
				isConfigured = True
				grovepi.digitalWrite(PORT_BUZZER,1)
		time.sleep(0.2)
		grovepi.digitalWrite(PORT_BUZZER,0)
	#write to the config file and clear display
	lcd.setText("")
	lcd.setRGB(0,0,0)
	configFile = open("security_config.txt", "w+")
	for key in keys:
		configFile.write(str(key)+"\n")
	configFile.write(str(distance) + "\n")

if __name__ == '__main__':
	#configuration setup
	if(not os.path.isfile("security_config.txt")):
		configureDevice()
	#import user settings
	configFile = open("security_config.txt", "r+")
	lines = configFile.readlines()
	combo = [int(lines[0]), int(lines[1]), int(lines[2])]
	distance = int(lines[3])
	print(lines)
	#main loop logic
	while True:
		measured_distance = grovepi.ultrasonicRead(PORT_RANGE)
		lcd.setText_norefresh(str(measured_distance))
