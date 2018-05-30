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


