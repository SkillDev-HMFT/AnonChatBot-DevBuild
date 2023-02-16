from linebot.models import *
from replit import db


def msg_defaultResponse():
  command = {"Menu": "!menu", "Help": "!help"}
  actions = []
  text = "Selamat datang! Silakan pilih perintah berikut."

  for key, value in command.items():
    actions.append(MessageAction(label=key, text=value))

  template = ButtonsTemplate(title='HMFT Official Account',
                             text=text,
                             actions=actions)

  text_message = TemplateSendMessage(alt_text='Selamat datang!',
                                     template=template)
  return text_message
