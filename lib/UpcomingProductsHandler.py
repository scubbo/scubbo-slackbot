# -*- coding: utf-8 -*-
import json
import os
import re

from bs4 import BeautifulSoup
import requests
from terminaltables import AsciiTable

from lib.slackClient import SlackClient


class UpcomingProductsHandler(object):

    def __init__(self):
        self.upcoming_url = 'https://www.fantasyflightgames.com/en/upcoming/'
        self.SC = SlackClient(os.environ['responseToken'])

    def can_handle(self, event):
        return (event['event']['text'].lower() == '!upcoming', None)

    def handle(self, event, match_context):
        channel = event['event']['channel']
        self.SC.send_message(channel, self.get_products())

    def get_products(self):
        r = requests.get(self.upcoming_url)
        soup = BeautifulSoup(r.text, 'html.parser')
        scripts = soup.find_all('script')

        for script in scripts:
            script = str(script)
            if 'upcoming_data =' in script:
                upcoming_data_script = script

        upcoming_products = re.findall(
            r'upcoming_data = (.*\]);',
            upcoming_data_script
        )[0]

        upcoming_anr_products = []
        for product in json.loads(upcoming_products):
            if product['root_collection'] == 'Android: Netrunner The Card Game':
                upcoming_anr_products.append(product)

        headers = ['Product', 'Status', 'Type', 'MSRP']
        rows = [[p['product'], p['name'], p['collection'],
                 str(p['price'])] for p in upcoming_anr_products]
        table_data = [headers] + rows
        table = AsciiTable(table_data, 'Upcoming Products').table
        preformatted_table = '```\n' + table + '\n```'
        return preformatted_table
