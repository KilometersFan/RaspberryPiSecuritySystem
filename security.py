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
	slope = 40/1023
	key_f = 60 + round(sensor_value*slope)
	return int(key_f)

if __name__ == '__main__':
	#configuration setup
	isConfigured = False
	if(not os.path.isfile("config.txt")):
		currentKey = 1
		keys = [0,0,0]
		#have user create combination lock
		while(not isConfigured):
			if(currentKey == 1):
				keys[0] = get_value()
			elif(currentKey == 2):
				keys[1] = get_value()
			elif(currentKey == 3):
				keys[2] = get_value()
			else:
				isConfigured = True
			lcd.setText_norefresh("Set Combination:\n{:>3}, {:>3}, {:>3}".format(keys[0], keys[1], keys[2]))
			if(grovepi.digitalRead(PORT_BUTTON)):
				currentKey += 1
				grovepi.digitalWrite(PORT_BUZZER,1)
			time.sleep(0.2)
			grovepi.digitalWrite(PORT_BUZZER,0)
		#write to the config file
		configFile = open("config.txt", "w+")
		for key in keys:
			configFile.write(str(key))
	else:
		isConfigured = True