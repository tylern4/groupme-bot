import json as js
import os
import sys

from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from urllib.parse import urlencode
from flask import Flask, request
import requests
from random import randrange, choice


import praw

reddit = praw.Reddit(client_id=os.getenv("REDDIT_CLIENT_ID"),
                     client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
                     user_agent=os.getenv("REDDIT_USER_AGENT"))


app = Flask(__name__)

reply_words = {
    "chotu?": 0,
    "meme": 1,
    "dank": 1,
    "slap": 1,
    "verse?": 2,
    "bible?": 2,
    "genesis": 3,
    "exodus": 3,
    "leviticus": 3,
    "numbers": 3,
    "deuteronomy": 3,
    "joshua": 3,
    "judges": 3,
    "ruth": 3,
    "1samuel": 3,
    "2samuel": 3,
    "1kings": 3,
    "2kings": 3,
    "1chronicles": 3,
    "2chronicles": 3,
    "ezra": 3,
    "nehemiah": 3,
    "esther": 3,
    "job": 3,
    "psalm": 3,
    "proverbs": 3,
    "ecclesiastes": 3,
    "song of solomon": 3,
    "isaiah": 3,
    "jeremiah": 3,
    "lamentations": 3,
    "ezekiel": 3,
    "daniel": 3,
    "hosea": 3,
    "joel": 3,
    "amos": 3,
    "obadiah": 3,
    "jonah": 3,
    "micah": 3,
    "nahum": 3,
    "habakkuk": 3,
    "zephaniah": 3,
    "haggai": 3,
    "zechariah": 3,
    "malachi": 3,
    "matthew": 3,
    "mark": 3,
    "luke": 3,
    "john": 3,
    "acts": 3,
    "romans": 3,
    "1corinthians": 3,
    "2corinthians": 3,
    "galatians": 3,
    "ephesians": 3,
    "philippians": 3,
    "colossians": 3,
    "1thessalonians": 3,
    "2thessalonians": 3,
    "1timothy": 3,
    "2timothy": 3,
    "titus": 3,
    "philemon": 3,
    "hebrews": 3,
    "james": 3,
    "1peter": 3,
    "2peter": 3,
    "1john": 3,
    "2john": 3,
    "3john": 3,
    "jude": 3,
    "revelation": 3,
}

groupme_url = 'https://api.groupme.com/v3/bots/post'
groupme_image_url = 'https://image.groupme.com/pictures'
bible_url = "https://api.esv.org/v3/passage/text"

message = None


@app.route('/test')
def test():
    if message == None:
        return "", 200
    else:
        return message, 200


# Called whenever the app's callback URL receives a POST request
# That'll happen every time a message is sent in the group
@app.route('/', methods=['POST'])
def webhook():
    # 'message' is an object that represents a single GroupMe message.
    message = request.get_json()
    # if str(message['group_id']) != str(os.getenv('GROUPME_CHAT_ID')):
    #    return "Wrong group\n", 200

    # The user_id of the user who sent the most recently message
    if message['sender_type'] == "bot":
        return "Not going to reply to myself\n", 200

    text = message['text']
    responce = parse_text(text)
    if responce == 0:
        text = """Meow I\'m Chotu 🐱:
Nick\'s been teaching me all about the computers so I can reply to you.
========
Nick doesn't know but I've also been on the reddit getting all the great memes 😸. Just ask me for one and I'll send it right over:
\tmeme
"""
        send_message(text)
        return "Help is on the way\n", 200
    elif responce == 1:
        meme_reply()
        return "Bot replied meme\n", 200
    # elif responce == 2:
    #    random_verse()
    #    return "Bot replied random verse\n", 200
    # elif responce == 3:
    #    verse_reply(text)
    #    return "Bot replied verse\n", 200

    return "No reply\n", 200


################################################################################
def parse_text(currentmessage):
    currentmessage = currentmessage.lower()
    for word, reply in reply_words.items():
        if word in currentmessage:
            return reply


# Send a message in the groupchat
def verse_reply(verse):
    try:
        params = {
            'q': verse,
            'include-short-copyright': False,
        }
        headers = {
            "Authorization": f"Token {os.getenv('BIBLE_API_KEY')}"
        }
        response = requests.get(bible_url, params=params, headers=headers)
        passage = response.json()['passages']
        for pas in passage:
            send_message(pas)
    except Exception as e:
        message = e
        data = {
            'bot_id'		: os.getenv('GROUPME_BOT_ID'),
            'text'			: f"Couldn't find \"{verse}\" \n\n....Maybe you should read your Bible more often. ⛪"
        }
        gm_request = Request(groupme_url, urlencode(data).encode())
        json = urlopen(gm_request).read().decode()


def random_verse():
    verses_list = js.load(open('random_verses.json'))
    verses = choice(verses_list)
    ver = choice(list(verses))
    verse_reply(verses[ver])


def send_message(text):
    if len(text) > 1000:
        split_verse = text.split("\n\n", 2)
        for sv in split_verse:
            send_message(sv)

    data = {
        'bot_id'		: os.getenv('GROUPME_BOT_ID'),
        'text'			: text
    }
    try:
        gm_request = Request(groupme_url, urlencode(data).encode())
        json = urlopen(gm_request).read().decode()
    except Exception as e:
        message = e
        print(e)


def upload_image_to_groupme(imgURL):
    imgRequest = requests.get(imgURL, stream=True)
    filename = 'temp.png'
    postImage = None
    if imgRequest.status_code == 200:
        # Save Image
        with open(filename, 'wb') as image:
            for chunk in imgRequest:
                image.write(chunk)
        # Send Image
        headers = {'content-type': 'application/json'}
        files = {'file': open(filename, 'rb')}
        payload = {'access_token': os.getenv('GROUPME_BOT_ACCESS_TOKEN')}
        r = requests.post(groupme_image_url, files=files, params=payload)
        imageurl = r.json()['payload']['url']
        os.remove(filename)
        return imageurl


def meme_reply():
    limits = 500
    new_subs = [s for s in reddit.subreddit(
        'dankchristianmemes').new(limit=limits)]
    meme = new_subs[randrange(limits)]

    try:
        data = {
            'bot_id'		: os.getenv('GROUPME_BOT_ID'),
            'text'			: meme.title,
            'picture_url'	: upload_image_to_groupme(meme.url)
        }
    except Exception as e:
        data = {
            'bot_id'		: os.getenv('GROUPME_BOT_ID'),
            'text':         f'{meme.title} , {meme.url}'
        }

    try:
        gm_request = Request(groupme_url, urlencode(data).encode())
        json = urlopen(gm_request).read().decode()
    except Exception as e:
        data = {
            'bot_id'		: os.getenv('GROUPME_BOT_ID'),
            'text'			: f"⛪⛪⛪⛪ {e}"
        }
        gm_request = Request(groupme_url, urlencode(data).encode())
        json = urlopen(gm_request).read().decode()
