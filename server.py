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
start = 0
email = ""
number = ""
loop = asyncio.get_event_loop()

@app.route('/configure', methods=['POST'])
def configure():
	payload = request.get_json()
	email = payload['email']
	number = payload['number']

@app.route('/alarm_triggered', methods=['POST'])
def alarm_triggered_callback():
	payload = request.json()
	print("Alarm triggered at: " + str(payload['time']))
	start = time.time()
	# loop = asyncio.get_event_loop()
	# loop.run_until_complete(counter())

@app.route('/disarm', methods=['POST'])
def disarm_callback(time):
	payload = request.json()
	print("Alarm triggered at: " + str(payload['time']))
	start = 0

async def counter():
	end = time.time()
	while(end - start < 60):
		end = time.time()
	if(start != 0):
		# client = Client(account_ssid, auth_token)
		# message = client.messages.create(from_ = '+14245810952',body = 'Your alarm has been triggered!', to = number)
		s = smtplib.SMTP('smtp.gmail.com', 587)
		s.starttls()
		s.login("rpimotionalarmdevice", "")
		message = "Your alarm has been triggered!"
		s.sendmail("rpimotionalarmdevice", email, message)
		s.quit()
	start = 0


if __name__ == '__main__':
	print("Server started!")
	app.run(debug=False, host='0.0.0.0', port=4250)