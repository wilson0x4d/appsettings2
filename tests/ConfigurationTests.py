# SPDX-FileCopyrightText: Copyright (C) Shaun Wilson
# SPDX-License-Identifier: MIT

import appsettings2
import json
import os
from punit import *

from tests.fakes.FakeConfigObj import FakeConfigObj
from tests.fakes.FakeComplexTypes import FakeComplexObject, FakeKeyValuePair
from tests.fakes.FakeInheritanceTypes import FakeSubSubClass
from tests.fakes.FakePropertyObjects import FakeInitializedNonSettablePropObject, FakeKeyValuePropPair, FakeUninitializedSettablePropObject

class ConfigurationTests:

    @fact
    def test_CanWriteDunderKeys(self):
        config = appsettings2.Configuration()
        config.set('THIS__IS_A__TEST', 5)
        assert 5 == config.THIS.IS_A.TEST

    @fact
    def test_CanReadDunderKeys(self):
        config = appsettings2.Configuration()
        config.set('THIS__IS_A__TEST', 5)
        v = config.get('THIS__IS_A__TEST')
        assert 5 == v

    @fact
    def test_CanWriteColonKeys(self):
        config = appsettings2.Configuration()
        config.set('THIS:IS_A:TEST', 5)
        assert 5 == config.THIS.IS_A.TEST

    @fact
    def test_CanReadColonKeys(self):
        config = appsettings2.Configuration()
        config.set('THIS:IS_A:TEST', 5)
        v = config.get('THIS:IS_A:TEST')
        assert 5 == v

    @fact
    def test_CanWritePeriodKeys(self):
        config = appsettings2.Configuration()
        config.set('THIS.IS_A.TEST', 5)
        assert 5 == config.THIS_IS_A_TEST

    @fact
    def test_CanReadPeriodKeys(self):
        config = appsettings2.Configuration()
        config.set('THIS.IS_A.TEST', 5)
        v = config.get('THIS.IS_A.TEST')
        assert 5 == v

    @fact
    def test_CanReadWriteMixedKeys(self):
        config = appsettings2.Configuration()
        config.set('THIS:IS_A.TEST', 5)
        v = config.get('THIS__IS_A.TEST')
        assert 5 == v
        assert 5 == config.THIS.IS_A_TEST

    @fact
    def test_IsDictionaryLike(self):
        config = appsettings2.Configuration()
        exceptions.raises[KeyError](lambda: config['test'])
        # confirm basic key-value semantics
        config['test'] = '123'
        assert '123' == config.test
        config.test = None
        assert config.test is None
        # confirm keys(), values()
        config.test = 234
        assert 234 == config['test']
        assert 1 == len(config.keys())
        assert 1 == len(config.values())
        # confirm items()
        items = config.items()
        assert 1 == len(items)
        assert 'test' == items[0][0]
        assert 234 == items[0][1]
        # confirm len()
        assert 1 == len(config)
        config['test2'] = 34.5
        assert 2 == len(config)
        assert 34.5 == config.test2
        # confirm del syntax, and has_key()
        assert config.has_key('test2')
        del config['test2']
        assert 1 == len(config)
        assert not config.has_key('test2')
        # confirm pop()
        config['test3'] = 4.5
        config['test4'] = '5'
        assert 4.5 == config.test3
        assert '5' == config.test4
        assert 4.5 == config.pop('test3')
        assert not config.has_key('test3')
        assert 2 == len(config)
        # confirm iterable
        config.clear()
        assert 0 == len(config)
        for e in config:
            assert False, 'unexpected iterable item'
        config.set('foo', 'bar')
        for e in config:
            assert 'foo' == e
            assert 'bar' == config[e]
        # implementation detail: confirm hierarchical keys
        # result in the expected hierarchical state.
        config.clear()
        config['test__hierarchy'] = 1
        assert config['test'] is not None
        assert config['test']['hierarchy'] is not None
        assert appsettings2.Configuration == type(config['test'])
        assert 1 == len(config['test'])
        assert 1 == config['test']['hierarchy']

    @fact
    def test_ToDictionary_BasicVerification(self):
        config = appsettings2.Configuration()
        config.set('THIS:IS_A__TEST1', 1)
        config.set('THIS__IS_A:TEST2', 2.2)
        config.set('THIS__IS_A__TEST3', '3')
        config.set(
            'deep_list',
            [
                {
                    'key': 1,
                    'value': [ 1,2,3 ]
                },
                {
                    'key': 2,
                    'value': [ 2,3,4 ]
                },
                {
                    'key': 3,
                    'value': [ 3,4,5 ]
                },
            ]
        )
        d = config.toDictionary()
        assert d is not None
        assert 1 == config.THIS.IS_A.TEST1
        assert 2.2 == config.THIS.IS_A.TEST2
        assert '3' == config.THIS.IS_A.TEST3
        assert isinstance(config.deep_list, list)
        i = 0
        for e in config.deep_list:
            i = i + 1
            assert isinstance(e, appsettings2.Configuration)
            assert i == e.key
            assert isinstance(e.value, list)
            for k in range(3):
                assert i+k == e.value[k]


    @fact
    def test_FromDictionary_BasicVerification(self):
        expected = {
            'this': {
                'is_a': {
                    'test1': 1,
                    'test2': 2.2,
                    'test3': '3'
                }
            },
            'deep_list': [
                {
                    'key': 1,
                    'value': [ 1,2,3 ]
                },
                {
                    'key': 2,
                    'value': [ 2,3,4 ]
                },
                {
                    'key': 3,
                    'value': [ 3,4,5 ]
                },
            ]
        }
        config = appsettings2.Configuration.fromDictionary(expected)
        assert isinstance(config, appsettings2.Configuration)
        assert isinstance(config.this, appsettings2.Configuration)
        assert isinstance(config.this.is_a, appsettings2.Configuration)
        assert 1 == config.this.is_a.test1
        assert 2.2 == config.this.is_a.test2
        assert '3' == config.this.is_a.test3
        assert isinstance(config.deep_list, list)
        i = 0
        for e in config.deep_list:
            i = i + 1
            assert isinstance(e, appsettings2.Configuration)
            assert i == e.key
            assert isinstance(e.value, list)
            for k in range(3):
                assert i+k == e.value[k]
        actual = config.toDictionary()
        assert collections.areSame(expected, actual)

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
        builder.addProvider(appsettings2.providers.JsonConfigurationProvider('tests/configs/subset.json'))
        builder.addProvider(appsettings2.providers.TomlConfigurationProvider('tests/configs/subset.toml'))
        builder.addProvider(appsettings2.providers.YamlConfigurationProvider('tests/configs/subset.yaml'))
        configuration = builder.build()
        assert configuration is not None
        assert 1 == configuration.get('some_float')
        assert 'rand2' == configuration.get('some_subobj:some_string')
        assert 3 == configuration.get('some_int')
        assert 3.4 == configuration.get('some_subobj:some_float')
        assert 'rand4' == configuration.get('some_string')
        assert 4 == configuration.get('some_subobj:some_int')
        assert '5' == configuration.get('TEST_ARGV')
        assert '6' == configuration.get('some_subobj__TEST_ARGV')
        assert '7' == configuration.get('env_test')
        assert '8' == configuration.get('some_subobj__env_test')
        return configuration

    @fact
    def test_WithSubsets_ToDictionary_MustSerialize(self):
        configuration = self.__getSubsetConfiguration()
        d = configuration.toDictionary()
        assert d is not None
        s = json.dumps(d)
        assert s is not None

    @fact
    def test_WithSubsets_MustBind(self):
        configuration = self.__getSubsetConfiguration()
        obj = FakeConfigObj()
        o = configuration.bind(obj)
        assert o == obj
        assert 1, obj.some_float
        assert 'rand2', obj.some_subobj.some_string
        assert 3, obj.some_int
        assert 3.4, obj.some_subobj.some_float
        assert 'rand4', obj.some_string
        assert 4, obj.some_subobj.some_int
        assert 5, obj.test_argv
        assert 6, obj.some_subobj.test_argv
        assert 7, obj.env_test
        assert 8, obj.some_subobj.env_test
 
    @fact
    def test_AttributesPreserveCase_ProvidesCaseInsensitiveAccess(self):
        configuration = appsettings2.Configuration()
        # confirm that keys are case-insensitive
        configuration.set('UPPER_CASE_KEY', 1)
        configuration.set('lower_case_key', 2)
        configuration.set('mIxEd_cAsE_KeY', 3)
        # confirm upper case keys function in a case-insensitive manner
        assert True == (configuration.has_key('UPPER_CASE_KEY'))
        assert True == (configuration.has_key('upper_case_key'))
        assert True == (configuration.has_key('uPpEr_CasE_keY'))
        assert True == (configuration.has_key('LOWER_CASE_KEY'))
        assert True == (configuration.has_key('lower_case_key'))
        assert True == (configuration.has_key('lOWeR_CasE_keY'))
        assert True == (configuration.has_key('MIXED_CASE_KEY'))
        assert True == (configuration.has_key('mixed_case_key'))
        assert True == (configuration.has_key('mIxED_CasE_keY'))
        # confirm that object attributes preserve the original casing
        assert True == (hasattr(configuration, 'UPPER_CASE_KEY'))
        assert False == (hasattr(configuration, 'upper_case_key'))
        assert 1 == configuration.UPPER_CASE_KEY
        assert True == (hasattr(configuration, 'lower_case_key'))
        assert False == (hasattr(configuration, 'LOWER_CASE_KEY'))
        assert 2 == configuration.lower_case_key
        assert True == (hasattr(configuration, 'mIxEd_cAsE_KeY'))
        assert False == (hasattr(configuration, 'mixed_case_key'))
        assert 3 == configuration.mIxEd_cAsE_KeY
        # confirm that data can be accessed in a case-insensitive manner
        assert 1 == configuration['UPPER_CASE_KEY']
        assert 1 == configuration.get('UPPER_CASE_KEY')
        assert 1 == configuration['uPPeR_cASe_KeY']
        assert 1 == configuration.get('uPPeR_cASe_KeY')
        assert 2 == configuration['LOWER_CASE_KEY']
        assert 2 == configuration.get('LOWER_CASE_KEY')
        assert 2 == configuration['LOWer_cASe_KeY']
        assert 2 == configuration.get('lOWeR_cASe_KeY')
        assert 3 == configuration['MIXED_CASE_KEY']
        assert 3 == configuration.get('MIXED_CASE_KEY')
        assert 3 == configuration['mixEd_cASe_KeY']
        assert 3 == configuration.get('MixeD_cASe_KeY')

    @fact
    def test_NormalizeOptionForcesUpperCase_StillProvidesCaseInsensitiveAccess(self):
        configuration = appsettings2.Configuration(normalize=True)
        # confirm that keys are case-insensitive
        configuration.set('UPPER_CASE_KEY', 1)
        configuration.set('lower_case_key', 2)
        configuration.set('mIxEd_cAsE_KeY', 3)
        # confirm normalized keys function in a case-insensitive manner
        assert True == (configuration.has_key('UPPER_CASE_KEY'))
        assert True == (configuration.has_key('upper_case_key'))
        assert True == (configuration.has_key('uPpEr_CasE_keY'))
        assert True == (configuration.has_key('LOWER_CASE_KEY'))
        assert True == (configuration.has_key('lower_case_key'))
        assert True == (configuration.has_key('lOWeR_CasE_keY'))
        assert True == (configuration.has_key('MIXED_CASE_KEY'))
        assert True == (configuration.has_key('mixed_case_key'))
        assert True == (configuration.has_key('mIxED_CasE_keY'))
        # confirm that object attributes have normalized casing
        assert True == (hasattr(configuration, 'UPPER_CASE_KEY'))
        assert False == (hasattr(configuration, 'upper_case_key'))
        assert 1 == configuration.UPPER_CASE_KEY
        assert True == (hasattr(configuration, 'LOWER_CASE_KEY'))
        assert False == (hasattr(configuration, 'lower_case_key'))
        assert 2 == configuration.LOWER_CASE_KEY
        assert True == (hasattr(configuration, 'MIXED_CASE_KEY'))
        assert False == (hasattr(configuration, 'mIxEd_cAsE_KeY'))
        assert 3 == configuration.MIXED_CASE_KEY
        # confirm that data can be accessed in a case-insensitive manner
        assert 1 == configuration['UPPER_CASE_KEY']
        assert 1 == configuration.get('UPPER_CASE_KEY')
        assert 1 == configuration['uPPeR_cASe_KeY']
        assert 1 == configuration.get('uPPeR_cASe_KeY')
        assert 2 == configuration['LOWER_CASE_KEY']
        assert 2 == configuration.get('LOWER_CASE_KEY')
        assert 2 == configuration['LOWer_cASe_KeY']
        assert 2 == configuration.get('lOWeR_cASe_KeY')
        assert 3 == configuration['MIXED_CASE_KEY']
        assert 3 == configuration.get('MIXED_CASE_KEY')
        assert 3 == configuration['mixEd_cASe_KeY']
        assert 3 == configuration.get('MixeD_cASe_KeY')

    @fact
    def test_ScrubkeysOptionGeneratesLexerFriendlyAttributes(self):
        configuration = appsettings2.Configuration(scrubkeys=True)
        configuration.set('basic#verification', 1)
        # confirm keys are accessible under their original name
        assert 1 == configuration['basic#verification']
        assert 1 == configuration.get('basic#verification')
        # confirm lexer-friendly attribute name is used
        assert 1 == configuration.basic_verification
        # and a sanity check that we can do this in reverse
        configuration.basic_verification = 2
        assert 2 == configuration['basic#verification']
        assert 2 == configuration.get('basic#verification')

    @fact
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
        assert complexObject is not None
        assert complexObject.keyValuePairs is not None
        assert 2 == len(complexObject.keyValuePairs)
        i = 0
        for e in complexObject.keyValuePairs:
            i += 1
            assert isinstance(e, FakeKeyValuePair)
            assert f'key{i}' == e.key
            assert f'value{i}' == e.value

    @fact
    def test_SupportsUninitializedSettablePropertyBinding(self):
        config = appsettings2.Configuration()
        config.set(
            'keyValuePairs',
            [
                {
                    'key': 1,
                    'value': [ 1,2,3 ]
                },
                {
                    'key': 2,
                    'value': [ 2,3,4 ]
                },
                {
                    'key': 3,
                    'value': [ 3,4,5 ]
                },
            ]
        )
        obj:FakeUninitializedSettablePropObject = config.bind(FakeUninitializedSettablePropObject())
        assert obj.keyValuePairs is not None
        assert 3 == len(obj.keyValuePairs)
        i = 0
        for e in obj.keyValuePairs:
            i = i + 1
            assert isinstance(e, FakeKeyValuePropPair)
            assert str(i) == e.key
            for k in range(3):
                assert i+k == e.value[k]

    @fact
    def test_MergesInitializedNonSettablePropertyBindingWhenSourceValueIsList(self):
        config = appsettings2.Configuration()
        config.set(
            'keyValuePairs',
            [
                {
                    'key': 1,
                    'value': [ 1,2,3 ]
                },
                {
                    'key': 2,
                    'value': [ 2,3,4 ]
                },
                {
                    'key': 3,
                    'value': [ 3,4,5 ]
                },
            ]
        )
        fake = FakeInitializedNonSettablePropObject()
        obj:FakeInitializedNonSettablePropObject = config.bind(fake)
        assert obj.keyValuePairs is not None
        assert 3 == len(obj.keyValuePairs)
        i = 0
        for e in obj.keyValuePairs:
            i = i + 1
            assert isinstance(e, FakeKeyValuePropPair)
            assert str(i) == e.key
            for k in range(3):
                assert i+k == e.value[k]

    @fact
    def test_FailsInitializedNonSettablePropertyBindingWhenSourceValueIsNonNull(self):
        config = appsettings2.Configuration()
        config.set(
            'validity',
            True
        )
        fake = FakeInitializedNonSettablePropObject()
        exceptions.raises[Exception](lambda: config.bind(fake))

    @fact
    def test_SkipsInitializedNonSettablePropertyBindingWithNullSourceValue(self):
        # verifies that nonsettable, pre-initialized properties do not error when the binding source contains a null value
        config = appsettings2.Configuration()
        config.set(
            'keyValuePairs',
            None
        )
        fake = FakeInitializedNonSettablePropObject()
        obj:FakeInitializedNonSettablePropObject = config.bind(fake)
        assert obj.keyValuePairs is not None
        assert 0 == len(obj.keyValuePairs)

    @fact
    def test_BindInheritedAttributes(self):
        config = appsettings2.Configuration()
        config.set('first', 1)
        config.set('second', 2)
        config.set('third', 3)
        obj = config.bind(FakeSubSubClass())
        assert obj.third is not None
        assert '3' == obj.third
        assert obj.second is not None
        assert '2' == obj.second
        assert obj.first is not None
        assert '1' == obj.first

    @fact
    def test_Bind_WhenKeyIsNone_MustSucceed(self):
        config = appsettings2.Configuration()
        expected = FakeComplexObject()
        actual = config.bind(expected, 'does_not_exist')
        assert id(expected) == id(actual)
