from flask import Flask
from flask import jsonify
from flask import request

import sys
import json
import time
import asyncio
import smtplib
from twilio.rest import Client

account_ssid = 'AC32c39154f82d33309f2001ef3614fd57'
auth_token = ''

app = Flask('Raspberry Pi Security System')
server_state = 0
was_disarmed = False
loop = asyncio.get_event_loop()

@app.route('/configure', methods=['POST'])
def configure():
	configFile = open('server_config.txt', 'w+')
	payload = request.get_json()
	email = payload['email']
	number = payload['number']
	configFile.write(email+"\n")
	configFile.write(number)
	configFile.close()
	return 'Ok'

@app.route('/alarm_triggered', methods=['POST'])
def alarm_triggered_callback():
	payload = request.get_json()
	print("Alarm triggered at: " + str(payload['time']))
	global server_state 
	server_state = 1
	loop = asyncio.new_event_loop()
	asyncio.set_event_loop(loop)
	loop.run_until_complete(counter())
	return 'Ok'

@app.route('/disarm', methods=['POST'])
def disarm_callback():
	payload = request.get_json()
	print("Alarm disarmed at: " + str(payload['time']))
	global server_state 
	server_state = 0
	global was_disarmed
	was_disarmed = True
	return 'Ok'

async def wait_60():
	asyncio.sleep(60)
	return False

async def counter():
	configFile = open('server_config.txt', 'r+')
	lines = configFile.readlines()
	email = lines[0]
	number = lines[1]
	global server_state 
	await asyncio.sleep(60)
	if(server_state != 0):
		# client = Client(account_ssid, auth_token)
		# message = client.messages.create(from_ = '+14245810952',body = 'Your alarm has been triggered!', to = number)
		s = smtplib.SMTP('smtp.gmail.com', 587)
		s.starttls()
		s.login("rpimotionalarmdevice", "")
		message = "Your alarm has been triggered!"
		s.sendmail("rpimotionalarmdevice", email, message)
		s.quit()
	server_state = 0


if __name__ == '__main__':
	print("Server started!")
	app.run(debug=False, host='0.0.0.0', port=4250)
