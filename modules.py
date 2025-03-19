from config import *
from tools import config
import tools
import random
import requests
import time
import random
import json
import html
import string
import math
import os
import io
import logging
import logging.handlers
from PIL import Image
import time
import hashlib
from bs4 import BeautifulSoup

import urllib
import urllib.request
import urllib.parse
import re
import uuid

recent_messages = []
def add_message(msg):
    recent_messages.append(msg)
    if len(recent_messages) > 50:
        recent_messages.pop(0)
    return recent_messages

_food = config["food"]
_poo_count = config["poo_count"]
_emojis = ""
with open(FOOD_EMOJI_FILE, "r") as f:
    _emojis = f.read()
_emojis = list(_emojis)

def cmd_feed(args, message):
    feed_answers = [
        "I bloody hope {0} is edible ...",
        "I'm not sure I ever had {0} ...",
        "The taste of {0} is awful but it's better than nothing  ...",
        "Thanks for the {0}, appreciated!",
        "Please recheck that {0} is food, as well I might grab a Big Mac ...",
        "No Cake?"
    ]

    enough_answers = [
        "I have had enough for now ...",
        "Thanks for trying to feed me with {0}, but my stomach is full ..."
    ]

    if len(_food) >= 30:
        return random.choice(enough_answers).format(" ".join(args))

    _food.append(" ".join(args))
    tools.update_value("food", _food)

    return random.choice(feed_answers).format(" ".join(args))


def cmd_listfood(args, message):
    reply = ""
    if len(_food) == 0:
        return "My stomach is empty"
    if len(args) > 1:
        reply += ' '.join(args)
    reply += "\n"
    reply += "\n".join(_food)
    return reply

def cmd_vomit(args, message):
    if len(_food) < 3:
        return "Is there anything left?"
    count = random.randint(1, int(len(_food) / 2))
    vomitted = []
    for i in range(count):
        item = random.choice(_food)
        vomitted.append(item)
        _food.remove(item)
    tools.update_value("food", _food)
    return f"BLLEAAAAAAAAAAARGGJHHHHHH {', '.join(vomitted)} {'!' * random.randint(3, 8)}"


def cmd_blame(args, message):
    user = message.user.name
    reason = " ".join(args)
    return ":" + str(message._message_id) + f" blames {user} for {reason}"


def cmd_thank(args, message):
    if len(args) < 1:
        return "Please specify what to thank!"
    reply = "thanks "
    reply += args[0]
    reply += " "
    if len(args) > 1:
        reply += ' '.join(args[1:])
    else:
        reply += "for help"
    return ":" + str(message._message_id) + " " + reply


_pee_state = config["pee_state"]


def cmd_pee(args, message):
    global _pee_state
    peeing_messages = {
        0: ["Let's build some dykes ....", 1],
        1: ["Open the floodgates ....", 2],
        2: ["That is gross ....", 3],
        3: ["Evacuate the room, woman and children first!", 0],
    }

    reply = peeing_messages[_pee_state][0]
    _pee_state = peeing_messages[_pee_state][1]

    tools.update_value("pee_state", _pee_state)

    return reply


def cmd_poo(args, message):
    global _poo_count
    error_msg = [
        "Beep... beep...",
        "Constipation!",
        "A-A-A-A-A-AAARGHHHHHH!!!",
        "Don't hurt me....",
        "How dare you can force me to poo when my stomach hurts?!?",
        "MMyy ssttoommmaacchh hhuurrttss aanndd II ccaann''tt ppoooo!!!!!!",
        "*falls in pain*",
        "Toilet Overflow"
    ]
    constipation = random.random() < 0.1
    super_poo = random.random() < 0.1

    if constipation and super_poo:
        super_poo = False

    if constipation:
        # Constipation!
        return random.choice(error_msg)

    msg = ""

    if len(_food) >= 1:
        msg = random.choice(_emojis)
        _food.pop()

    msg += ("💩" + " ") * _poo_count

    if super_poo:
        count = random.randint(2, 10)

        for _ in range(count):
            if _poo_count > 30:
                _poo_count = 1
            else:
                _poo_count += 1
    else:
        if _poo_count > 30:
            _poo_count = 1
        else:
            _poo_count += 1
    tools.update_value("poo_count", _poo_count)
    tools.update_value("food", _food)
    return msg


