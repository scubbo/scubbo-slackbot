# -*- coding: utf-8 -*-

import os
from lib.slackClient import SlackClient

class ScorthCardHandler(object):

  def __init__(self):
    self.SC = SlackClient(os.environ['responseToken'])

  def can_handle(self, event):
    return ('scorch' in event['event']['text'].lower(),)

  def handle(self, event, match_context):
    channel = event['event']['channel']
    message_id = event['event']['ts']
    attachment = {
      'mrkdwn_in': ['fields'],
      'fields': [
        {
          'value': 'Did you mean _a scorth card_?'
        }
      ]
    }
    self.SC.send_attachments_threaded_reply(channel, message_id, attachment)
