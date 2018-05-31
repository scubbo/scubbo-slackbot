# -*- coding: utf-8 -*-
import requests_mock

from lib.UpcomingProductsHandler import UpcomingProductsHandler
from tests.fixtures import Fixtures


class TestUpcomingProductsHandler:
    def test_can_handle(self):
        uph = UpcomingProductsHandler()
        assert uph.can_handle(Fixtures.event('!upcoming')) == (True, None)
        bad_commands = [
            '!upcoming ',
            ' !upcoming',
            'upcoming',
            '! upcoming',
            '/upcoming',
            '\\upcoming',
            '!products'
        ]
        for cmd in bad_commands:
            assert uph.can_handle(Fixtures.event(cmd)) == (False, None)

    def test_get_products(self):
        uph = UpcomingProductsHandler()
        mock_html = Fixtures.upcoming_products_html()
        with requests_mock.Mocker() as m:
            m.get(uph.upcoming_url, text=mock_html)
            table = uph.get_products()
        expected_table = (
            '```\n'
            '+Upcoming Products---+------------------+-------------------------------+-------+\n'
            '| Product            | Status           | Type                          | MSRP  |\n'
            '+--------------------+------------------+-------------------------------+-------+\n'
            '| Kampala Ascendent  | Shipping Now     | Kitara Cycle - Data Packs     | 14.95 |\n'
            '| Revised Core Set   | Shipping Now     | Android: Netrunner Core Set   | 39.95 |\n'
            '| Reign and Reverie  | At the Printer   | Deluxe Expansions             | 29.95 |\n'
            '| Order and Chaos    | Awaiting Reprint | Deluxe Expansions             | 29.95 |\n'
            '| Chrome City        | Awaiting Reprint | The SanSan Cycle – Data Packs | 14.95 |\n'
            '| Old Hollywood      | Awaiting Reprint | The SanSan Cycle – Data Packs | 14.95 |\n'
            '| Honor and Profit   | Awaiting Reprint | Deluxe Expansions             | 29.95 |\n'
            '| The Underway       | Awaiting Reprint | The SanSan Cycle – Data Packs | 14.95 |\n'
            '+--------------------+------------------+-------------------------------+-------+\n'
            '```'
        )
        assert table == expected_table
