# -*- coding: utf-8 -*-

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

    # Block any messages in the #mtg channel
    if ('channel' in event['event']) and (event['event']['channel'] is u'C4WF0612L'):
      return (False,)

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
      card_data_from_api = loads(requests.get('https://netrunnerdb.com/api/2.0/public/card/' + card['code']).text)
      attachment = {
        'color': self._getColor(card_data_from_api),
        'image_url': self._getImageUrl(card['code'], card_data_from_api),
        'title': card['title'],
        'title_link': 'https://netrunnerdb.com/en/card/' + card['code'],
        'fields': [
          {
            'value': self._parseText(card_data_from_api)
          }
          #Netrunnerdb API doesn't give flavour text :(
        ]
      }
      self.SC.send_attachments_threaded_reply(channel, message_id, attachment)

  def _parseText(self, card_data):
    bare_text = card_data['data'][0]['text']
    return bare_text.replace('[subroutine]', '↳')

  def _getColor(self, card_data):
    try:
      if card_data['data'][0]['side_code'] == 'runner':
        return '#ff0000'
      else:
        return '#0000ff'
    except Exception as e:
      # If we get any exception fetching side_code
      print(e)
      return '#333333'

  def _getImageUrl(self, card_id, card_data):
    if 'data' in card_data and 'image_url' in card_data['data'][0]:
      return card_data['data'][0]['image_url']
    else:
      return card_data['imageUrlTemplate'].replace('{code}', card_id)