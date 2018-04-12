# -*- coding: utf-8 -*-

import os
from lib.slackClient import SlackClient

class HELLACTIONHandler(object):

  def __init__(self):
    self.SC = SlackClient(os.environ['responseToken'])

  def can_handle(self, event):
    print('HELLACTIONHandler received event:')
    print(event)
    is_hellish = self._is_hellish(event['event']['text'].lower())
    return (is_hellish, None)

  def _is_hellish(self, s):
    return any(x in s for x in ['hellaction', 'hell action', 'hell-action'])

  def handle(self, event, match_context):
    print('Trying to respond to event ')
    print(event)
    channel = event['event']['channel']
    message_id = event['event']['ts']
    response = self.SC.react(channel, message_id, 'fire')
    print('Response was ')
    print(response)
