from linebot.models import *
from replit import db
import random
from txt_formatter import *

#=======SEND MESSAGE==========
def send_message(event, message, linebotapi):
    if event.source.type == 'group':
      linebotapi.push_message(event.source.group_id, message)
    elif event.source.type == 'user':
      linebotapi.push_message(event.source.user_id, message)
    elif event.source.type == 'room':
      linebotapi.push_message(event.source.room_id, message)

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
    'menu': cmd_menu,
    'credits': cmd_credits,
    'credit': cmd_credits,
  }
  admin_commands={
    'forward': cmd_forward,
    'admin': cmd_admin,
    'management': cmd_counselor,
    'manage': cmd_counselor,
  }

  #Load admins and mods
  admins = db["admins"] #Load admin list
  mods = db["mods"] #Load mod list
  
  if command in commands:
    return commands[command](event, command_subset, linebotapi)
  elif next((item for item in admins if item["userId"] == event.source.user_id), True) != True and command in admin_commands:
    return admin_commands[command](event, command_subset, linebotapi)
  else:
    linebotapi.reply_message(
      event.reply_token,
      TextSendMessage(
        text='Invalid command.\n!help to list all available commands'))

#=============================================
#=============== COMMAND DICTIONARY===========
default_cmd_dict = {
  'echo': ' <message>\nEcho your message after the command',
  'credit': '\nCredits'
}

admin_cmd_dict = {
  'admin': ' <admin_command>\nAccess to admin commands',
  'manage': '\nmanage counselor list \n(alias: !management)'
}

services_cmd_dict = {
  'counsel': '\nList all counselors \n(alias: !counseling)'
}
mod_cmd_dict = {
  #To be added mod role maybe? maybe not? who knows?
}  

#=============================================
#=============== HELP COMMAND ================ IN DEVELOPMENT
def cmd_help(event, command_subset, linebotapi):
  admins = db["admins"] #Load admin list
  mods = db["mods"] #Load mod list

  #Create command list
  cmd_list = "Available commands:"
  for key, value in default_cmd_dict.items():
    cmd_list+="\n\n• !"+key+value
  for key, value in services_cmd_dict.items():
    cmd_list+="\n\n• !"+key+value
  
    
  #Do admin check. send admin_cmd_dict too if is admin 
  if next((item for item in admins if item["userId"] == event.source.user_id), True) != True:
    cmd_list += "\n\nAdmin commands:"
    for key, value in admin_cmd_dict.items():
      cmd_list += "\n\n• !"+key+value     

  #Do mod check. send mod_cmd_dict too if is mod or admin
  if next((item for item in admins if item["userId"] == event.source.user_id), True) != True or next((item for item in mods if item["userId"] == event.source.user_id), True) != True:
    cmd_list+="\n\nMod commands:"
    for key, value in mod_cmd_dict.items():
      cmd_list+="\n\n!"+key+value
      
  #Message for !help
  linebotapi.reply_message(event.reply_token, TextSendMessage(text=cmd_list+"\n\nYou are looking for help. I know, we're also looking for help. If you want to help, join us at PROBES: https://discord.gg/thZt9g9ZU4"))

#=============================================
#=============== ECHO COMMAND ================
def cmd_echo(event, command_subset, linebotapi):
  linebotapi.reply_message(event.reply_token, TextSendMessage(text=command_subset))
  
#=============================================
#=============== MENU COMMAND ================  
def cmd_menu(event, command_subset, linebotapi):
  #Create service list
  cmd_list = "Available services:"
  for key, value in services_cmd_dict.items():
    cmd_list += "\n\n!"+key+value
      
  #Message for !help
  linebotapi.reply_message(event.reply_token, TextSendMessage(text=cmd_list, quick_reply = QuickReply(items=[QuickReplyButton(action=MessageAction(label="Counselor", text="!counsel"))])))
  
#=============================================
#============ COUNSELING COMMAND ============= IN DEVELOPMENT
def cmd_counseling(event, command_subset, linebotapi):
  counselors = db['counselors']
  random.shuffle(counselors)
  
  contents = []
  for item in counselors:
      content = {
      "type": "bubble",
      "size": "nano",
      "body": {
        "type": "box",
        "layout": "vertical",
        "contents": [
          {
            "type": "text",
            "text": item["name"],
            "weight": "bold",
            "size": "xl",
            "align": "center",
            "color": "#6b7c2c",
            "margin": "15px"
          },
          {
            "type": "text",
            "text": "Counselor",
            "style": "italic",
            "align": "center",
            "size": "md",
            "color": "#878c40"
          }
        ],
        "height": "100px",
        "backgroundColor": "#ece7c2"
      },
      "footer": {
        "type": "box",
        "layout": "vertical",
        "contents": [
          {
            "type": "text",
            "text": "CONTACT",
            "color": "#428fd6",
            "align": "center",
            "margin": "5px",
            "action": {
              "type": "uri",
              "label": "action",
              "uri": f"line://ti/p/~{item['LineID']}"
            }
          }
        ],
        "height": "50px"
      }
    }
      contents.append(content)
  
  carousel= {
        "type": "carousel",
        "contents": contents
    }
  template_message = FlexSendMessage(alt_text='Silakan pilih counsel.', text="Silakan pilih.", contents=carousel)
  send_message(event, TextSendMessage(text="Silakan pilih counsel di bawah ini."), linebotapi)
  send_message(event, template_message, linebotapi)
  
  # linebotapi.reply_message(event.reply_token, TextSendMessage(text="Silakan pilih counsel di bawah ini."))
  # linebotapi.push_message(event.source.group_id, TextSendMessage(text=template_message)))
  
#================== ADMIN ====================
#============== ADMIN COMMANDS ===============
def cmd_admin(event, command_subset, linebotapi):

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

  if not command_subset:
    linebotapi.reply_message(
      event.reply_token,
      TextSendMessage(
        text=
        'Please type your command\n!counselor <command> <arguments>\n"!counselor help" for help on counselor management commands'
      ))

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

#=============================================
#============ FORWARD COMMAND ================ IN DEVELOPMENT
def cmd_forward(event, command_subset, linebotapi):
  if event.source.type != 'user':
    linebotapi.reply_message(event.reply_token, TextSendMessage(text="Perintah ini tidak dapat digunakan di grup atau MPC."))

#=============================================
#============ CREDITS ========================
def cmd_credits(event, command_subset, linebotapi):
  linebotapi.reply_message(event.reply_token, TextSendMessage(text="Izaru, damnnotplaywell, ScPz"))