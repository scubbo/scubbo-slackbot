# -*- coding: utf-8 -*-
import json
import os

from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont
import requests

from slackClient import SlackClient


class UpcomingProductHandler(object):

    def __init__(self):
        self.SC = SlackClient(os.environ['responseToken'])

    def can_handle(self, event):
        return event['event']['text'].lower() == '!upcoming'

    def handle(self, event, match_context):
        channel = event['event']['channel']
        message_id = event['event']['ts']
        attachment = {
            'mrkdwn_in': ['fields'],
            'fields': [
                {
                    'value': None  # TODO: make this the formatted upcoming ANR products
                }
            ]
        }
        self.SC.send_attachments_threaded_reply(
            channel, message_id, attachment)

    def format_product(self, product_dict):
        keys = ['product', 'name', 'collection', 'price']
        return ' | '.join(str(v) for k, v in product_dict.items() if k in keys)

    def get_products(self):
        r = requests.get('https://www.fantasyflightgames.com/en/upcoming/')
        soup = BeautifulSoup(r.text, 'html.parser')
        # products = soup.find_all('div', class_='upcoming-upper')
        scripts = soup.find_all('script')
        upcoming_data_script = [
            s for s in scripts if 'upcoming_data =' in str(s)]
        upcoming_products = json.loads(str(upcoming_data_script[0]).split('\n')[
                                       1].split('upcoming_data =')[1].split(';')[0])
        upcoming_anr_products = [d for d in upcoming_products if d[
            'root_collection'] == 'Android: Netrunner The Card Game']
        headers = ['Product | Status | Type | MSRP']
        rows = [format_product(p) for p in upcoming_anr_products]
        table = '\n'.join(headers + rows)
        return table

    def gen_image(self):
        # make sure you have the fonts locally in a fonts/ directory
        georgia_bold = 'fonts/georgia_bold.ttf'
        georgia_bold_italic = 'fonts/georgia_bold_italic.ttf'

        # W, H = (1280, 720) # image size
        W, H = (720, 405) # image size
        txt = 'Hello Petar this is my test image' # text to render
        background = (0,164,201) # white
        fontsize = 35
        font = ImageFont.truetype(georgia_bold_italic, fontsize)

        image = Image.new('RGBA', (W, H), background)
        draw = ImageDraw.Draw(image)

        # w, h = draw.textsize(txt) # not that accurate in getting font size
        w, h = font.getsize(txt)

        draw.text(((W-w)/2,(H-h)/2), txt, fill='white', font=font)
        # draw.text((10, 0), txt, (0,0,0), font=font)
        # img_resized = image.resize((188,45), Image.ANTIALIAS)

        save_location = os.getcwd()

        # img_resized.save(save_location + '/sample.jpg')
        image.save(save_location + '/sample.png')