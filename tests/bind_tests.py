# SPDX-FileCopyrightText: © 2025 Shaun Wilson
# SPDX-License-Identifier: MIT

"""Tests for :py:meth:`~appsettings2.Configuration.bind`."""

from __future__ import annotations

import appsettings2
from punit import fact
from typing import Any


class InnerSetting:
    """A simple class whose instances are stored inside a ``dict`` value slot."""

    host: str
    port: int


class DatabaseConfig:
    """An object that contains a dict-of-classes and a list-of-classes."""

    servers: dict[str, InnerSetting]
    database: str
    timeout: float


@fact
def bind_dict_with_class_values_rehydrates() -> None:
    """Dict[str, SomeClass] values must be rehydrated into instances, not left as plain dicts."""
    config = appsettings2.Configuration()
    config.set('servers', {
        'a': {'host': 'alpha.local', 'port': 5432},
        'b': {'host': 'beta.local', 'port': 5433},
    })
    target = DatabaseConfig()
    target.database = 'maindb'
    target.timeout = 30.0
    config.bind(target)
    assert isinstance(target.servers['a'], InnerSetting), (
        'Expected InnerSetting, got plain dict')
    assert 'alpha.local' == target.servers['a'].host
    assert 5432 == target.servers['a'].port
    assert isinstance(target.servers['b'], InnerSetting)
    assert 'beta.local' == target.servers['b'].host


@fact
def bind_uninitialized_dict_with_class_values_creates_instances() -> None:
    """When the target's dict slot is None, bind must instantiate and fill it."""
    config = appsettings2.Configuration()
    config.set('servers', {
        'primary': {'host': 'db.example.com', 'port': 3306},
    })
    target = DatabaseConfig()
    target.database = 'staging'
    target.timeout = 15.5
    config.bind(target)
    assert target.servers is not None
    assert isinstance(target.servers['primary'], InnerSetting)
    assert 'db.example.com' == target.servers['primary'].host


@fact
def bind_dict_with_primitive_values_works() -> None:
    """Dict[str, str] values must remain plain dicts (not broken)."""
    config = appsettings2.Configuration()
    config.set('labels', {'x': 'alpha', 'y': 'beta'})
    target = SimpleStringDictTarget()
    config.bind(target)
    assert target.labels is not None
    assert isinstance(target.labels, dict)
    assert 'alpha' == target.labels['x']


@fact
def bind_dict_with_class_values_via_key() -> None:
    """bind(..., key=...) must also rehydrate class values inside dicts."""
    config = appsettings2.Configuration()
    config.set('servers', {
        'prod': {'host': 'prod.db', 'port': 443},
    })
    target = DatabaseConfig()
    result = config.bind(target, key='servers')
    assert result is not None
    assert isinstance(target.servers['prod'], InnerSetting)
    assert 'prod.db' == target.servers['prod'].host


@fact
def bind_dict_with_class_values_via_nested_key() -> None:
    """bind(..., key=...) must rehydrate class values when the key references a nested Configuration."""
    # Properly nest with '__' delimiters so get(key) resolves correctly
    config = appsettings2.Configuration()
    db_config = appsettings2.Configuration()
    db_config.set('servers', {
        'prod': {'host': 'prod.db', 'port': 443},
    })
    config.set('database__servers', db_config)
    target = DatabaseConfig()
    result = config.bind(target, key='database__servers')
    assert result is not None
    assert isinstance(target.servers['prod'], InnerSetting)
    assert 'prod.db' == target.servers['prod'].host


@fact
def bind_dict_with_class_values_via_key_not_found() -> None:
    """Binding to a key that doesn't exist must return the target unchanged."""
    config = appsettings2.Configuration()
    target = DatabaseConfig()
    result = config.bind(target, key='nonexistent')
    assert result is target


@fact
def bind_dict_with_class_values_from_plain_dict_source() -> None:
    """When source itself is a plain dict (not Configuration), class values must still be rehydrated."""
    raw_source = {
        'primary': {'host': 'raw.host', 'port': 9090},
    }

    target = DatabaseConfig()
    plain_config = appsettings2.Configuration()
    plain_config._Configuration__recursive_bind(target, raw_source)  # noqa: SLF001
    assert isinstance(target.servers['primary'], InnerSetting)
    assert 'raw.host' == target.servers['primary'].host