_wipe_state = config["wipe_state"]


def cmd_wipe(args, message):
    global _poo_count
    global _wipe_state
    wiping_messages = {
        0: ["*takes a toilet paper*", 1],
        1: ["I'm not your mother", 2],
        2: ["You do it yourself", 3],
        3: ["You clean up your own mess", 0],
    }

    reply = wiping_messages[_wipe_state][0]
    _wipe_state = wiping_messages[_wipe_state][1]

    if _poo_count > 3:
        _poo_count = 1

    tools.update_value("poo_count", _poo_count)
    tools.update_value("wipe_state", _wipe_state)

    return reply


def cmd_youtube(args, message):
    if len(args) == 0:
        return "Try searching nothing yourself. >:)"
    html = urllib.request.urlopen(
        "https://www.youtube.com/results?search_query=" +
        urllib.parse.quote(' '.join(args)))
    video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
    if len(video_ids) == 0:
        return "No videos were found!"
    return "https://www.youtube.com/watch?v=" + random.choice(video_ids)


def cmd_yt(args, message):
    return cmd_youtube(args, message)


def cmd_alive(args, message):
    if len(args) == 0:
        return "Strangely, I'm not."
    else:
        return "Yes, also " + ' '.join(args)
    return "Strange bot. @Petəíŕd check the code. Some err!"

def cmd_say(args, message):
    if len(args) == 0:
        return "Error: Provide text to say."

    return ' '.join(args)

def cmd_wake(args, message):
    if len(args) == 0:
        return "***BZZZZZZZZZ!** Nothing woke up!*"

    waking = ' '.join(args)

    phrases = [
        "A single blade of grass has been delicately inserted into the nostrils of {0}. Now we wait.",
        "**BZZZZZZZZZZZZZ!** {0} was *shocked* to get woken up!",
        "A bucket of water was just dumped on poor, poor {0}.",
        "Some angry dogs were just released where {0} is sleeping...",
        "{0} just had their bed dropped into a bull fighting arena.",
        "Let me go test the strobe lights directly over where {0} is sleeping...",
        "*throws cold water on {0}*",
        "{0} was involuntarily rolled onto the floor.",
        "**WAKE UP {0}**!",
        "A bucket of cold ice was just dumped on sleeping {0}.",
        "{0} was thrown into snow. *Brrrrr!*",
        "{0} was shaked to wake up. *Growls*",
    ]

    return random.choice(phrases).format(waking)


def cmd_pizza(args, message):
    return ":" + str(message._message_id) + " https://i.sstatic.net/7FYUQ.gif"


def cmd_why(args, message):
    words = ["I", "you", "did", "does", "because", "while", "being", "forced", "succeed", "guys", "need", "hard", "directly",
             "walk", "run", "created", "indeed", "really", "nice", "bot", "chat", "amusing", "this is", "funny", "wanted"]
    random.shuffle(words)

    punctuation_end = [".", "?", "!"]

    min = 3
    max = 10
    count = random.randint(min, max)

    result = []

    for i in range(count):
        word = random.choice(words)

        while word in result:
            word = random.choice(words)

        if random.random() < 0.1 and i != count - 1:
            word += ","

        result.append(word)

    first = result[0]
    first = list(first)
    first[0] = first[0].upper()
    first = "".join(first)

    result[0] = first
    result = " ".join(result)
    result += random.choice(punctuation_end)

    return result


def cmd_shuffle(args, message):
    random.shuffle(args)
    return " ".join(args)


