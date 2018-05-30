class Fixtures(object):

    @staticmethod
    def event(text, channel='test_channel', ts='test_message_id'):
        return {
            'event': {
                'text':text,
                'channel':channel,
                'ts':ts
            }
        }
