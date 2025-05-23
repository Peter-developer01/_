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
import re
import modules
from bs4 import BeautifulSoup

import logging
import logging.handlers

ignusers = [576644, 540406]
reply_length = len(":xxxxxxxx ")

def prefix(msg):
    return str(config.PREFIX) + " " + str(msg)

def cmdPrefix(cmd):
	return str(config.COMMAND_PREFIX) + "" + str(cmd)

msgs = []
room = None
# legacy stuff
active = True
modules.pass_active(active)

def send_message(room, message):
	global active
	if active: room.send_message(message)
	return False

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
	modules.pass_browser(browser)
	#send_message(room, "~ PetlinBOT Online.")
	count = 1
	while True:
		print("running, " + str(count))
		count += 1
		time.sleep(60)

	client.logout()

def check_tells(user):
	tell_list = requests.get(config.TELL_API_URL).json()
	name = user.name.lower()
	def loop():
		con = 0
		for i in range(0, len(tell_list)):
			tell = tell_list[i]
			if name.startswith(tell[0].lower()) or name.startswith(tell[0][1:].lower()):
				send_message(room, prefix(f"@{user.name.replace(' ', '')}, I have a message for you from {tell[1]}: \"{tell[2]}\""))
				requests.post(config.TELL_API_URL+"/remove", json={
					"to_remove": i
				})

				con = 1
				tell_list.pop(i)
				break
		if con: loop()
	loop()
	
	return 0

def check_pings(content):
	ping_regex = "(?<!@)@{0}(?![\w-])"

	def pingify(name):
		return name[:3] + "".join([l + "?" for l in name[3:]])

	notifications = []
	for user_id in modules.afk_users:
		user = modules.afk_users[user_id]
		pings = re.findall(re.compile(ping_regex.format(pingify(user["name"].replace(" ", "").lower()))), content.lower())
		if len(pings) > 0:
			notifications.append([user["name"], user["reason"]])
	return notifications

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
		send_message(room, prefix(reply))
	elif event(chatexchange.events.UserEntered):
		if not is_me(message.user.name):
			tools.log_event(tools.get_time(), "user_join", message.user.name, None)
		#check_tells(message.user)
	elif event(chatexchange.events.UserLeft):
		tools.log_event(tools.get_time(), "user_left", message.user.name, None)

def read(msg_id):
	if msg_id.isdigit():
		msg_id = msg_id
	elif msg_id.split("#")[-1].isdigit():
		msg_id = msg_id.split("#")[-1]
	elif msg_id.split("/")[-1].isdigit():
		msg_id = msg_id.split("/")[-1]
	url = f"https://chat.{config.HOST}/messages/{msg_id}/history"
	msg_id = int(msg_id)
	content = requests.get(url)
	if content:
		soup = BeautifulSoup(content.text, "html.parser")
		element = soup.select(".message .content .message-source")
		content = element[0].text
		return content
	else:
		return f"`{msg_id}: message not found."