def cmd_translate(args, message):
    def format_request(query, original_lang, translate_to, email):
        return f"https://api.mymemory.translated.net/get?q={query}&langpair={original_lang}|{translate_to}&de={email}"

    error_codes = {
        1: "Not enough arguments. Perhaps you forgot language?",
        2: "No such language. Both first and second argument should be in ISO-639-1 format."
    }

    possible_langs = "aa,ab,ae,af,ak,am,an,ar,as,av,ay,az,ba,be,bg,bh,bi,bm,bn,bo,br,bs,ca,ce,ch,co,cr,cs,cu,cv,cy,da,de,dv,dz,ee,el,en,eo,es,et,eu,fa,ff,fi,fj,fo,fr,fy,ga,gd,gl,gn,gu,gv,ha,he,hi,ho,hr,ht,hu,hy,hz,ia,id,ie,ig,ii,ik,io,is,it,iu,ja,jv,ka,kg,ki,kj,kk,kl,km,kn,ko,kr,ks,ku,kv,kw,ky,la,lb,lg,li,ln,lo,lt,lu,lv,mg,mh,mi,mk,ml,mn,mr,ms,mt,my,na,nb,nd,ne,ng,nl,nn,no,nr,nv,ny,oc,oj,om,or,os,pa,pi,pl,ps,pt,qu,rm,rn,ro,ru,rw,sa,sc,sd,se,sg,si,sk,sl,sm,sn,so,sq,sr,ss,st,su,sv,sw,ta,te,tg,th,ti,tk,tl,tn,to,tr,ts,tt,tw,ty,ug,uk,ur,uz,ve,vi,vo,wa,wo,xh,yi,yo,za,zh,zu".split(
        ",")

    def parse_args(text):
        parts = text.split(" ")
        args_data = {}
        if len(parts) < 3:
            # Not enough arguments
            return 1
        args_data["original_lang"] = html.escape(parts.pop(0).lower())
        args_data["translate_to"] = html.escape(parts.pop(0).lower())
        if args_data["original_lang"] not in possible_langs or args_data["translate_to"] not in possible_langs:
            return 2
        args_data["query"] = html.escape(" ".join(parts))
        return args_data

    result = parse_args(" ".join(args))

    if type(result) != dict and result in error_codes:
        return error_codes[result]

    translation = requests.get(format_request(
        result["query"], result["original_lang"], result["translate_to"], EMAIL)).json()
    result_text = translation["responseData"]["translatedText"]

    if "EXAMPLE: LANGPAIR=EN|IT USING 2 LETTER ISO OR RFC3066" in result_text:
        return error_codes[2]
    if "PLEASE SELECT TWO DISTINCT LANGUAGES" in result_text:
        return "Please select two distinct languages."
    return result_text


def cmd_help(args, message):
    if len(args) >= 1:
        name = ' '.join(args)
        lower_name = name.lower()
        if lower_name in tools.help_list:
            return f"Help for \"{name}\": " + tools.help_list[lower_name]
        return f"No help found for {name}."

    vars = globals()
    functions = [COMMAND_PREFIX + func[4:]
                 for func in vars if func[:4] == "cmd_"]
    start = "Commands:"
    str_return = "\n".join(functions)
    str_return = str_return.split("\n")
    str_return = sorted(str_return)
    str_return = start + "\n" + "\n".join(str_return)
    return str_return

def cmd_ping(args, message):
    return "@" + ' @'.join(args)


def cmd_status(args, message):
    status_dict = tools.get_status()

    # sort according to action status
    status_dict = dict(
        sorted(status_dict.items(), key=lambda item: item[1]["count"], reverse=True))

    longest_name = 0
    for id in status_dict:
        if len(status_dict[id]["name"]) > longest_name:
            longest_name = len(status_dict[id]["name"])

    statuses = "    user" + " " * (longest_name - 1) + "|" + "  " + " count\n"

    for id in status_dict:
        statuses += "    " + str(status_dict[id]["name"]) + " " * (longest_name - len(
            status_dict[id]["name"])) + "   |   " + str(status_dict[id]["count"]) + "\n"

    return "\n".join(statuses.split("\n")[:6])

def cmd_getallusers(args, message):
    status_dict = tools.get_status()
    sorted_dict = dict(
        sorted(status_dict.items(), key=lambda item: item[1]["count"], reverse=True))
    names_list = [item["name"] for item in sorted_dict.values()]

    return f":{str(message._message_id)} {', '.join(names_list)}\n..."

