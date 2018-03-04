import os, re
from lib.slackClient import SlackClient
from json import loads
import requests

API_REQUEST_STRING = 'https://api.coinmarketcap.com/v1/ticker/?start=%s&limit=100'

class CoinCoinHandler(object):

  def __init__(self):
    # Todo - put a search in here for `crypto:"<search_term">`
    self.REGEX = re.compile('^.*?(\S+coin)(?:[!? ,.]|$).*$|^.*?Crypto: ?"(.*?)".*$', re.IGNORECASE)
    self.SC = SlackClient(os.environ['responseToken'])

  def can_handle(self, event):
    print(event['event'])

    # Don't reply to self. It doesn't end well...
    if event['event']['subtype'] == u'bot_message':
      return (False,)

    text = event['event']['text']
    match = self.REGEX.match(text)
    if match:
      return (True, [group for group in match.groups() if group][0])
    else:
      return (False,)

  def handle(self, event, match_context):
    channel = event['event']['channel']
    message_id = event['event']['ts']
    coin = self._find_currency(match_context.lower())
    if not coin:
      self.SC.send_threaded_reply(channel, message_id, "Sorry, I couldn't find any cryptocurrency named %s" % match_context)
    else:
      # TODO: Graph.
      # Need to figure out how to extract the chart config and
      # pass it to https://export.highcharts.com/
      self.SC.send_threaded_reply(channel, message_id, self._build_response(coin))

  def _build_response(self, coin):
    return "Cryptocurrency {name!s} is worth ${price_usd!s}. Its value has changed {percent_change_7d!s}%% in the last 7 days.".format(**coin)

  def _find_currency(self, search_term, start_index=0):
    response = loads(requests.get(API_REQUEST_STRING % str(start_index)).text)
    if 'error' in response:
      return None
    for coin in response:
      if coin['name'].lower() == search_term:
        return coin
    else:
      return self._find_currency(search_term, start_index+100)