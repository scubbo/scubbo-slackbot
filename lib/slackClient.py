import json
import requests
import types

class DebugPrintDecorator(object):
  def __init__(self, f):
    self.f = f

  def __call__(self, *args, **kwargs):
    response = json.loads(self.f(*args, **kwargs).text)
    if not response['ok']:
      print 'Error calling ' + self.f.__name__ + ' with args ' + str(args) + ' and kwargs ' + str(kwargs) + ': ' + str(response)

  # https://stackoverflow.com/questions/30104047/how-can-i-decorate-an-instance-method-with-a-decorator-class
  def __get__(self, instance, owner):
    return types.MethodType(self, instance, owner)

class SlackClient:

  POST_MESSAGE_URL = 'https://slack.com/api/chat.postMessage'

  def __init__(self, token):
    self.headers = {
      'Content-Type': 'application/json; charset=utf-8',
      'Authorization': 'Bearer ' + token
    }

  @DebugPrintDecorator
  def send_message(self, channel, message):
    '''Arguably, this (and the attachments version, below) could have delegated to their appropriate threaded version if it contained logic to only set the thread_ts if present. But I wanted the signatures to clearly demonstrate intended usage'''
    data = {
      'text': message,
      'channel': channel
    }
    return self._post_to_post_message(data)

  @DebugPrintDecorator
  def send_threaded_reply(self, channel, parent_message_id, message):
    data = {
      'text': message,
      'channel': channel,
      'thread_ts': parent_message_id
    }
    return self._post_to_post_message(data)

  @DebugPrintDecorator
  def send_attachments(self, channel, attachments, message=None):
    '''Attachment spec is here: https://api.slack.com/docs/message-attachments#attachment_structure. Note we also accept a single attachment and do not require it to be wrapped in a singleton list'''
    if type(attachments) == types.DictType:
      attachments = [attachments]
    data = {
      'channel': channel,
      'attachments': []
    }
    if message:
      data['text'] = message
    for attachment in attachments:
      data['attachments'].append(attachment)
    return self._post_to_post_message(data)

  @DebugPrintDecorator
  def send_attachments_threaded_reply(self, channel, parent_message_id, attachments, message=None):
    '''Attachment spec is here: https://api.slack.com/docs/message-attachments#attachment_structure. Note we also accept a single attachment and do not require it to be wrapped in a singleton list'''
    if type(attachments) == types.DictType:
      attachments = [attachments]
    data = {
      'channel': channel,
      'thread_ts': parent_message_id,
      'attachments': []
    }
    if message:
      data['text'] = message
    for attachment in attachments:
      data['attachments'].append(attachment)
    return self._post_to_post_message(data)

  def _post_to_post_message(self, data):
    return requests.post(self.POST_MESSAGE_URL, json.dumps(data), headers = self.headers)
