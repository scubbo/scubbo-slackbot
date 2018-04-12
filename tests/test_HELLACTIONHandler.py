import os
from unittest.mock import patch, mock_open
import requests
from requests_mock import Mocker
from json import dumps, loads
from lib.HELLACTIONHandler import HELLACTIONHandler

REACT_URL = 'https://slack.com/api/reactions.add'

TEST_RESPONSE_TOKEN = 'test-response-token'
TEST_CHANNEL = 'test-channel'
TEST_MESSAGE_ID = 'test-message-id'

os.environ['responseToken'] = TEST_RESPONSE_TOKEN

def test_can_handle(**kwargs):
  nch = HELLACTIONHandler()
  assert nch.can_handle({'event':{'text':'hell action'}})[0]
  assert nch.can_handle({'event':{'text':'HELLACTION'}})[0]
  assert nch.can_handle({'event':{'text':'HeLl-AcTiOn'}})[0]
  assert nch.can_handle({'event':{'text':'Foo hell action bar'}})[0]
  assert nch.can_handle({'event':{'text':'Hella action'}})[0] == False

@Mocker(kw='requests_mock')
def test_handle(**kwargs):
  requests_mock = kwargs['requests_mock']
  requests_mock.post(REACT_URL, text=dumps({'ok':True}))
  nch = HELLACTIONHandler()
  nch.handle({'event':{'channel':TEST_CHANNEL,'ts':TEST_MESSAGE_ID}}, None)

  requests_call_history = requests_mock.request_history
  # 1 to get ALL_CARDS, 2 to get card image, 3 to send message
  assert len(requests_call_history) == 1
  slack_request = requests_call_history[0]
  assert slack_request.url == REACT_URL
  assert slack_request.headers['Content-Type'] == 'application/json; charset=utf-8'
  assert slack_request.headers['Authorization'] == 'Bearer ' + TEST_RESPONSE_TOKEN

  slack_request_data = loads(slack_request.text)
  assert slack_request_data['channel'] == TEST_CHANNEL
  assert slack_request_data['timestamp'] == TEST_MESSAGE_ID
  assert slack_request_data['name'] == 'fire'