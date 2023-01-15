##JSON
import json

def printjson(json_object):
  json_formatted_str = json.dumps(json_object, indent=2)

  print(json_formatted_str)
  return 'OK'
