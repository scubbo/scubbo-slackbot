# -*- coding: utf-8 -*-
import json
import os

from bs4 import BeautifulSoup
import requests
from terminaltables import AsciiTable

from lib.slackClient import SlackClient


class UpcomingProductsHandler(object):

    def __init__(self):
        self.SC = SlackClient(os.environ['responseToken'])

    def can_handle(self, event):
        return (event['event']['text'].lower() == '!upcoming', None)

    def handle(self, event, match_context):
        channel = event['event']['channel']
        self.SC.send_message(channel, self.get_products())

    def get_products(self):
        r = requests.get('https://www.fantasyflightgames.com/en/upcoming/')
        soup = BeautifulSoup(r.text, 'html.parser')
        scripts = soup.find_all('script')
        upcoming_data_script = [
            s for s in scripts if 'upcoming_data =' in str(s)]
        upcoming_products = json.loads(str(upcoming_data_script[0]).split('\n')[
                                       1].split('upcoming_data =')[1].split(';')[0])
        upcoming_anr_products = [d for d in upcoming_products if d[
            'root_collection'] == 'Android: Netrunner The Card Game']
        headers = ['Product', 'Status', 'Type', 'MSRP']
        rows = [[p['product'], p['name'], p['collection'], str(p['price'])] for p in upcoming_anr_products]
        table_data = [headers] + rows
        table = AsciiTable(table_data, 'Upcoming Products').table
        preformatted_table = '```\n' + table + '\n```'
        return preformatted_table

def get_products():
    r = requests.get('https://www.fantasyflightgames.com/en/upcoming/')
    soup = BeautifulSoup(r.text, 'html.parser')
    scripts = soup.find_all('script')
    upcoming_data_script = [
        s for s in scripts if 'upcoming_data =' in str(s)]
    upcoming_products = json.loads(str(upcoming_data_script[0]).split('\n')[
                                   1].split('upcoming_data =')[1].split(';')[0])
    upcoming_anr_products = [d for d in upcoming_products if d[
        'root_collection'] == 'Android: Netrunner The Card Game']
    headers = ['Product', 'Status', 'Type', 'MSRP']
    rows = [[p['product'], p['name'], p['collection'], str(p['price'])] for p in upcoming_anr_products]
    table_data = [headers] + rows
    table = AsciiTable(table_data, 'Upcoming Products').table
    preformatted_table = '```\n' + table + '\n```'
    return preformatted_table

if __name__ == '__main__':
    print(get_products())
