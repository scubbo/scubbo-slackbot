import re
from lib.slackClient import SlackClient

class CoinCoinHandler(object):

  def __init__(self):
    self.REGEX = re.compile('.*(\S+coin).*')
    self.SC = SlackClient(os.environ['responseToken'])

  def can_handle(self, event):
    print(event['event'])
    text = event['event']['text']
    match = self.REGEX.match(text)
    if match and event['event']['user'] == 'U1S0XJP0W':
      return (True, match.group(1))
    else:
      return (False,)

  def handle(self, event, match_context):
    channel = event['event']['channel']
    message_id = event['event']['ts']
    self.SC.send_threaded_reply(self, channel, message_id, "I see you want to know about " + match_context)
