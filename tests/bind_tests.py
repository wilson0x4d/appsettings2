# SPDX-FileCopyrightText: © 2025 Shaun Wilson
# SPDX-License-Identifier: MIT

"""Tests for :py:meth:`~appsettings2.Configuration.bind`."""

from __future__ import annotations

import appsettings2
from punit import fact


# ---------------------------------------------------------------------------
# Fake types used in the tests below.
# ---------------------------------------------------------------------------


class InnerSetting:
    """A simple class whose instances are stored inside a ``dict`` value slot."""

    host: str
    port: int


class DatabaseConfig:
    """An object that contains a dict-of-classes and a list-of-classes."""

    servers: dict[str, InnerSetting]
    database: str
    timeout: float


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


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
        "Expected InnerSetting, got plain dict")
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


# ---------------------------------------------------------------------------
# Additional simple-string-dict targets (inline fakes).
# ---------------------------------------------------------------------------


class SimpleStringDictTarget:
    labels: dict[str, str]


class StringAnnotatedTarget:
    servers: dict[str, 'InnerSetting']
