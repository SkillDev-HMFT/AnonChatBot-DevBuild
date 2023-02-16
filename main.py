import os
from flask import Flask, request, abort


from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import *
from linebot.exceptions import *

from printjson import printjson
from cmdhandler import *

# Logging
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

# App Init
app = Flask(__name__)

# Get from environment secrets
ChAccToken = os.environ['CHANNEL_ACCESS_TOKEN']
ChSecret = os.environ['CHANNEL_SECRET']
# Channel Access Token
line_bot_api = LineBotApi(ChAccToken)
# Channel Secret
handler = WebhookHandler(ChSecret)

#for pinging
@app.route('/')
def home():
  return "Samlekom"

# callback Post Request
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

# Message handling
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
  command = {"Menu": "!menu", "Help": "!help"}
  actions = []
  text = "Selamat datang! Silakan pilih perintah berikut."

  for key, value in command.items():
    actions.append(MessageAction(label=key, text=value))
    
  template = ButtonsTemplate(title='HMFT Official Account',
                            text=text,
                            actions=actions)
  
  text_message = TemplateSendMessage(alt_text='Selamat datang!', template=template)
  
  if event.message.text.startswith('!'):
    handle_commands(event, line_bot_api)

  else:
    if event.source.type == 'user':
    # pass
      line_bot_api.reply_message(event.reply_token, text_message)
    
  return 'OK'

if __name__ == "__main__":
  port = int(os.environ.get('PORT', 5000))
  app.run(host='0.0.0.0', port=port)