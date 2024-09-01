# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT

from fakes import *
import json
import os
import src as appsettings2
import unittest

class ConfigurationTests(unittest.TestCase):

    def test_CanWriteDunderKeys(self):
        config = appsettings2.Configuration()
        config.set('THIS__IS_A__TEST', 5)
        self.assertEqual(5, config.THIS.IS_A.TEST)

    def test_CanReadDunderKeys(self):
        config = appsettings2.Configuration()
        config.set('THIS__IS_A__TEST', 5)
        v = config.get('THIS__IS_A__TEST')
        self.assertEqual(5, v)

    def test_CanWriteColonKeys(self):
        config = appsettings2.Configuration()
        config.set('THIS:IS_A:TEST', 5)
        self.assertEqual(5, config.THIS.IS_A.TEST)

    def test_CanReadColonKeys(self):
        config = appsettings2.Configuration()
        config.set('THIS:IS_A:TEST', 5)
        v = config.get('THIS:IS_A:TEST')
        self.assertEqual(5, v)

    def test_CanWritePeriodKeys(self):
        config = appsettings2.Configuration()
        config.set('THIS.IS_A.TEST', 5)
        self.assertEqual(5, config.THIS.IS_A.TEST)

    def test_CanReadPeriodKeys(self):
        config = appsettings2.Configuration()
        config.set('THIS.IS_A.TEST', 5)
        v = config.get('THIS.IS_A.TEST')
        self.assertEqual(5, v)

    def test_CanReadWriteMixedKeys(self):
        config = appsettings2.Configuration()
        config.set('THIS:IS_A.TEST', 5)
        v = config.get('THIS.IS_A__TEST')
        self.assertEqual(5, v)
        self.assertEqual(5, config.THIS.IS_A.TEST)

    def test_IsDictionaryLike(self):
        config = appsettings2.Configuration()
        self.assertRaises(KeyError, config.__getitem__, 'test')
        # confirm basic key-value semantics
        config['test'] = '123'
        self.assertEqual('123', config.test)
        config.test = None
        self.assertIsNone(None, config.test)
        # confirm keys(), values()
        config.test = 234
        self.assertEqual(234, config['test'])
        self.assertEqual(1, len(config.keys()))
        self.assertEqual(1, len(config.values()))
        # confirm items()
        items = config.items()
        self.assertEqual(1, len(items))
        self.assertEqual('test', items[0][0])
        self.assertEqual(234, items[0][1])
        # confirm len()
        self.assertEqual(1, len(config))
        config['test2'] = 34.5
        self.assertEqual(2, len(config))
        self.assertEqual(34.5, config.test2)
        # confirm del syntax, and has_key()
        self.assertTrue(config.has_key('test2'))
        del config['test2']
        self.assertEqual(1, len(config))
        self.assertFalse(config.has_key('test2'))
        # confirm pop()
        config['test3'] = 4.5
        config['test4'] = '5'
        self.assertEqual(4.5, config.test3)
        self.assertEqual('5', config.test4)
        self.assertEqual(4.5, config.pop('test3'))
        self.assertFalse(config.has_key('test3'))
        self.assertEqual(2, len(config))
        # confirm iterable
        config.clear()
        self.assertEqual(0, len(config))
        for e in config:
            self.fail('unexpected iterable item')
        config.set('foo', 'bar')
        for e in config:
            self.assertEqual('foo', e)
            self.assertEqual('bar', config[e])
        # implementation detail: confirm hierarchical keys
        # result in the expected hierarchical state.
        config.clear()
        config['test__hierarchy'] = 1
        self.assertIsNotNone(config['test'])
        self.assertIsNotNone(config['test']['hierarchy'])
        self.assertEqual(appsettings2.Configuration, type(config['test']))
        self.assertEqual(1, len(config['test']))
        self.assertEqual(1, config['test']['hierarchy'])

    def test_ToDictionary_MustSucceed(self):
        config = appsettings2.Configuration()
        config.set('THIS:IS_A.TEST1', 1)
        config.set('THIS:IS_A.TEST2', 2.2)
        config.set('THIS:IS_A.TEST3', "3")
        d = config.toDictionary()
        self.assertIsNotNone(d)

    def __getSubsetConfiguration(self):
        # "subset configurations" are a set of
        # configurations which each configure a subset
        # of the entire config, and are meant to be
        # used to do a broad verification that 
        # all providers work as intended when added
        # to the builder.
        builder = appsettings2.ConfigurationBuilder(normalize=True)
        builder.addProvider(appsettings2.providers.CommandLineConfigurationProvider([
            'TEST_ARGV=5',
            'some_subobj__TEST_ARGV=6'
        ]))
        os.environ['env_test'] = '7'
        os.environ['some_subobj__env_test'] = '8'
        builder.addProvider(appsettings2.providers.EnvironmentConfigurationProvider())
        builder.addProvider(appsettings2.providers.JsonConfigurationProvider(filepath='tests/configs/subset.json'))
        builder.addProvider(appsettings2.providers.TomlConfigurationProvider(filepath='tests/configs/subset.toml'))
        builder.addProvider(appsettings2.providers.YamlConfigurationProvider(filepath='tests/configs/subset.yaml'))
        configuration = builder.build()
        self.assertIsNotNone(configuration)
        self.assertEqual(1, configuration.get('some_float'))
        self.assertEqual('rand2', configuration.get('some_subobj:some_string'))
        self.assertEqual(3, configuration.get('some_int'))
        self.assertEqual(3.4, configuration.get('some_subobj:some_float'))
        self.assertEqual('rand4', configuration.get('some_string'))
        self.assertEqual(4, configuration.get('some_subobj:some_int'))
        self.assertEqual('5', configuration.get('TEST_ARGV'))
        self.assertEqual('6', configuration.get('some_subobj__TEST_ARGV'))
        self.assertEqual('7', configuration.get('env_test'))
        self.assertEqual('8', configuration.get('some_subobj__env_test'))
        return configuration

    def test_WithSubsets_ToDictionary_MustSerialize(self):
        configuration = self.__getSubsetConfiguration()
        d = configuration.toDictionary()
        self.assertIsNotNone(d)
        s = json.dumps(d)
        self.assertIsNotNone(s)

    def test_WithSubsets_MustBind(self):
        configuration = self.__getSubsetConfiguration()
        obj = FakeConfigObj()
        o = configuration.bind(obj)
        self.assertEqual(o, obj)
        self.assertEqual(1, obj.some_float)
        self.assertEqual('rand2', obj.some_subobj.some_string)
        self.assertEqual(3, obj.some_int)
        self.assertEqual(3.4, obj.some_subobj.some_float)
        self.assertEqual('rand4', obj.some_string)
        self.assertEqual(4, obj.some_subobj.some_int)
        self.assertEqual(5, obj.test_argv)
        self.assertEqual(6, obj.some_subobj.test_argv)
        self.assertEqual(7, obj.env_test)
        self.assertEqual(8, obj.some_subobj.env_test)
 