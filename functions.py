import random
import uuid
from config import *
from modules import *
from collections import namedtuple
import re

notfound_strings = [
	"WUT?",
	"Maybe lookup my instructions?",
	"Have you tried the help command?",
	"What are you talking about?",
	"This is not the command you are looking for.",
	"{0}? What?"
]

def upper_first(s):
	return s[0].upper() + s[1:]

def get_answer(command = "", args = [], message = None):
	command = "cmd_" + command
	if command in globals():
		return globals()[command](args, message)
	else:
		return random.choice(notfound_strings).format(upper_first(command.split("_")[1]))

def command(message, raw_message):
	if type(message) != str: return
	if not message.startswith(COMMAND_PREFIX): return

	command = message.split(COMMAND_PREFIX)[1].split(" ")[0]
	command = command.lower()
	args = message
	args = args[len(COMMAND_PREFIX)+len(command)+1:]
	args = args.split(" ")
	if args[0] == '':
		args = args[1:]

	return get_answer(nest(raw_message).content, args, raw_message)

msg = namedtuple("msg", ["reply"])
class Msg:
	def __init__(self, content, user, reply, id):
		self._message_id = id
		self.content = content.strip()
		self.message = msg(reply=reply)
		self.user = user

nest_regex = re.compile(r"{{[^{}]*}}")
reply_regex = re.compile(r"^:\d{8}\s")
sin_lbregex = re.compile(r"(?<!{){(?!{)")
sin_rbregex = re.compile(r"(?<!})}(?!})")
UNIQUE_RIGHT_BRACKET = str(uuid.uuid4())
UNIQUE_LEFT_BRACKET = str(uuid.uuid4())

def nest(message):
	message.content = re.sub(sin_lbregex, UNIQUE_LEFT_BRACKET, message.content)
	message.content = re.sub(sin_rbregex, UNIQUE_RIGHT_BRACKET, message.content)
	matches = re.findall(nest_regex, message.content)
	for match in matches:
		start = message.content.find(match)
		end = start + len(match)
		match = match[2:-2]
		command = match.split(" ")[0]
		answer = nest(Msg(get_answer(command, match.split()[1:], message), message.user, message.message.reply, message._message_id))
		if answer.content.startswith(PREFIX + " "): answer.content = answer.content[len(PREFIX) + 1:]
		answer = re.sub(reply_regex, "", answer.content)
		message.content = message.content[:start] + answer + message.content[end:]

	if re.findall(nest_regex, message.content): message.content = nest(message.content)
	message.content = message.content.replace(UNIQUE_LEFT_BRACKET, "{").replace(UNIQUE_RIGHT_BRACKET, "}")
	return message