@fact
def bind_dict_with_primitive_values_from_plain_dict_source() -> None:
    """When source is a plain dict and value type is primitive (str), no rehydration needed."""
    raw_source = {'key': 'value'}

    target = SimpleStringDictTarget()
    plain_config = appsettings2.Configuration()
    plain_config._Configuration__recursive_bind(target, raw_source)  # noqa: SLF001
    assert target.labels == {'key': 'value'}


@fact
def bind_nested_class_values_deeply() -> None:
    """Classes nested several levels deep must all be rehydrated correctly."""
    config = appsettings2.Configuration()
    config.set('servers', {
        'node1': {'host': '10.0.0.1', 'port': 9090},
    })
    target = DatabaseConfig()
    target.database = 'deepdb'
    target.timeout = 5.0
    config.bind(target)
    assert isinstance(target.servers['node1'], InnerSetting)
    assert '10.0.0.1' == target.servers['node1'].host


@fact
def bind_dict_empty_dict_value() -> None:
    """Binding an empty dict must leave the target's dict empty."""
    config = appsettings2.Configuration()
    config.set('servers', {})
    target = DatabaseConfig()
    target.database = 'emptydb'
    target.timeout = 1.0
    config.bind(target)
    assert target.servers == {}


@fact
def bind_dict_with_class_values_type_str_annotation() -> None:
    """When the type annotation is written as a string ('InnerSetting'), it must still work."""
    config = appsettings2.Configuration()
    config.set('servers', {
        'x': {'host': 'x.local', 'port': 1234},
    })
    target = StringAnnotatedTarget()
    config.bind(target)
    assert isinstance(target.servers['x'], InnerSetting)
    assert 'x.local' == target.servers['x'].host


class SimpleStringDictTarget:
    labels: dict[str, str]


class StringAnnotatedTarget:
    servers: dict[str, 'InnerSetting']


class PrimitiveTypedTarget:
    """Target with primitive-typed attrs that need conversion from underlying types."""
    port_as_float: float
    port_as_int: int
    port_as_str: str
    database_name: str
    enabled: bool


class UntypedTarget:
    """Target with an untyped (no-annotation) attribute — tests the raw-passthrough path."""

    config_value: object  # no conversion hints → falls through to else branch


class AnyTypedTarget:
    """Target with Any-typed attributes — value passes through unchanged."""

    any_value: Any


class TypedFallbackTarget:
    """Target whose hint doesn't match any explicit branch (e.g. custom type not in branches)."""

    raw_data: object  # should get raw source via else at line ~204


@fact
def bind_primitive_conversion_float_from_int() -> None:
    """float-typed attr receiving an int source must be converted."""
    config = appsettings2.Configuration()
    config.set('port_as_float', 42)  # raw int

    target = PrimitiveTypedTarget()
    config.bind(target, key='port_as_float')
    assert isinstance(target.port_as_float, float)
    assert target.port_as_float == 42.0


@fact
def bind_primitive_conversion_int_from_str() -> None:
    """int-typed attr receiving a string source must be converted."""
    config = appsettings2.Configuration()
    config.set('port_as_int', '8080')  # raw str

    target = PrimitiveTypedTarget()
    config.bind(target, key='port_as_int')
    assert isinstance(target.port_as_int, int)
    assert target.port_as_int == 8080


@fact
def bind_primitive_conversion_str_from_float() -> None:
    """str-typed attr receiving a float source must be converted."""
    config = appsettings2.Configuration()
    config.set('port_as_str', 3.14)  # raw float

    target = PrimitiveTypedTarget()
    config.bind(target, key='port_as_str')
    assert isinstance(target.port_as_str, str)
    assert target.port_as_str == '3.14'


@fact
def bind_primitive_conversion_root_float() -> None:
    """float-typed attr bound from root Configuration source must be converted."""
    config = appsettings2.Configuration()
    config.set('port_as_float', 99.5)

    target = PrimitiveTypedTarget()
    config.bind(target)
    assert isinstance(target.port_as_float, float)
    assert target.port_as_float == 99.5


