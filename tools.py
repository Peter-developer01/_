# Tools.
import json
from datetime import datetime
import requests
from config import LOGGER_API_URL, STATUS_API_URL, CONFIG_API_URL
import time

config = requests.get(CONFIG_API_URL).json()


def get_value(name = ""):
	if name == "":
		raise KeyError("name")

	return config[name]

def get_status():
	return requests.get(STATUS_API_URL+"/get").json()
status = get_status()
time.sleep(2)

def update_status(id, name):
	status = get_status()
	id = str(id)
	cur = None

	if id in status:
		cur = status[id]["count"]
	else:
		cur = 0

	status[id] = {
		"name": name,
		"count": cur + 1
	}

	with open("status.json", "w") as f:
		f.write(json.dumps(status))

	requests.post(STATUS_API_URL+"/update", json={
		"updated": id,
		"name": name,
		"count": status[id]["count"]
	})

def update_value(name = "", value = ""):
	if name == "":
		raise KeyError("name")

	config[name] = value
	requests.post(CONFIG_API_URL+"/update", json=config)

def _pad_time(num):
	if len(str(num)) == 1:
		return "0" + str(num)
	else: return str(num)

def get_time():
	d = time.localtime()
	date_string = "%s-%s-%s %s:%s:%s" % (_pad_time(d.tm_year), _pad_time(d.tm_mon), _pad_time(d.tm_mday), _pad_time(d.tm_hour), _pad_time(d.tm_min), _pad_time(d.tm_sec))
	return date_string

def log_event(time, event_type, user, text):
	match event_type:
		case "new_message":
			requests.post(LOGGER_API_URL, json={
				"timestamp": time,
				"event": event_type,
				"user": user,
				"text": text
			})
		case "user_join":
			requests.post(LOGGER_API_URL, json={
				"timestamp": time,
				"event": event_type,
				"user": user
			})
		case "user_left":
			requests.post(LOGGER_API_URL, json={
				"timestamp": time,
				"event": event_type,
				"user": user
			})
		case "bot_restart":
			requests.post(LOGGER_API_URL, json={
				"timestamp": time,
				"event": event_type,
				"user": user
			})

	return "Done."

help_list = {
	"alive": "Check if the bot is alive.",
	"blame": "Blame someone for [insert reason here]. Syntax: //blame [reason]",
	"feed": "Makes bot eat anything you pass in the arguments.",
	"help": "Display list of commands.",
	"listfood": "List food that was eaten by `feed` command.",
	"pee": "Pee. Shall I say you more about that?",
	"ping": "Ping [insert person here]. It will add `@` symbol to the text.",
	"pizza": "Download pizza.",
	"poo": "Poo. Removes the last food if the food is present. Warning: you might get stuck in constipation.",
	"reinstate": "Reinstate something. Selects a random reinstating message from a list.",
	"say": "Broadcast a message to the room.",
	"shuffle": "Shuffle arguments.",
	"thank": "Thanks [something].",
	"vomit": "Vomit food. Selects random count of food to vomit and random food. Will take food away from stomach.",
	"wake": "Selects a random message to wake someone.",
	"why": "Why do you need to use this command? Why?",
	"wipe": "Wipe your poo.",
	"youtube": "Fast-search YouTube. Will return the first result.",
	"yt": "An alias for youtube.",
	"translate": "Translate text. Syntax: `translate [source language] [destination language] [source text]`. Both source language and destination language should be in ISO-639-1 format.",
	"imagine": "Image generation. Uses HuggingFace.",
	"imgmodel": "Config command. Select a model from a list of available models.",
	"hang": "Play hangman with the bot.",
	"guess": "Useless number guessing game. The bot will generate a number and you have to guess it.",
	"img2txt": "Translate image to text (explain). The image must be in JPG format. May not work randomly because it's free.",
	"flan": "Just for laughs. May decide to not work randomly.",
	"log": "Get a link to logs. Syntax: [year]-[month]-[day] (should be numbers).",
	"tell": "Tell someone something. The bot will ping the person and tell them something whenever it notices activity.",
	"status": "Get a list of users and their activity counts."
}

# Left here for historical reasons.
# Is not used anymore.
def uwuifier(text):
	def uwuify(text):
		now = datetime.now()
		seed = datetime.timestamp(now)
		uwu = uwuitpy.uwuipy(seed, 0.1, 0, 0.1, 0)
		return uwu.uwuify(text)
		
	def uwuicy_(text):
		now = datetime.now()
		seed = datetime.timestamp(now)
		uwu = uwuicy.uwuipy(seed)
		return uwu.uwuify(text)

	if config["uwuify"] == 1:
		text = uwuify(text)
	if config["uwuicy"] == 1:
		text = uwuicy_(text)

	return text
