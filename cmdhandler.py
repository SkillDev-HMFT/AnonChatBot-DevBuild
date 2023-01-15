from linebot.models import (MessageEvent, TextMessage, TextSendMessage,
                            TemplateSendMessage, CarouselTemplate,
                            CarouselColumn, URIAction)
from replit import db

#====== COMMAND HANDLER ======
def handle_commands(event, linebotapi):
  msg = event.message.text
  if not msg.startswith("!"):
    return None

  command = msg.split()[0][1:]
  command_subset = ' '.join(msg.split()[1:])
  commands = {
    'echo': cmd_echo,
    'counseling': cmd_counseling,
    'admin': cmd_admin
  }
  if command in commands:
    return commands[command](event, command_subset, linebotapi)
  else:
    linebotapi.reply_message(event.reply_token,
                             TextSendMessage(text='Invalid command'))

#=============================================    
#=============== ECHO COMMAND ================
def cmd_echo(event, command_subset, linebotapi):
  linebotapi.reply_message(event.reply_token,
                           TextSendMessage(text=command_subset))

#=============================================
#============ COUNSELING COMMAND =============
def cmd_counseling(event, command_subset, linebotapi):
  data = [{
    'name': 'raisal',
    'LINEID': 'raisalgenre2001'
  }, {
    'name': 'leofardi',
    'LINEID': 'iniidleofardi'
  }]
  carousel_template = CarouselTemplate(columns=[
    CarouselColumn(text='Name: ' + data[0]['name'],
                   actions=[
                     URIAction(label='LINE ID',
                               uri='line://ti/p/~' + data[0]['LINEID'])
                   ]),
    CarouselColumn(text='Name: ' + data[1]['name'],
                   actions=[
                     URIAction(label='LINE ID',
                               uri='line://ti/p/~' + data[1]['LINEID'])
                   ])
  ])
  template_message = TemplateSendMessage(alt_text='Carousel template',
                                         template=carousel_template)
  linebotapi.reply_message(event.reply_token, template_message)

#=============================================
#============== ADMIN COMMANDS ===============
def cmd_admin(event, command_subset, linebotapi):
  admins = db["admins"]

  #Admin privilege check
  if next((item for item in admins if item["userId"] == event.source.user_id),
          False) == False:
    linebotapi.reply_message(
      event.reply_token,
      TextSendMessage(
        text='Anda tidak memiliki izin untuk menggunakan perintah ini'))

  else:
    #Check command was entered or not
    if not command_subset:
      linebotapi.reply_message(
        event.reply_token,
        TextSendMessage(
          text='Please type your admin command\n!admin <command> <arguments>'))
      return

    #split input to admin command and args
    command = command_subset.split()[0]
    args = command_subset.split()[1:]

    
  #----------------------------
  #  !admin add <name> <userId>
  #  Give admin privilege to <userId> with name <name>
    if command == "add":
      linebotapi.reply_message(event.reply_token,
                               TextSendMessage(text="Adding user..."))


      
  #----------------------------
  #  !admin remove <name>
  #  Remove <name> from admin list.
    elif command == "remove":

      if args == []:
        linebotapi.reply_message(
          event.reply_token,
          TextSendMessage(
            text="!admin remove <name>\nRemove <name> from admin list."))

      else:
        linebotapi.reply_message(
          event.reply_token,
          TextSendMessage(text="Removing admin privilege from " + args[0] +
                          '...'))

        user = [element for element in admins if element['name'] == args[0]]

        if user == []:
          linebotapi.push_message(
            event.source.user_id,
            TextSendMessage(text=args[0] + " is not an admin"))
        else:
          for i in user:
            admins.remove(i)
            db["admins"] = admins
            linebotapi.push_message(
              event.source.user_id,
              TextSendMessage(text="Removed admin privilege from " + args[0]))

  #----------------------------
  #  !admin list
  #  List all admins
    elif command == "list":
      linebotapi.push_message(
        event.source.user_id,
        TextSendMessage(text="List of admins:\n" + '\n'.join([
          '{:<20s} {:}'.format(str(element['name']), str(element['userId']))
          for element in admins
        ])))

  #----------------------------
  #If there's no admin command entered
    else:
      linebotapi.reply_message(event.reply_token,
                               TextSendMessage(text="Invalid admin command"))