# hangman
def load_hang_data():
    req = requests.get(HANGMAN_API_URL + "/status").json()
    return req

hang_users = load_hang_data()

def save_hang_data():
    res = requests.post(HANGMAN_API_URL + "/update", json={
        "users": hang_users,
        "key": PA_API_KEY
    })
    return res.ok

def hang_word_worth(word):
    word_worths = {
        1: 12,
        2: 11,
        3: 9,
        4: 8,
        5: 7,
        6: 6,
        7: 5,
        8: 4,
        9: 3,
        10: 2,
        11: 2,
        12: 2,
        13: 2,
        14: 2,
        15: 2,
        16: 2,
        17: 2,
        18: 2,
        19: 2,
        20: 2,
        21: 2,
        22: 2,
        23: 2,
        24: 2,
        25: 2
    }

    return word_worths[len(word)]

hang_words = []

with open("words.txt", "r") as f:
    hang_words = f.read().split("\n")
hang_word = random.choice(hang_words)
hang_turns = 7
hang_format = list("_" * len(hang_word))
hang_failed = ""
hang_man_state = 0
hangman_in_play = False

def giant_s(n):
    return "s" if n != 1 else ""

def cmd_hang(args, message):
    global hang_word, hang_guesses, hang_turns, hang_failed, hang_format, hang_failed, hang_man_state, hangman_in_play, hang_users
    user_id = str(message.user.id)

    if user_id not in hang_users:
        hang_users[user_id] = {
            # the bug was that it did not increase if user wasn't previously there so iFixit by changing default games_played to 1 instead of 0 because if they start a new game, they already played 1 game
            "games_played": 1,
            "games_lost": 0,
            "games_won": 0,
            "name": message.user.name,
            "hang_reputation": 0,
            "pronouns": "they/them"
        }
    elif "hangman_in_play" not in hang_users[user_id] or not hang_users[user_id]["hangman_in_play"]:
        hang_users[user_id]["games_played"] += 1
        hang_users[user_id]["hang_word"] = random.choice(hang_words)
        hang_users[user_id]["hang_turns"] = 7
        hang_users[user_id]["hang_format"] = list("_" * len(hang_users[user_id]["hang_word"]))
        hang_users[user_id]["hang_failed"] = ""
        hang_users[user_id]["hang_man_state"] = 0
        hang_users[user_id]["hangman_in_play"] = True

    hang_users[user_id]["hangman_in_play"] = True
    if "hang_word" not in hang_users[user_id] or not hang_users[user_id]["hang_word"]:
        hang_users[user_id]["hang_word"] = random.choice(hang_words)
        hang_users[user_id]["hang_turns"] = 7
        hang_users[user_id]["hang_format"] = list("_" * len(hang_users[user_id]["hang_word"]))
        hang_users[user_id]["hang_failed"] = ""
        hang_users[user_id]["hang_man_state"] = 0

    if len(args) == 0:
        return "Usage: `!hang <letters>`. The hangman does not listen to replies."
    #? variable variables: hang_word, hang_turns, hang_failed, hang_format, hang_man_state
    arg_s = "".join(args).lower()
    letters = "".join(
        [letter if letter in string.ascii_lowercase else '' for letter in arg_s])
    letters = set(list(letters.lower()))

    new_hang_format = hang_users[user_id]["hang_format"]
    for i in range(len(hang_users[user_id]["hang_word"])):
        if new_hang_format[i] != "_":
            continue

        if hang_users[user_id]["hang_word"][i] in letters:
            new_hang_format[i] = hang_users[user_id]["hang_word"][i]

    letters = ''.join(
        i for i in letters if i not in hang_users[user_id]["hang_failed"] and i not in hang_users[user_id]["hang_word"])
    count = len(letters)
    if (count > 0):
        pass

    hang_users[user_id]["hang_man_state"] = 7 - hang_users[user_id]["hang_turns"]
    hang_users[user_id]["hang_turns"] -= int(count / 2) if count > 1 else count
    # hang_failed = "".join(list(set(letters + hang_failed)))
    hang_users[user_id]["hang_failed"] = unique(hang_users[user_id]["hang_failed"] + letters)
    hang_users[user_id]["hang_format"] = new_hang_format
    save_hang_data()

    lost = hang_users[user_id]["hang_turns"] <= 0
    won = "".join(hang_users[user_id]["hang_format"]) == hang_word

    reply_str = ":" + str(message._message_id) + " "

    if lost or won:
        previous_hang_word = hang_users[user_id]["hang_word"] + ""
        hang_users[user_id]["hang_word"] = random.choice(hang_words)
        hang_users[user_id]["hang_man_state"] = 0
        hang_users[user_id]["hang_turns"] = 7
        hang_users[user_id]["hang_format"] = list("_" * len(hang_word))
        hang_users[user_id]["hang_failed"] = ""
        hang_users[user_id]["hangman_in_play"] = False
        if lost:
            lost_rep = hang_word_worth(previous_hang_word) / 2
            lost_rep = math.floor(lost_rep)
            hang_users[user_id]["hang_reputation"] -= lost_rep
            hang_users[user_id]["games_lost"] += 1
            save_hang_data()
            return reply_str + "You lost. Your reputation has decreased by " + str(lost_rep) + ". The word was " + previous_hang_word + "."
        elif won:
            gained_rep = hang_word_worth(previous_hang_word)
            hang_users[user_id]["hang_reputation"] += gained_rep
            hang_users[user_id]["games_won"] += 1
            save_hang_data()
            return reply_str + "You won! Your reputation has increased by " + str(gained_rep) + ". The word is " + previous_hang_word + "."

    #return_string = hang_pics[hang_man_state] + "\n"
    return_string = " ".join(hang_users[user_id]["hang_format"]) + "\n\n"
    return_string += " ".join(sorted(list(set(hang_users[user_id]["hang_failed"])))) + "\n"
    return_string += "Turns left: " + str(hang_users[user_id]["hang_turns"])

    return_string = return_string.split("\n")
    return_string = "\n".join("    " + string for string in return_string)

    return return_string

