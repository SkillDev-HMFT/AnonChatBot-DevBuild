import os
from flask import Flask, request, abort

from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import *
from linebot.exceptions import *

from printjson import printjson
from cmdhandler import *

from replit import db

#Logging
from logging.config import dictConfig

dictConfig({
  'version': 1,
  'formatters': {
    'default': {
      'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }
  },
  'handlers': {
    'wsgi': {
      'class': 'logging.StreamHandler',
      'stream': 'ext://flask.logging.wsgi_errors_stream',
      'formatter': 'default'
    }
  },
  'root': {
    'level': 'WARNING',
    'handlers': ['wsgi']
  }
})

db["admins"] = [{
  'name': 'Raisal',
  'userId': 'U524c29c53c53057bae735bab657cf07c'},
                {
  'name': 'Airi',
  'userId': 'U524c29c53c53057bae735bab657cf07c'},
                {
  'name': 'Vinya',
  'userId': 'U524c29c53c53057bae735bab657cf07c'},
                {
  'name': 'Mike',
  'userId': 'U524c29c53c53057bae735bab657cf07c'},
               ]
#App Init
app = Flask(__name__)

#Get from environment secrets
ChAccToken = os.environ['CHANNEL_ACCESS_TOKEN']
ChSecret = os.environ['CHANNEL_SECRET']
# Channel Access Token
line_bot_api = LineBotApi(ChAccToken)
# Channel Secret
handler = WebhookHandler(ChSecret)


#for pinging
@app.route('/')
def home():
  return "I'm alive"


# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
  # get X-Line-Signature header value
  signature = request.headers['X-Line-Signature']
  # get request body as text
  body = request.get_data(as_text=True)

  #Print for debugging
  #app.logger.info("Request body: " + body)
  #printjson(request.get_json())  

  # handle webhook body
  try:
    handler.handle(body, signature)
  except InvalidSignatureError:
    abort(400)
  except LineBotApiError as e:
    app.logger.warning("Send message fail", e)
    abort(400)
  return 'OK'


#Send message <to> = userID <message> = message to send
@app.route('/testSend/<to>/<message>', methods=['GET'])
def testSend(to, message):
  try:
    line_bot_api.push_message(to, TextSendMessage(text=message))
  except LineBotApiError as e:
    app.logger.warning("Send message fail", e)
    abort(400)
  return 'OK'


#=====Test ID======
Leo = os.environ['IdLeofardi']
Raisal = os.environ['IdRaisal']


# Simple Echo
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
  if event.message.text.startswith('!'):
    handle_commands(event, line_bot_api)

  return 'OK'


if __name__ == "__main__":
  port = int(os.environ.get('PORT', 5000))
  app.run(host='0.0.0.0', port=port)