@fact
def bind_primitive_conversion_root_int() -> None:
    """int-typed attr bound from root Configuration source must be converted."""
    config = appsettings2.Configuration()
    config.set('port_as_int', '420')

    target = PrimitiveTypedTarget()
    config.bind(target)
    assert isinstance(target.port_as_int, int)
    assert target.port_as_int == 420


@fact
def bind_primitive_conversion_root_str() -> None:
    """str-typed attr bound from root Configuration source must be converted."""
    config = appsettings2.Configuration()
    config.set('database_name', 12345)  # int stored in config

    target = PrimitiveTypedTarget()
    config.bind(target)
    assert isinstance(target.database_name, str)
    assert target.database_name == '12345'


@fact
def bind_primitive_bool_conversion_root() -> None:
    """bool-typed attr receiving a non-bool source must be converted."""
    config = appsettings2.Configuration()
    config.set('enabled', 1)  # int stored in config

    target = PrimitiveTypedTarget()
    config.bind(target)
    assert isinstance(target.enabled, bool)
    assert target.enabled is True


@fact
def bind_primitive_all_attrs_from_mixed_sources() -> None:
    """Multi-attr bind from mixed primitive sources must all convert correctly."""
    config = appsettings2.Configuration()
    config.set('port_as_float', '3.14')  # str → float
    config.set('port_as_int', 8080)      # int → int (no-op, but exercise path)
    config.set('port_as_str', 99.9)       # float → str
    config.set('database_name', True)     # bool → str
    config.set('enabled', 'true')         # str → ??? (bool is not in the conversion branches)

    target = PrimitiveTypedTarget()
    config.bind(target)
    assert isinstance(target.port_as_float, float)
    assert target.port_as_float == 3.14
    assert isinstance(target.port_as_int, int)
    assert target.port_as_int == 8080
    assert isinstance(target.port_as_str, str)
    assert target.port_as_str == '99.9'
    assert isinstance(target.database_name, str)
    assert target.database_name == 'True'


@fact
def bind_fallback_else_path_raw_passthrough() -> None:
    """Attribute with no matching branch hint (object) gets raw source value unchanged."""
    config = appsettings2.Configuration()
    config.set('raw_data', [1, 2, 3])  # complex object → should pass through

    target = TypedFallbackTarget()
    config.bind(target)
    assert target.raw_data == [1, 2, 3]


@fact
def bind_fallback_else_path_none_source() -> None:
    """None source with untyped attr sets the attribute to None."""
    config = appsettings2.Configuration()
    config.set('raw_data', None)

    target = TypedFallbackTarget()
    config.bind(target)
    assert target.raw_data is None


@fact
def bind_fallback_else_path_with_key() -> None:
    """bind(key=...) with an untyped attr must also fall through to else."""
    config = appsettings2.Configuration()
    config.set('raw_data', [4, 5])

    target = TypedFallbackTarget()
    config.bind(target, key='raw_data')
    assert target.raw_data == [4, 5]


class FakeNode:
    host: str
    port: int


class ListOfComplexTarget:
    nodes: list[FakeNode]


@fact
def bind_list_of_complex_from_raw_dicts() -> None:
    """list[FakeNode] must rehydrate each dict entry into a FakeNode instance."""
    config = appsettings2.Configuration()
    config.set('nodes', [
        {'host': 'alpha.local', 'port': 5432},
        {'host': 'beta.local', 'port': 5433},
    ])

    target = ListOfComplexTarget()
    config.bind(target)
    assert isinstance(target.nodes[0], FakeNode)
    assert isinstance(target.nodes[1], FakeNode)
    assert target.nodes[0].host == 'alpha.local'
    assert target.nodes[0].port == 5432


@fact
def bind_list_of_complex_via_key() -> None:
    """bind(key=...) with list of dicts must also rehydrate."""
    config = appsettings2.Configuration()
    config.set('nodes', [
        {'host': 'gamma.local', 'port': 8080},
    ])

    target = ListOfComplexTarget()
    config.bind(target, key='nodes')
    assert isinstance(target.nodes[0], FakeNode)
    assert target.nodes[0].host == 'gamma.local'


@fact
def bind_list_of_complex_empty() -> None:
    """Empty list source must produce empty list on target."""
    config = appsettings2.Configuration()
    config.set('nodes', [])

    target = ListOfComplexTarget()
    config.bind(target)
    assert target.nodes == []


