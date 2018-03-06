import os, re
import requests
from json import loads
from lib.slackClient import SlackClient

class NetrunnerCardHandler(object):

  def __init__(self):
    with open('abbreviations.json', 'r') as f:
      self.ABBREVIATIONS = loads(f.read())

    self.REGEX = re.compile('\[\[(.*?)\]\]')
    self.ALL_CARDS = loads(requests.get('https://netrunnerdb.com/api/2.0/public/cards').text)['data']
    self.SC = SlackClient(os.environ['responseToken'])

  def can_handle(self, event):
    """
    Return a tuple of (boolean, context) so that the latter can be
    passed into `handle` if the former is true
    """
    text = event['event']['text']

    matches = self.REGEX.findall(text)

    if matches:
      responseCards = []
      for match in matches:
        if match in self.ABBREVIATIONS:
          match = self.ABBREVIATIONS[match]
        for card in self.ALL_CARDS:
          if all([c in card['title'].lower() for c in match.lower().split()]):
            responseCards.append(card)
            break
      return (bool(responseCards), {'cards':responseCards})
    else:
      return (False,)

  def handle(self, event, match_context):
    channel = event['event']['channel']
    message_id = event['event']['ts']
    cards = match_context['cards']

    for card in cards:
      attachment = {
        'image_url': self._getImageUrl(card['code']),
        'title': card['title']
      }
      print('DEBUG: calling SC.send_attachments_threaded_reply with ' + str(channel) + ':' + str(message_id) + ':' + str(attachment))
      self.SC.send_attachments_threaded_reply(channel, message_id, attachment)

  def _getImageUrl(self, cardId):
    card_data_from_api = loads(requests.get('https://netrunnerdb.com/api/2.0/public/card/' + cardId).text)
    if 'data' in card_data_from_api and 'image_url' in card_data_from_api['data'][0]:
      return card_data_from_api['data'][0]['image_url']
    else:
      return card_data_from_api['imageUrlTemplate'].replace('{code}', cardId)