PRONOUNS = {
    1: "they/them",
    2: "he/him",
    3: "she/her"
}

def cmd_hang_stats(args, message):
    return_string = ""
    index = 0
    id_or_name = " ".join(args) if len(args) > 0 else None

    sorted_users = {k: v for k, v in sorted(hang_users.items(), key=lambda item: item[1]["hang_reputation"], reverse=True)}
    for user in sorted_users:
        if id_or_name and id_or_name != str(user) and id_or_name != hang_users[user]["name"]: continue
        pronouns = hang_users[user]["pronouns"] if "pronouns" in hang_users[user] else "they/them"
        pronoun_singular = ""
        pronoun_plural = ""
        if pronouns == PRONOUNS[1]:
            pronoun_singular, pronoun_plural = "they", "their"
        elif pronouns == PRONOUNS[2]:
            pronoun_singular, pronoun_plural = "he", "his"
        elif pronouns == PRONOUNS[3]:
            pronoun_singular, pronoun_plural = "she", "her"
        else:
            pronoun_singular, pronoun_plural = pronouns.split("/")

        if index != 0: return_string += "\n---------------\n"
        games_played = hang_users[user]["games_played"]
        games_won = hang_users[user]["games_won"]
        games_lost = hang_users[user]["games_lost"]
        games_forfeited = games_played - games_won - games_lost
        return_string += f"User {hang_users[user]['name']} (user id {user}):\n"
        return_string += f"- has played {games_played} time{giant_s(games_played)}\n"
        return_string += f"""- of which, {pronoun_singular} won {games_won} time{giant_s(games_won)}{" and" if hangman_in_play else ","} lost {games_lost} time{giant_s(games_lost)}"""
        return_string += f", and forfeited {games_forfeited} time{giant_s(games_forfeited)}." if not hangman_in_play else "."
        return_string += f"\n"
        return_string += f"{pronoun_plural.capitalize()} hangman reputation is {hang_users[user]['hang_reputation']}."
        if not id_or_name: index += 1
    return return_string or (f"No users found matching \"{id_or_name}\"." if id_or_name else "No users have played Hangman yet.")

