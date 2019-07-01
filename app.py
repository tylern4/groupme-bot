import json as js
import os
import sys

from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from urllib.parse import urlencode
from flask import Flask, request
from random import randrange

import praw

reddit = praw.Reddit(client_id=os.getenv("REDDIT_CLIENT_ID"),
                     client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
                     user_agent=os.getenv("REDDIT_USER_AGENT"))


app = Flask(__name__)

reply_words = {
    "meme": 1,
    "dank": 1,
    "slap": 1,
    "verse": 2,
    "bible": 2,
}

groupme_url = 'https://api.groupme.com/v3/bots/post'
groupme_image_url = 'https://image.groupme.com/pictures'


@app.route('/test')
def ok(message="Test working"):
    return message, 200


# Called whenever the app's callback URL receives a POST request
# That'll happen every time a message is sent in the group
@app.route('/', methods=['POST'])
def webhook():
    # 'message' is an object that represents a single GroupMe message.
    message = request.get_json()
    if str(message['group_id']) != str(os.getenv('GROUPME_CHAT_ID')):
        return "Wrong group\n", 200

    # The user_id of the user who sent the most recently message
    if message['sender_type'] == "bot":
        return "Not going to reply to myself\n", 200

    text = message['text']
    reponse = parse_text(text)
    if reponse == 1:
        meme_reply()
        return "Bot replied\n", 200
    elif reponse == 2:
        mes = text[text.find(":")+1:]
        verse_reply(mes)
        return "Bot replied\n", 200

    return "No reply\n", 200


################################################################################

# Send a message in the groupchat
def verse_reply(verse):
    _verse = verse.replace(" ", "+")
    bible_url = f"https://api.esv.org/v3/passage/text/?q={_verse}"
    auth = {"Authorization": f"Token {os.getenv('BIBLE_API_KEY')}"}
    bible_request = Request(bible_url, headers=auth)
    try:
        bible_json = urlopen(bible_request).read().decode()
        data = {
            'bot_id'		: os.getenv('GROUPME_BOT_ID'),
            'text'			: js.loads(bible_json)["passages"][0].strip()
        }
        gm_request = Request(groupme_url, urlencode(data).encode())
        json = urlopen(gm_request).read().decode()
    except:
        data = {
            'bot_id'		: os.getenv('GROUPME_BOT_ID'),
            'text'			: f"Couldn't find \"{verse}\" \n\n....Maybe you should read your Bible more often. ⛪"
        }
        gm_request = Request(groupme_url, urlencode(data).encode())
        json = urlopen(gm_request).read().decode()


def upload_image_to_groupme(imgURL):
    import requests
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


def parse_text(currentmessage):
    currentmessage = currentmessage.lower().strip()
    for word, reply in reply_words.items():
        if word in currentmessage:
            return reply


def meme_reply():
    limits = 100
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
