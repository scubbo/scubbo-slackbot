# -*- coding: utf-8 -*-
import os, re, sys
import urllib2
from json import loads, dumps
sys.path.append('lib')
from slackClient import SlackClient

REGEX = re.compile('\[\[(.*?)\]\]')
ALL_CARDS = loads(urllib2.urlopen('https://netrunnerdb.com/api/2.0/public/cards').read())['data']

with file('abbreviations.json', 'r') as f:
  ABBREVIATIONS = loads(f.read())

def handler(event, context):
  text = event['event']['text']
  channel = event['event']['channel']
  message_id = event['event']['ts']

  matches = REGEX.findall(text)

  if matches:
    print 'matches was some'
    for match in matches:
      print 'working on ' + str(match)
      if match in ABBREVIATIONS:
        print 'match was in ABBREVIATIONS'
        match = ABBREVIATIONS[match]
      print 'checking for ' + match
      for card in ALL_CARDS:
        if all([c in card['title'].lower() for c in match.lower().split()]):
          print 'all condition was matched'
          sc = SlackClient(os.environ['responseToken'])
          attachment = {
            'image_url': 'https://netrunnerdb.com/card_image/' + card['code'] + '.png',
            'title': card['title']
          }
          sc.send_attachments_threaded_reply(channel, message_id, attachment)
          break
  else:
    print 'matches was None'
  return {
    "statusCode": 200,
    "headers": {"Content-Type":"application/json"},
    "body": 'I hear ya'
  }