def cmd_hang_setpronouns(args, message):
    if len(args) < 1: return "Please specify a pronoun or pronoun ID (1 = they/them, 2 = he/him, 3 = she/her)."
    first_arg = int(args[0]) if args[0].isnumeric() else args[0]
    if "/" not in "/".join(args) and first_arg not in PRONOUNS: return "Invalid pronouns (perhaps you forgot the second pronoun?)"
    hang_users[str(message.user.id)]["pronouns"] = PRONOUNS[first_arg] if type(first_arg) == int and first_arg in PRONOUNS else "/".join(args)
    save_hang_data()
    return f"Your pronouns have been set to \"{hang_users[str(message.user.id)]['pronouns']}\"."

def cmd_h(args, message):
    return cmd_hang(args, message)


def unique(str):
    new = ""
    for c in str:
        if c in new:
            continue
        new += c
    return new


# Image generation
SF_2_API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2"
SF_1_4_API_URL = "https://api-inference.huggingface.co/models/CompVis/stable-diffusion-v1-4"
SF_1_5_API_URL = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
OJ_API_URL = "https://api-inference.huggingface.co/models/prompthero/openjourney"
OJ_V4_API_URL = "https://api-inference.huggingface.co/models/prompthero/openjourney-v4"
API_URLS = [OJ_API_URL, OJ_V4_API_URL,
            SF_2_API_URL, SF_1_4_API_URL, SF_1_5_API_URL]
API_URL = API_URLS[0]
headers = {"Authorization": "Bearer " + API_KEY}
upload_url = 'http://peterkolosov.pythonanywhere.com/upload'


def query(payload, url):
    response = requests.post(url, headers=headers, json=payload)
    return response.content


def cmd_imagine(args, message):
    string = " ".join(args)
    retries = 0
    response = query({"inputs": string}, API_URL)
    if ("\"error" in str(response)):
        message.message.reply(
            "Due to an internal error, you might experience a long delay. Don't worry though, you will get an image soon.")
    while ("\"error" in str(response)) and retries < 15:
        print(str(response))
        print("Trying again...")
        response = query({"inputs": string}, API_URL)
        retries += 1
        time.sleep(10)
    image = Image.open(io.BytesIO(response))
    timestamp = str(time.time())
    file_name = timestamp + ".jpg"
    image.save(file_name)
    files = {'file': open(file_name, 'rb')}
    response = requests.post(upload_url, files=files)
    os.remove(file_name)

    return ":" + str(message._message_id) + " " + response.text


def cmd_imgmodel(args, message):
    global API_URL
    try:
        modelNum = int(args[0])
        API_URL = API_URLS[modelNum]
        reply = "Model changed."
    except:
        API_URL = API_URLS[0]
        reply = "Model changed to default."

    return ":" + str(message._message_id) + " " + reply

def cmd_gpt2(args, message):
    msg = " ".join(args)
    response = query({
        "inputs": msg
    }, "https://api-inference.huggingface.co/models/openai-community/gpt2")

    return ":" + str(message._message_id) + " " + json.loads(response)[0]["generated_text"]


guess_number = 0
guess_turns = 0
guess_ended = True


