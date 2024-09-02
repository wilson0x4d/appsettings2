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
 
    def test_AttributesPreserveCase_ProvidesCaseInsensitiveAccess(self):
        configuration = appsettings2.Configuration()
        # confirm that keys are case-insensitive
        configuration.set('UPPER_CASE_KEY', 1)
        configuration.set('lower_case_key', 2)
        configuration.set('mIxEd_cAsE_KeY', 3)
        # confirm upper case keys function in a case-insensitive manner
        self.assertTrue(configuration.has_key('UPPER_CASE_KEY'))
        self.assertTrue(configuration.has_key('upper_case_key'))
        self.assertTrue(configuration.has_key('uPpEr_CasE_keY'))
        self.assertTrue(configuration.has_key('LOWER_CASE_KEY'))
        self.assertTrue(configuration.has_key('lower_case_key'))
        self.assertTrue(configuration.has_key('lOWeR_CasE_keY'))
        self.assertTrue(configuration.has_key('MIXED_CASE_KEY'))
        self.assertTrue(configuration.has_key('mixed_case_key'))
        self.assertTrue(configuration.has_key('mIxED_CasE_keY'))
        # confirm that object attributes preserve the original casing
        self.assertTrue(hasattr(configuration, 'UPPER_CASE_KEY'))
        self.assertFalse(hasattr(configuration, 'upper_case_key'))
        self.assertEqual(1, configuration.UPPER_CASE_KEY)
        self.assertTrue(hasattr(configuration, 'lower_case_key'))
        self.assertFalse(hasattr(configuration, 'LOWER_CASE_KEY'))
        self.assertEqual(2, configuration.lower_case_key)
        self.assertTrue(hasattr(configuration, 'mIxEd_cAsE_KeY'))
        self.assertFalse(hasattr(configuration, 'mixed_case_key'))
        self.assertEqual(3, configuration.mIxEd_cAsE_KeY)
        # confirm that data can be accessed in a case-insensitive manner
        self.assertEqual(1, configuration['UPPER_CASE_KEY'])
        self.assertEqual(1, configuration.get('UPPER_CASE_KEY'))
        self.assertEqual(1, configuration['uPPeR_cASe_KeY'])
        self.assertEqual(1, configuration.get('uPPeR_cASe_KeY'))
        self.assertEqual(2, configuration['LOWER_CASE_KEY'])
        self.assertEqual(2, configuration.get('LOWER_CASE_KEY'))
        self.assertEqual(2, configuration['LOWer_cASe_KeY'])
        self.assertEqual(2, configuration.get('lOWeR_cASe_KeY'))
        self.assertEqual(3, configuration['MIXED_CASE_KEY'])
        self.assertEqual(3, configuration.get('MIXED_CASE_KEY'))
        self.assertEqual(3, configuration['mixEd_cASe_KeY'])
        self.assertEqual(3, configuration.get('MixeD_cASe_KeY'))

    def test_NormalizeOptionForcesUpperCase_StillProvidesCaseInsensitiveAccess(self):
        configuration = appsettings2.Configuration(normalize=True)
        # confirm that keys are case-insensitive
        configuration.set('UPPER_CASE_KEY', 1)
        configuration.set('lower_case_key', 2)
        configuration.set('mIxEd_cAsE_KeY', 3)
        # confirm normalized keys function in a case-insensitive manner
        self.assertTrue(configuration.has_key('UPPER_CASE_KEY'))
        self.assertTrue(configuration.has_key('upper_case_key'))
        self.assertTrue(configuration.has_key('uPpEr_CasE_keY'))
        self.assertTrue(configuration.has_key('LOWER_CASE_KEY'))
        self.assertTrue(configuration.has_key('lower_case_key'))
        self.assertTrue(configuration.has_key('lOWeR_CasE_keY'))
        self.assertTrue(configuration.has_key('MIXED_CASE_KEY'))
        self.assertTrue(configuration.has_key('mixed_case_key'))
        self.assertTrue(configuration.has_key('mIxED_CasE_keY'))
        # confirm that object attributes have normalized casing
        self.assertTrue(hasattr(configuration, 'UPPER_CASE_KEY'))
        self.assertFalse(hasattr(configuration, 'upper_case_key'))
        self.assertEqual(1, configuration.UPPER_CASE_KEY)
        self.assertTrue(hasattr(configuration, 'LOWER_CASE_KEY'))
        self.assertFalse(hasattr(configuration, 'lower_case_key'))
        self.assertEqual(2, configuration.LOWER_CASE_KEY)
        self.assertTrue(hasattr(configuration, 'MIXED_CASE_KEY'))
        self.assertFalse(hasattr(configuration, 'mIxEd_cAsE_KeY'))
        self.assertEqual(3, configuration.MIXED_CASE_KEY)
        # confirm that data can be accessed in a case-insensitive manner
        self.assertEqual(1, configuration['UPPER_CASE_KEY'])
        self.assertEqual(1, configuration.get('UPPER_CASE_KEY'))
        self.assertEqual(1, configuration['uPPeR_cASe_KeY'])
        self.assertEqual(1, configuration.get('uPPeR_cASe_KeY'))
        self.assertEqual(2, configuration['LOWER_CASE_KEY'])
        self.assertEqual(2, configuration.get('LOWER_CASE_KEY'))
        self.assertEqual(2, configuration['LOWer_cASe_KeY'])
        self.assertEqual(2, configuration.get('lOWeR_cASe_KeY'))
        self.assertEqual(3, configuration['MIXED_CASE_KEY'])
        self.assertEqual(3, configuration.get('MIXED_CASE_KEY'))
        self.assertEqual(3, configuration['mixEd_cASe_KeY'])
        self.assertEqual(3, configuration.get('MixeD_cASe_KeY'))

    def test_ScrubkeysOptionGeneratesLexerFriendlyAttributes(self):
        configuration = appsettings2.Configuration(scrubkeys=True)
        configuration.set('basic#verification', 1)
        # confirm keys are accessible under their original name
        self.assertEqual(1, configuration['basic#verification'])
        self.assertEqual(1, configuration.get('basic#verification'))
        # confirm lexer-friendly attribute name is used
        self.assertEqual(1, configuration.basic_verification)
        # and a sanity check that we can do this in reverse
        configuration.basic_verification = 2
        self.assertEqual(2, configuration['basic#verification'])
        self.assertEqual(2, configuration.get('basic#verification'))

    def test_SupportsTypedLists(self):
        provider = appsettings2.providers.JsonConfigurationProvider(
            json="""
            {
                "keyValuePairs": [
                    {
                        "key": "key1",
                        "value": "value1"
                    },
                    {
                        "key": "key2",
                        "value": "value2"
                    }
                ]
            }""")
        configuration = appsettings2.Configuration()
        provider.populateConfiguration(configuration)
        complexObject:FakeComplexObject = FakeComplexObject()
        configuration.bind(complexObject)
        self.assertIsNotNone(complexObject)
        self.assertIsNotNone(complexObject.keyValuePairs)
        self.assertEqual(2, len(complexObject.keyValuePairs))
        i = 0
        for e in complexObject.keyValuePairs:
            i += 1
            self.assertIsInstance(e, FakeKeyValuePair)
            self.assertEqual(f'key{i}', e.key)
            self.assertEqual(f'value{i}', e.value)
