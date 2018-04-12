import os
from unittest.mock import patch, mock_open
import requests
from requests_mock import Mocker
from json import dumps, loads
from lib.NetrunnerCardHandler import NetrunnerCardHandler

CARDS_URL = 'https://netrunnerdb.com/api/2.0/public/cards'
CARDS_URL_RESPONSE = dumps({'data':[{'title': 'test card name one', 'code': '1'}]})
CARD_URL_PREFIX = 'https://netrunnerdb.com/api/2.0/public/card/'
TITLE_FROM_CARD_DATA = 'test-title-from-card-data'
TEXT_FROM_CARD_DATA = 'test-<strong>text</strong>'
TEXT_FROM_CARD_DATA_PARSED = 'test-*text*'
CARD_IMAGE_URL = 'http://card-image-url'
CARD_DATA_RESPONSE = dumps({'data':[{'image_url':CARD_IMAGE_URL,'title':TITLE_FROM_CARD_DATA,'text':TEXT_FROM_CARD_DATA}]})
CARD_DATA_RESPONSE_WITHOUT_IMAGE_URL = dumps({'imageUrlTemplate':'abc{code}def', 'data':[{'title':TITLE_FROM_CARD_DATA,'text':TEXT_FROM_CARD_DATA}]})
POST_MESSAGE_URL = 'https://slack.com/api/chat.postMessage'

TEST_RESPONSE_TOKEN = 'test-response-token'
TEST_CHANNEL = 'test-channel'
TEST_MESSAGE_ID = 'test-message-id'

os.environ['responseToken'] = TEST_RESPONSE_TOKEN

@Mocker(kw='requests_mock')
def test_can_handle(**kwargs):
  kwargs['requests_mock'].get(CARDS_URL, text=CARDS_URL_RESPONSE)
  nch = NetrunnerCardHandler()
  assert nch.can_handle({'event':{'text':'[[test card name one]]'}})[0]
  assert nch.can_handle({'event':{'text':'[[test card name foo]]'}})[0] == False
  assert nch.can_handle({'event':{'text':'no square brackets'}})[0] == False
  assert nch.can_handle({'event':{'text':'[[test card name one]]','channel':u'C4WF0612L'}})[0] == False
  assert nch.can_handle({'event':{'text':'[[test card name one]]','channel':u'C4WF0612M'}})[0]

@Mocker(kw='requests_mock')
def test_handle(**kwargs):
  requests_mock = kwargs['requests_mock']
  requests_mock.get(CARDS_URL, text=CARDS_URL_RESPONSE)
  requests_mock.get(CARD_URL_PREFIX+'01', text=CARD_DATA_RESPONSE)
  requests_mock.post(POST_MESSAGE_URL, text=dumps({'ok':True}))
  nch = NetrunnerCardHandler()
  nch.handle({'event':{'channel':TEST_CHANNEL,'ts':TEST_MESSAGE_ID}}, {'cards':[{'code':'01','title':TITLE_FROM_CARD_DATA}]})

  requests_call_history = requests_mock.request_history
  # 1 to get ALL_CARDS, 2 to get card image, 3 to send message
  assert len(requests_call_history) == 3
  slack_request = requests_call_history[-1]
  assert slack_request.url == POST_MESSAGE_URL
  assert slack_request.headers['Content-Type'] == 'application/json; charset=utf-8'
  assert slack_request.headers['Authorization'] == 'Bearer ' + TEST_RESPONSE_TOKEN

  slack_request_data = loads(slack_request.text)
  assert slack_request_data['channel'] == TEST_CHANNEL
  assert slack_request_data['thread_ts'] == TEST_MESSAGE_ID
  assert len(slack_request_data['attachments']) == 1
  assert slack_request_data['attachments'][0]['image_url'] == CARD_IMAGE_URL
  assert slack_request_data['attachments'][0]['title'] == TITLE_FROM_CARD_DATA

@Mocker(kw='requests_mock')
def test_card_without_image_url(**kwargs):
  requests_mock = kwargs['requests_mock']
  requests_mock.get(CARDS_URL, text=CARDS_URL_RESPONSE)
  requests_mock.get(CARD_URL_PREFIX+'01', text=CARD_DATA_RESPONSE_WITHOUT_IMAGE_URL)
  requests_mock.post(POST_MESSAGE_URL, text=dumps({'ok':True}))
  nch = NetrunnerCardHandler()
  nch.handle({'event':{'channel':TEST_CHANNEL,'ts':TEST_MESSAGE_ID}}, {'cards':[{'code':'01','title':TITLE_FROM_CARD_DATA}]})

  requests_call_history = requests_mock.request_history
  assert len(requests_call_history) == 3
  slack_request = requests_call_history[-1]
  slack_request_data = loads(slack_request.text)
  assert slack_request_data['attachments'][0]['image_url'] == 'abc01def'
  assert slack_request_data['attachments'][0]['fields'][0]['value'] == TEXT_FROM_CARD_DATA_PARSED