def cmd_guess(args, message):
    global guess_number, guess_turns, guess_ended
    reply = ":" + str(message._message_id) + " "
    if len(args) == 2:
        if not guess_ended:
            return reply + "It's too early to set up a new game."

        gmin = args[0]
        gmax = args[1]
        if not gmin.isnumeric():
            return reply + "Min is not an integer."
        if not gmax.isnumeric():
            return reply + "Max is not an integer."
        try:
            gmin, gmax = int(gmin), int(gmax)
        except:
            return reply + "Well thanks for crashing me. Check that the arguments are numbers."

        if gmin > gmax:
            gmin, gmax = gmax, gmin

        guess_number = random.randint(gmin, gmax)
        guess_turns = 0
        guess_ended = False

        return reply + "Initialized a new game."

    if guess_ended:
        return reply + "Error! Game is not initialized. Send `" + COMMAND_PREFIX + "guess <min> <max>`, where the arguments are the lowest number to generate and the highest number to generate for you to guess."

    n = args[0]
    if not n.isnumeric():
        return reply + "Your guess has to be a positive number. Negative numbers shall calm down!"
    n = int(n)

    won = False
    to_reply = "Uhm, I guess you shouldn't have seen this very string."
    turns = guess_turns + 0

    if n < guess_number:
        to_reply = reply + "My number is bigger."
    elif n > guess_number:
        to_reply = reply + "My number is smaller."
    elif n == guess_number:
        won = True
        guess_ended = True
        guess_turns = 0
        to_reply = reply + "To initialize new game, you should send `" + COMMAND_PREFIX + \
            "guess <min> <max>`, where the arguments are the lowest number to generate and the highest number to generate for you to guess."

    if not won:
        guess_turns += 1
    elif won:
        GIANT_S = "turn" if turns == 1 else "turns"
        message.message.reply(
            "You won in " + str(turns) + " " + GIANT_S + "!!")

    return to_reply

def cmd_8ball(args, message):
    skull = " ".join(args)
    fangs = "1234567890abcdef"
    tongue = hashlib.md5(skull.encode("utf-8")).hexdigest()
    coincidence = ""
    coincidence = tongue[tongue.count(tongue[tongue.count(tongue[0])])]

    gaedanken = fred(tongue, coincidence)

    great_decision = "This is impossible!"
    match gaedanken:
        case "0" | "1":
            great_decision = "Of course."
        case "2" | "3":
            great_decision = "Yes!"
        case "4" | "5":
            great_decision = "Well, duh."
        case "6" | "7":
            great_decision = "Yes."
        case "8" | "9":
            great_decision = "Better not tell you now!"
        case "a":
            great_decision = "No way..."
        case "b":
            great_decision = "Chances are lower than you having a crystal ball right now."
        case "c":
            great_decision = "Don't count on it!"
        case "d":
            great_decision = "Nope. Just... nope."
        case "e":
            great_decision = "That's too dubious!"
        case "f":
            great_decision = "Are you kidding!? No!"

    return ":" + str(message._message_id) + " " + great_decision


def fred(string, bones):
    freqd = {}
    for i in string:
        if i in freqd:
            freqd[i] += 1
        else:
            freqd[i] = 5 if i == bones else 1

    return max(freqd, key=freqd.get)


def cmd_read(args, message):
    if len(args) == 0:
        return "Please provide a valid message ID."
    msg_arr = []
    for msg_id in args:
        try:
            url = f"https://chat.{HOST}/messages/{msg_id}/history"
            msg_id = int(msg_id)
            content = requests.get(url)
            if content:
                soup = BeautifulSoup(content.text, "html.parser")
                element = soup.select(".message .content")
                msg_arr.append(str(element[0])[22:].replace("</div>", "").strip())
            else:
                # spaces   intentional
                msg_arr.append(f" `{msg_id}: message not found.` ")
        except:
            msg_arr.append(f" `{msg_id}: not a valid ID.` ")

    return "".join(msg_arr)


API_IMG2TXT = "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-large"


def img2txt(filename):
    with open(filename, "rb") as f:
        data = f.read()
    response = requests.post(API_IMG2TXT, headers=headers, data=data)
    return response.content


def cmd_img2txt(args, message):
    uniq = uuid.uuid4().hex
    if len(args) == 0:
        return "Please provide a valid image."
    try:
        url = "/".join(args)
        r = requests.get(url, allow_redirects=True)
        with open(uniq + ".jpg", 'wb') as f:
            f.write(r.content)

        result = img2txt(uniq + ".jpg")
        print(result, dir(result))
        result = eval(result)[0]["generated_text"]
        if not result.endswith("."):
            result += "."
        result = list(result)
        result[0] = result[0].upper()
        result = "".join(result)
        os.remove(uniq + ".jpg")
        return ":" + str(message._message_id) + " " + result
    except:
        logging.exception("img2txt")
        return "Something went wrong."

