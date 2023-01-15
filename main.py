import os
import json
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

#Logging
from logging.config import dictConfig

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'WARNING',
        'handlers': ['wsgi']
    }
})

#App Init
app = Flask(__name__)

def printjson(json_object):
  json_formatted_str = json.dumps(json_object, indent=2)

  print(json_formatted_str)
  return 'OK'
  
ChAccToken = os.environ['CHANNEL_ACCESS_TOKEN']
ChSecret = os.environ['CHANNEL_SECRET']
# Channel Access Token
line_bot_api = LineBotApi(ChAccToken)
# Channel Secret
handler = WebhookHandler(ChSecret)

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
    #app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

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
    if event.source.user_id == Raisal:
      msg = "Raisal: " + event.message.text
      line_bot_api.push_message(Leo, TextSendMessage(text=msg))
    elif event.source.user_id == Leo:
      msg = "Leo: " + event.message.text
      line_bot_api.push_message(Raisal, TextSendMessage(text=msg))
    else:
      line_bot_api.reply_message(event.reply_token, TextSendMessage(text=event.message.text))


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)