from flask import Flask
from flask import jsonify
from flask import request

import sys
import json
import time
import asyncio
import threading
import queue
import smtplib
from twilio.rest import Client

account_ssid = 'AC32c39154f82d33309f2001ef3614fd57'
auth_token = ''

app = Flask('Raspberry Pi Security System')
alarm_queue = queue.Queue()

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
	start = time.time()
	print("Alarm triggered at: " + str(start))
	alarm_thread = threading.Thread(target=counter, args=(1,))
	alarm_queue.put(alarm_thread)
	alarm_thread.start()
	return 'Ok'

@app.route('/disarm', methods=['POST'])
def disarm_callback():
	print("Alarm disarmed at: " + str(time.time()))
	alarm_queue.get().__setattr__('state', 0)
	return 'Ok'

def counter(state):
	configFile = open('server_config.txt', 'r+')
	lines = configFile.readlines()
	email = lines[0]
	number = lines[1]
	setattr(threading.current_thread(), 'state', state)
	time.sleep(60)
	if(getattr(threading.current_thread(),'state') != 0):
		client = Client(account_ssid, auth_token)
		message = client.messages.create(from_ = '+14245810952',body = 'Your alarm has been triggered!', to = number)
		s = smtplib.SMTP('smtp.gmail.com', 587)
		s.starttls()
		s.login("rpimotionalarmdevice", "")
		message = "Your alarm has been triggered!"
		s.sendmail("rpimotionalarmdevice", email, message)
		s.quit()

if __name__ == '__main__':
	print("Server started!")
	app.run(threaded=True,debug=False, host='0.0.0.0', port=4250)