FLAN_API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-large"

def cmd_flan(args, message):
    if len(args) == 0:
        return "i'm not sure"

    try:
        response = requests.post(FLAN_API_URL, headers=headers, json={"inputs": " ".join(args)})
        return ":" + str(message._message_id) + " " + response.json()[0]["generated_text"]
    except:
        return "Something went wrong."

def cmd_log(args, message):
    if len(args) == 0:
        return "Log list: https://peterkolosov.pythonanywhere.com/logs"
    return f":{message._message_id} https://peterkolosov.pythonanywhere.com/log/{args[0]}.log"

def cmd_tell(args, message):
    if len(args) == 0:
        return "OK, I'll let nobody know."
    
    user = args.pop(0)
    if len(user) < 3:
        return "Name is too short !!"

    msg = " ".join(args)

    if msg:
        requests.post(TELL_API_URL+"/new", json={
            "user_to_tell": html.unescape(user),
            "user_teller": html.unescape(message.user.name),
            "message": html.unescape(msg)
        })

        return f"OK, I'll let {user} know."
    else:
        return f"OK, I'll let {user} know nothing."

got_mood = 0
def get_mood():
    global got_mood

    if got_mood:
        return mood

    mood = "not even trying"
    try:
        mood = requests.get(MOOD_API_URL).text
    except:
        mood = "failed loser"

    got_mood = 1
    return mood

mood = get_mood()

CONVERT_URL = "https://www.convert.net/gw.php"
def cmd_convert(args, message):
    global mood, recent_messages
    if len(" ".join(args).strip()) == 0: return "Please specify what to convert."

    last_messages = [msg.user.name + ": " + msg.content for msg in recent_messages[len(recent_messages)-20:]]

    req = " ".join(args)
    mooded_request = f"""Recent messages, from the earliest to the latest:
{chr(10).join(last_messages) or "There were no recent messages."}
End of recent messages.
As a {mood} bot, reply to "{req}" from {message.user.name}, using the message list as the context."""

    jsondata = {
        "action": "convert_math",
        "v": mooded_request
    }

    req = requests.post(CONVERT_URL, data=jsondata, headers={'User-Agent': 'Mozilla/5.0'})
    if req.ok:
        return ":" + str(message._message_id) + " " + req.json()["r"] + " [(source)](https://www.convert.net)"
    return "Something went wrong!"

def cmd_mood(args, message):
    global mood
    v = " ".join(args)
    if v == "": return "I am feeling a bit " + mood + "."

    mood = v
    headers = { "Content-Type": "application/json" }
    payload = {
        "new_mood": v
    }

    req = requests.post(MOOD_API_URL + "/set", headers=headers, json=payload)
    if req.ok:
        return ":" + str(message._message_id) + " I am now " + v + ". :D"
    else: return "Something went wrong!"

def cmd_tea(args, message):
    user = message.user.name.replace(" ", "")
    if len(args) != 0: user = args[0]

    tea_flavors = [
        "matcha", "green", "lemon", "mint", "ginger",
        "oolong", "black", "herbal", "Earl Grey", "jasmine"
    ]

    steaming = " steaming" if random.uniform(0, 1) > 0.5 else ""

    return ":" + str(message._message_id) + f" *brews a cup of{steaming} {random.choice(tea_flavors)} tea for @{user}*"

def cmd_recents(args, message):
    return "\n".join([msg.user.name + ": " + msg.content for msg in recent_messages[len(recent_messages)-20:]])

browser = None
def pass_browser(obj):
    global browser
    browser = obj

def cmd_delete(args, message):
    global browser
    for arg in args:
        if arg.isnumeric():
            try:
                browser.delete_message(int(arg))
            except:
                logging.exception("delete_message")
                return "Something went wrong while deleting message " + arg
   
    return "Done"
