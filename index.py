# -*- coding: utf-8 -*-
import os, re, sys
import requests
from json import loads, dumps
sys.path.append('lib')
from slackClient import SlackClient

HANDLER_NAMES = [f[:-3] for f in os.listdir('lib') if f.endswith('Handler.py')]
# Can't define this as a standalone method for some reason - the method can't be found
HANDLERS = map(lambda x: getattr(__import__(x), x)(), HANDLER_NAMES)

def handler(event, context):
  for handler in HANDLERS:
    can_handle = handler.can_handle(event)
    if (can_handle[0]):
      handler.handle(event, can_handle[1])

  return {
    "statusCode": 200,
    "headers": {"Content-Type":"application/json"},
    "body": 'I hear ya'
  }