def on_message(msg, client):
	global functions
	#if hasattr(msg, "user"):
	try:
		if msg.user.id in ignusers: return
	except:
		print("Duh ;)")
	message = msg

	try:
		tools.update_status(message.user.id, message.user.name)
		pass
	except:
		logging.exception("")
	
	if not isinstance(message, chatexchange.events.MessagePosted) and not isinstance(message, chatexchange.events.MessageEdited):
		other_action(message)
		return
	if not msg.user: return
	old_content = message.content
	clean_content = message.content
	pingstart = False
	reply_id = None
	if message.content:
		if modules.is_afk(message.user):
			modules.unregister_afk_user(message.user)
			if not message.content.startswith(config.COMMAND_PREFIX + "afk"):
				message.message.reply("Welcome back!")
		pingstart = message.content.startswith("@PetlinBOT")
		maybe_ping = message.content.split(" ")[0]
		message.content = read(str(message._message_id))
		old_content = message.content
		clean_content = message.content
		ids = re.findall(r"^:\d{8}\s", message.content)
		if ids:
			try:
				reply_id = int(ids[0][1:9])
			except:
				logging.exception("")
		if maybe_ping and maybe_ping.startswith("@") and re.findall(r"^:\d{8}\s", message.content): old_content = maybe_ping + old_content[9:]
		if pingstart: message.content = "@PetlinBOT" + message.content[10:]
		
		reply_notifications = ""
		ping_notifications = check_pings(old_content)
		for notification in ping_notifications:
			reason = notification[1]
			reply_notifications += f"{notification[0]} is away{': ' + reason if reason else ''}\n"
		reply_notifications = reply_notifications[:-1]
		if reply_notifications and message.user.id != 579700:
			message.message.reply(reply_notifications)
	modules.add_message(message)
	replied = False
	rm_regex = re.compile(r"^:\d{8}\s(rm|del|delete|remove)$")
	if re.findall(rm_regex, clean_content) and message.content.startswith("@PetlinBOT"):
		try:
			#functions.command(f"{config.COMMAND_PREFIX}delete {message.content[1:9]}", message)
			modules.cmd_delete([clean_content[1:9]], message)
			replied = True
		except:
			logging.exception("on reply rm")
			message.message.reply("Unable to delete message.")

	old = message.content + ""
	if message.content and "@petl" in message.content.lower() and message.user.id not in [375672, 579700] and not replied: # ignonrgin oaky and myself
		try:
			old = message.content + ""
			# message.message.reply("What do you need?")
			start_ping_regex = re.compile("^@petl?i?n?b?o?t?", re.I)
			content = re.sub(start_ping_regex, "", message.content.strip())
			message.content = config.COMMAND_PREFIX + "convert " + content
			#ping_replace_regex = re.compile('@petli?n?b?o?t?', re.IGNORECASE)
			#content = ping_replace_regex.sub("(ping mentioning you)", content)
			
			reply = functions.command(config.COMMAND_PREFIX + "convert " + content, message)
	
			if reply != None and reply != False:
				reply = reply.replace("<span>", "").replace("</span>", "")
				if len(reply) > 480:
					n = 480
					l = [reply[i:i+n] for i in range(0, len(reply), n)]
					for v in l:
						send_message(room, html.unescape(v))
				else: send_message(room, html.unescape(reply))
			replied = True
		except:
			logging.exception("on mention")
			message.message.reply("Something went wrong!")
	message.content = old
	
	#if message.content and html.unescape(message.content).startswith("<div class="): message.content = message.content[18:-6]
	if reply_id:
		message.content = message.content.split(" ")[1:]
		message.content = ":" + str(reply_id) + " " +  " ".join(message.content)
	tools.log_event(tools.get_time(), "new_message", html.unescape(message.user.name), html.unescape(message.content or ""), message_id=message._message_id)

	if message.user.name != "PetlinBOT":
		check_tells(message.user)

	print(">> (%s, %s) %s" % (message.user.name, message._message_id, message.content))
	msgs.append(message.content)
	if "".join(msgs[-3:]) == message.content * 3:
		send_message(room, prefix(message.content))
	if not message.content.startswith(config.COMMAND_PREFIX): return
	try:
		if message.content.strip() == config.COMMAND_PREFIX: return
	except:
		pass

	if replied: return
	def nowrap(content):
		content = content.lower()
		if content.startswith(config.COMMAND_PREFIX + "status"): return True
		elif content.startswith(config.COMMAND_PREFIX + "hang "): return True
		elif content.startswith(config.COMMAND_PREFIX + "h "): return True
		return False
	try:
		#reply = html.unescape(functions.command(message.content, message))
		reply = functions.command(message.content, message)
		if reply != None and reply != False and reply != modules.UNIQUE_NO_OUTPUT:
			reply = reply.replace("<span>", "").replace("</span>", "")
			if reply.startswith("https://www.youtube.com/") or reply.startswith(":") or message.content.lower().startswith(config.COMMAND_PREFIX + "status"):
				if len(reply) > 480 and not nowrap(message.content):
					n = 480
					l = [reply[i:i+n] for i in range(0, len(reply), n)]
					for v in l:
						send_message(room, v)
				else: send_message(room, reply)
			else:
				if nowrap(message.content):
					send_message(room, reply.replace("\\*", "*"))
				else:
					if len(reply) > 480:
						n = 480
						l = [reply[i:i+n] for i in range(0, len(reply), n)]
						for v in l:
							send_message(room, prefix(v))
					else:
						send_message(room, prefix(reply))
	except:
		logging.exception("command")
		message.message.reply("Something went wrong!")

if __name__ == '__main__':
	main()
