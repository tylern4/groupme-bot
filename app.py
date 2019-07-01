import json
import os
import sys

from urllib.request import Request, urlopen
from urllib.parse import urlencode
from flask import Flask, request


app = Flask(__name__)


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
        return "Wrong group \n", 200

    # The user_id of the user who sent the most recently message
    if message['sender_type'] == "bot":
        return "Not going to reply to myself\n", 200

    # current message to be parsed
    currentmessage = message['text'].lower().strip()
    text_reply(currentmessage)

    return "Bot replied\n", 200


################################################################################

# Send a message in the groupchat
def text_reply(msg):
    url = 'https://api.groupme.com/v3/bots/post'
    data = {
        'bot_id'		: os.getenv('GROUPME_BOT_ID'),
        'text'			: msg
    }
    request = Request(url, urlencode(data).encode())
    json = urlopen(request).read().decode()


# Send a message with an image attached in the groupchat
def image_reply(msg, imgURL):
    url = 'https://api.groupme.com/v3/bots/post'
    urlOnGroupMeService = upload_image_to_groupme(imgURL)
    data = {
        'bot_id'		: os.getenv('GROUPME_BOT_ID'),
        'text'			: msg,
        'picture_url'	: urlOnGroupMeService
    }
    request = Request(url, urlencode(data).encode())
    json = urlopen(request).read().decode()


# Uploads image to GroupMe's services and returns the new URL
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
        url = 'https://image.groupme.com/pictures'
        files = {'file': open(filename, 'rb')}
        payload = {'access_token': os.getenv('ACCESS_TOKEN')}
        r = requests.post(url, files=files, params=payload)
        imageurl = r.json()['payload']['url']
        os.remove(filename)
        return imageurl
