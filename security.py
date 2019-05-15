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
		currentInt = 1
		int1 = 0
		int2 = 0
		int3 = 0
		while(not isConfigured):
			if(currentInt == 1):
				int1 = get_value()
			elif(currentInt == 2):
				int2 = get_value()
			elif(currentInt == 3):
				int3 = get_value()
			else:
				isConfigured = True
			lcd.setText_norefresh("Set Password: {}\n{:>3}, {:>3}, {:>3}".format(currentInt, int1, int2, int3))
			if(grovepi.digitalRead(PORT_BUTTON)):
				currentInt += 1
				grovepi.digitalWrite(PORT_BUZZER,1)
			time.sleep(0.2)
			grovepi.digitalWrite(PORT_BUZZER,0)
	else:
		isConfigured = True