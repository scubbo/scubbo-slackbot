import os
from unittest.mock import patch, mock_open
import requests
from requests_mock import Mocker
from lib.CoinCoinHandler import CoinCoinHandler
from json import loads, dumps

#TODO: extract this
TEST_RESPONSE_TOKEN = 'test-response-token'
TEST_CHANNEL = 'test-channel'
TEST_MESSAGE_ID = 'test-message-id'
os.environ['responseToken'] = TEST_RESPONSE_TOKEN

API_REQUEST_STRING_1 = 'https://api.coinmarketcap.com/v1/ticker/?start=0&limit=100'
API_REQUEST_STRING_2 = 'https://api.coinmarketcap.com/v1/ticker/?start=100&limit=100'
API_REQUEST_STRING_3 = 'https://api.coinmarketcap.com/v1/ticker/?start=200&limit=100'

RESPONSE_1 = '[{"name":"test_name_1","price_usd":"0.01","percent_change_7d":"2.34"},{"name":"test_name_2","price_usd":"1337","percent_change_7d":"1.23"}]'
RESPONSE_2 = '[{"name":"test_name_3", "price_usd":"0.12","percent_change_7d":"-0.06"}]'
ERROR_RESPONSE = '{"error":"id not found"}'

#TODO: extract this
POST_MESSAGE_URL = 'https://slack.com/api/chat.postMessage'

def test_can_handle():
  cch = CoinCoinHandler()

  case_1 = cch.can_handle(_build_event('Tell me about foocoin'))
  assert case_1[0]
  assert case_1[1] == 'foocoin'

  case_2 = cch.can_handle(_build_event('Is barcoin worth anything?'))
  assert case_2[0]
  assert case_2[1] == 'barcoin'

  case_3 = cch.can_handle(_build_event('YeAh LoL MuH BiTcOiN iS sO vAlUaBlE'))
  assert case_3[0]
  assert case_3[1] == 'BiTcOiN'

  case_4 = cch.can_handle(_build_event('Nani!? WaifuCoin!???!?!'))
  assert case_4[0]
  assert case_4[1] == 'WaifuCoin'

  case_5 = cch.can_handle(_build_event('While you were partying, I studied the blockchain'))
  assert not case_5[0]

  case_6 = cch.can_handle(_build_event('I don\'t care about your silly Internet coinage'))
  assert not case_6[0]

  case_7 = cch.can_handle(_build_event('My favourite hobby is frescoing'))
  assert not case_7[0]

  case_8 = cch.can_handle(_build_event('Bitcoin and dogecoin and lolcoin, oh my!'))
  assert case_8[0]
  assert case_8[1] == 'Bitcoin' # Just do the first one

  case_9 = cch.can_handle(_build_event('Computer, Crypto: "Neo-Anarchism Is Super Cool" is my search term'))
  assert case_9[0]
  assert case_9[1] == 'Neo-Anarchism Is Super Cool'

@Mocker(kw='requests_mock')
def test_handle_1(**kwargs):
  mock = _setup_handle_and_return_mock(kwargs)

  cch = CoinCoinHandler()
  cch.handle(_build_event(''), 'test_name_1')

  _assertionsForSingleCall(mock, 'Cryptocurrency test_name_1 is worth $0.01. Its value has changed 2.34%% in the last 7 days.')

@Mocker(kw='requests_mock')
def test_handle_2(**kwargs):
  mock = _setup_handle_and_return_mock(kwargs)

  cch = CoinCoinHandler()
  cch.handle(_build_event(''), 'test_name_2')

  _assertionsForSingleCall(mock, 'Cryptocurrency test_name_2 is worth $1337. Its value has changed 1.23%% in the last 7 days.')

@Mocker(kw='requests_mock')
def test_handle_3(**kwargs):
  mock = _setup_handle_and_return_mock(kwargs)

  cch = CoinCoinHandler()
  cch.handle(_build_event(''), 'test_name_3')

  request_call_history = mock.request_history
  assert len(request_call_history) == 3

  first_call = request_call_history[0]
  assert first_call.url == API_REQUEST_STRING_1

  second_call = request_call_history[1]
  assert second_call.url == API_REQUEST_STRING_2

  third_call = request_call_history[2]
  assert third_call.url == POST_MESSAGE_URL
  slack_request_data = loads(third_call.text)
  assert slack_request_data['channel'] == TEST_CHANNEL
  assert slack_request_data['thread_ts'] == TEST_MESSAGE_ID
  assert slack_request_data['text'] == 'Cryptocurrency test_name_3 is worth $0.12. Its value has changed -0.06%% in the last 7 days.'

@Mocker(kw='requests_mock')
def test_handle_not_found(**kwargs):
  mock = _setup_handle_and_return_mock(kwargs)

  cch = CoinCoinHandler()
  cch.handle(_build_event(''), 'test_name_not_found')

  request_call_history = mock.request_history
  assert len(request_call_history) == 4

  slack_request_data = loads(request_call_history[-1].text)
  assert slack_request_data['text'] == 'Sorry, I couldn\'t find any cryptocurrency named test_name_not_found'

def _assertionsForSingleCall(mock, output_string):
  request_call_history = mock.request_history
  assert len(request_call_history) == 2

  first_call = request_call_history[0]
  assert first_call.url == API_REQUEST_STRING_1

  second_call = request_call_history[1]
  assert second_call.url == POST_MESSAGE_URL
  slack_request_data = loads(second_call.text)
  assert slack_request_data['channel'] == TEST_CHANNEL
  assert slack_request_data['thread_ts'] == TEST_MESSAGE_ID
  assert slack_request_data['text'] == output_string

def _build_event(text):
  return {'event':{'text':text,'user':'U1S0XJP0W','channel':TEST_CHANNEL,'ts':TEST_MESSAGE_ID}}

def _setup_handle_and_return_mock(kwargs):
  requests_mock = kwargs['requests_mock']
  requests_mock.get(API_REQUEST_STRING_1, text=RESPONSE_1)
  requests_mock.get(API_REQUEST_STRING_2, text=RESPONSE_2)
  requests_mock.get(API_REQUEST_STRING_3, text=ERROR_RESPONSE)
  requests_mock.post(POST_MESSAGE_URL, text=dumps({'ok':True}))
  return requests_mock