class OptDictTarget:
    servers: dict[str, InnerSetting] | None


@fact
def bind_optional_dict_non_none_rehydrates() -> None:
    """Optional[dict[str, SomeClass]] with a real value must rehydrate class entries."""
    config = appsettings2.Configuration()
    config.set('servers', {
        'a': {'host': 'a.local', 'port': 1},
    })

    target = OptDictTarget()
    config.bind(target)
    assert target.servers is not None
    assert isinstance(target.servers['a'], InnerSetting)


@fact
def bind_optional_dict_none_value() -> None:
    """Optional[dict[str, SomeClass]] with None source must stay None."""
    config = appsettings2.Configuration()
    config.set('servers', None)

    target = OptDictTarget()
    config.bind(target)
    assert target.servers is None


class SingleUnionTarget:
    """When Union has one non-None member, __deunionize should pick it."""

    attr1: 'InnerSetting | str'


@fact
def bind_union_single_non_none_picks_first() -> None:
    """Union[A, B] → __deunionize picks the first non-None type (A)."""
    config = appsettings2.Configuration()
    config.set('attr1', {'host': 'x.local', 'port': 99})

    target = SingleUnionTarget()
    config.bind(target)
    assert isinstance(target.attr1, InnerSetting)


@fact
def bind_union_single_non_none_via_key_rehydrates() -> None:
    """Union[A, B] with class dict value → rehydrates as A."""
    config = appsettings2.Configuration()
    config.set('attr1', {'host': 'y.local', 'port': 99})

    target = SingleUnionTarget()
    config.bind(target, key='attr1')
    assert isinstance(target.attr1, InnerSetting)


class PreInitSettablePropTarget:
    """Target with a pre-initialized settable property."""

    _value: int = 0

    @property
    def value(self) -> int:
        return self._value

    @value.setter
    def value(self, v: int) -> None:
        self._value = v


@fact
def bind_settable_pre_init_property() -> None:
    """Pre-initialized settable property must be updated via bind."""
    config = appsettings2.Configuration()
    config.set('value', 42)

    target = PreInitSettablePropTarget()
    config.bind(target)
    assert target.value == 42


class ScrubKeyTarget:
    """Target attributes matching scrubbed/normalized key names."""

    x_foo_1: str


@fact
def bind_scrub_key_matching() -> None:
    """Scrubbed config key must match scrubbed attribute name."""
    config = appsettings2.Configuration(scrubkeys=True)
    config.set('X-foo.1', 'hello')

    target = ScrubKeyTarget()
    config.bind(target)
    assert target.x_foo_1 == 'hello'


@fact
def bind_normalize_uppercase_matching() -> None:
    """Normalized key must match normalized attribute hint."""
    config = appsettings2.Configuration(normalize=True)
    # set('X-foo.1') with normalize → key stored as 'X_FOO_1' (after scrub)
    config.set('X-foo.1', 'world')

    target = ScrubKeyTarget()
    config.bind(target)
    assert target.x_foo_1 == 'world'


@fact
def bind_nested_config_dict_class_values() -> None:
    """Nested Configuration source wrapping a dict must still rehydrate class values."""
    inner = appsettings2.Configuration()
    inner.set('host', 'nested.local')
    inner.set('port', 3000)

    config = appsettings2.Configuration()
    config.set('servers', {'inner': inner})

    target = NestedDictConfigTarget()
    config.bind(target)
    assert isinstance(target.servers['inner'], InnerSetting)
    assert target.servers['inner'].host == 'nested.local'


class NestedDictConfigTarget:
    servers: dict[str, InnerSetting]


class ListTarget:
    items: list[int]


class SetTarget:
    items: set[int]


@fact
def bind_empty_list_source() -> None:
    """Empty list source must produce empty list, not crash."""
    config = appsettings2.Configuration()
    config.set('items', [])

    target = ListTarget()
    config.bind(target)
    assert target.items == []


@fact
def bind_empty_set_source_via_list_input() -> None:
    """Empty list source bound to set[int] must produce empty set."""
    config = appsettings2.Configuration()
    config.set('items', [])

    target = SetTarget()
    config.bind(target)
    assert target.items == set()
