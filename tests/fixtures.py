class Fixtures(object):

    @staticmethod
    def event(text, channel='test_channel', ts='test_message_id'):
        return {
            'event': {
                'text': text,
                'channel': channel,
                'ts': ts
            }
        }

    @staticmethod
    def upcoming_products_html():
        with open('tests/data/ffg_upcoming.html', 'r') as f:
            mock_html = f.read()
        return mock_html
