import random
import tools
from config import *
from modules import *

notfound_strings = [
	"WUT?",
	"Maybe lookup my instructions?",
	"Have you tried the help command? This would help.",
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

	return get_answer(command, args, raw_message)

