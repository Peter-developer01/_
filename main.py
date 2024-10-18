#!/usr/bin/env python
import html
import tools

import chatexchange.client
import chatexchange.events
import chatexchange.browser as browser

import functions
import config
import requests
from markdownify import markdownify as md
from datetime import datetime
import time
import random

import logging
import logging.handlers

def prefix(msg):
    return str(config.PREFIX) + " " + str(msg)

def cmdPrefix(cmd):
	return str(config.COMMAND_PREFIX) + "" + str(cmd)

msgs = []
room = None

def main():
	global room
	host_id = config.HOST
	room_id = config.ROOM_ID

	client = chatexchange.client.Client(host_id)
	client.login(config.CRED_EMAIL, config.CRED_PASSWORD)

	room = client.get_room(room_id)
	room.join()
	room.watch(on_message)

	print("(You are now in room #%s on %s.)" % (room_id, host_id))
	tools.log_event(tools.get_time(), "bot_restart", "PetlinBOT", None)
	#room.send_message("~ PetlinBOT Online.")
	count = 1
	while True:
		print("running, " + str(count))
		count += 1
		time.sleep(60)

	client.logout()

def check_tells(user):
	tell_list = requests.get(config.TELL_API_URL).json()
	for i in range(0, len(tell_list)):
		tell = tell_list[i]
		if tell[0].startswith(user.name[:3]):
			room.send_message(prefix(f"@{user.name.replace(' ', '')}, I have a message for you from {tell[1]}: \"{tell[2]}\""))
			requests.post(config.TELL_API_URL+"/remove", json={
				"to_remove": i
			})

	
	return 0

def other_action(message):
	def event(event_name):
		return isinstance(message, event_name)

	def is_me(name):
		if name == "PetlinBOT": return True
		return False	

	if event(chatexchange.events.MessageStarred):
		reply = f'Not [everything](https://chat.{config.HOST}/transcript/message/{message._message_id}#{message._message_id}) is star-worthy...'
		if not message._message_stars % 2:
			reply = f'[Stars](https://chat.{config.HOST}/transcript/message/{message._message_id}#{message._message_id}) get removed under peer-pressure?'
		room.send_message(prefix(reply))
	elif event(chatexchange.events.UserEntered):
		if !is_me(message.user.name):
			tools.log_event(tools.get_time(), "user_join", message.user.name, None)
		check_tells(message.user)
	elif event(chatexchange.events.UserLeft):
		tools.log_event(tools.get_time(), "user_left", message.user.name, None)

def on_message(message, client):
	global functions
	try:
		tools.update_status(message.user.id, message.user.name)
	except:
		logging.exception("")
	
	if not isinstance(message, chatexchange.events.MessagePosted) and not isinstance(message, chatexchange.events.MessageEdited):
		other_action(message)
		return
	
	tools.log_event(tools.get_time(), "new_message", html.unescape(message.user.name), html.unescape(message.content))

	# in case the user somehow sneaked behind the UserEntered detector
	if message.user.name != "PetlinBOT":
		check_tells(message.user)

	print(">> (%s, %s) %s" % (message.user.name, message._message_id, message.content))
	msgs.append(message.content)
	if "".join(msgs[-3:]) == message.content * 3:
		room.send_message(prefix(message.content))
	if not message.content.startswith(config.COMMAND_PREFIX): return

	try:
		reply = html.unescape(functions.command(message.content, message))
		if reply != None and reply != False:
			if reply.startswith("https://www.youtube.com/") or reply.startswith(":") or message.content.startswith(config.COMMAND_PREFIX + "status"):
				room.send_message(reply)
			else:
				if (message.content.startswith(config.COMMAND_PREFIX + "hang") or message.content.startswith(config.COMMAND_PREFIX + "hang")):
					room.send_message(reply.replace("\\*", "*"))
				else:
					room.send_message(prefix(md(reply).replace("\\*", "*")))
	except:
		logging.exception("")
		message.message.reply("Something went wrong!")

if __name__ == '__main__':
	main()
