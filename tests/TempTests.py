import unittest

from src import *
from src.providers import *

def get_configuration() -> Configuration:
    return ConfigurationBuilder(normalize=True)\
        .addProvider(JsonConfigurationProvider(f'appsettings.json', required=False))\
        .addProvider(JsonConfigurationProvider(f'appsettings.Development.json', required=False))\
        .addProvider(EnvironmentConfigurationProvider())\
        .build()

class TempTests(unittest.TestCase):
    def test_temp(self):
        configuration = get_configuration()
        self.assertIsNotNone(configuration)