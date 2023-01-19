from linebot.models import (MessageEvent, TextMessage, TextSendMessage,
                            TemplateSendMessage, CarouselTemplate, FlexSendMessage,
                            CarouselColumn, URIAction)
from db import *


#====== COMMAND HANDLER ======
def handle_commands(event, linebotapi):
  msg = event.message.text

  command = msg.split()[0][1:]
  command_subset = ' '.join(msg.split()[1:])
  commands = {
    'help': cmd_help,
    'echo': cmd_echo,
    'counsel': cmd_counseling,
    'counseling': cmd_counseling,
    'admin': cmd_admin,
    'counselor': cmd_counselor,
    'counselors': cmd_counselor
  }
  
  if command in commands:
    return commands[command](event, command_subset, linebotapi)
  else:
    linebotapi.reply_message(
      event.reply_token,
      TextSendMessage(
        text='Invalid command.\n!help to list all available commands'))

#=============================================
#=============== HELP COMMAND ================ IN DEVELOPMENT
def cmd_help(event, command_subset, linebotapi):
  default_cmd_dict = {
    'echo': 'Echo your message after the command',
    'counsel': 'List all counselors (alias: !counseling)'
  }
  admin_cmd_dict = {
    'admin': 'Access to admin commands',
    'counselor': 'manage counselor list'
  }
  mod_cmd_dict = {
    #To be added mod role maybe? maybe not? who knows?
  }
  #Do admin check. send admin_cmd_dict too if is admin
  linebotapi.push_message(
    event.source.user_id,
    TextSendMessage(
      text=
      "Available commands:\n!echo\n!counsel\n\nYou are looking for help. I know, we're also looking for help. If you want to help, join us at PROBES: https://discord.gg/thZt9g9ZU4"
    ))


#=============================================
#=============== ECHO COMMAND ================
def cmd_echo(event, command_subset, linebotapi):
  linebotapi.push_message(event.source.user_id,
                          TextSendMessage(text=command_subset))


#=============================================
#============ COUNSELING COMMAND ============= IN DEVELOPMENT
def cmd_counseling(event, command_subset, linebotapi):
  counselors = db['counselors']

  contents = []
  for item in counselors:
      content = {
          "type": "bubble",
          "size": "kilo",
          "body": {
              "type": "box",
              "layout": "vertical",
              "contents": [
                  {
                      "type": "text",
                      "text": item['name'],
                      "weight": "bold",
                      "size": "xxl",
                      "align": "center",
                      "color": "#6b7c2c",
                      "margin": "35px"
                  },
                  {
                      "type": "text",
                      "text": "Counselor",
                      "style": "italic",
                      "align": "center",
                      "size": "lg",
                      "color": "#878c40"
                  }
              ],
              "height": "150px",
              "backgroundColor": "#ece7c2"
          },
          "footer": {
              "type": "box",
              "layout": "vertical",
              "contents": [
                  {
                      "type": "button",
                      "action": {
                          "type": "uri",
                          "label": "CONTACT",
                          "uri": f"line://ti/p/~{item['LineID']}"
                      }
                  }
              ]
          }
      }
      contents.append(content)

  carousel= {
        "type": "carousel",
        "contents": contents
    }
  template_message = FlexSendMessage(alt_text='Carousel Template', contents=carousel)
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
          text=
          'Please type your admin command\n!admin <command> <arguments>\n"!admin help" for help on admin commands'
        ))
      return

    #split input to admin command and args
    command = command_subset.split()[0]
    args = command_subset.split()[1:]

    #----------------------------
    #  !admin help
    #  help command, obviously
    if command == "help":
      #list admin commands here with "<command>: <desciption>"
      commands_dict = {
        'list': "List all admins",
        'add': "Give admin privilege to a user",
        'remove': "Remove admin privilege from a user"
      }
      linebotapi.reply_message(event.reply_token,
                               TextSendMessage(text=commands_dict))

    #----------------------------
    #  !admin add <name> <userId>
    #  Give admin privilege to <userId> with name <name>
    if command == "add":
      admins.append({'name': args[0], 'userId': args[1]})
      linebotapi.reply_message(
        event.reply_token,
        TextSendMessage(text="Added " + args[0] + " as an admin (UID: " +
                        args[1] + ')'))

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


#=============================================
#============ COUNSELOR COMMANDS =============


def cmd_counselor(event, command_subset, linebotapi):
  admins = db["admins"]
  counselors = db["counselors"]

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
          text=
          'Please type your command\n!counselor <command> <arguments>\n"!counselor help" for help on counselor management commands'
        ))
      return

    #split input to admin command and args
    command = command_subset.split()[0]
    args = command_subset.split()[1:]

    #----------------------------
    #  !counselor help
    #  help command, obviously
    if command == "help":
      #list admin commands here with "<command>: <desciption>"
      commands_dict = {
        'list': "List all counselors",
        'add': "Add user as a counselor",
        'remove': "Remove user from counselor list"
      }
      #-------> To do <-------
      #Need better message formatting
      linebotapi.reply_message(event.reply_token,
                               TextSendMessage(text=commands_dict))

      
    #----------------------------
    #  !counselor list
    #  List all counselors
    elif command == "list":
      linebotapi.push_message(
        event.source.user_id,
        TextSendMessage(text="List of Counselors:\n" + '\n'.join([
          '{:<20s} {:}'.format(str(element['name']), str(element['LineID']))
          for element in counselors
        ])))
