# SPDX-FileCopyrightText: © 2025 Shaun Wilson
# SPDX-License-Identifier: MIT

from __future__ import annotations

import json
import logging
import re
import types
from types import NoneType
from typing import Any, Iterator, Union, TYPE_CHECKING, get_args, get_origin, get_type_hints
import unicodedata

from .ConfigurationException import ConfigurationException


class Configuration:
    """The :py:class:`~appsettings2.Configuration` class is how applications access configuration data populated by :py:class:`~appsettings2.providers.ConfigurationProvider` objects. It exposes configuration data through dynamic object attributes as well as a dictionary-like interface."""

    __key_scrub_re: re.Pattern[str] | None
    __keys: dict[str, str]
    __normalize: bool

    def __init__(self, normalize: bool = False, scrubkeys: bool = False) -> None:
        """
        Initialize *Configuration* instance.

        :param normalize: Option indicating whether or not attribute names should be normalized to upper-case on the resulting :py:class:`~appsettings2.Configuration` object, defaults to False.
        :param scrubkeys: Option indicating whether or not attribute names should be scrubbed to be compatible with the Python lexer, defaults to False.
        """
        self.__keys = {}
        self.__logger = logging.getLogger('appsettings2')
        self.__normalize = normalize
        self.__key_scrub_re = (
            None
            if not scrubkeys
            else re.compile(r'[^A-Za-z0-9_]', re.IGNORECASE | re.UNICODE)
        )

    if TYPE_CHECKING:

        def __getattr__(self, name: str) -> Any:
            """Tell type checkers that accessing any attribute returns any type."""
            ...

        def __setattr__(self, name: str, value: Any) -> None:
            """Tell type checkers that setting any attribute to any value is allowed."""
            ...

    def __delitem__(self, key: str) -> None:
        """Delete the specified configuration key."""
        key = key.upper()
        k = self.__keys.get(key)
        if k is not None:
            delattr(self, k)
            self.__keys.pop(key)

    def __getitem__(self, key: str) -> Any:
        """
        Get the configuration data associated with the specified configuration key.

        :param key: The configuration key to get data for. Supports `__` and `:` hierarchical delimiters.
        :return: The configuration data associated with `key`, otherwise raises `KeyError` if `key` was not found.
        """
        parts = key.replace(':', '__').split('__')
        o = self
        for part in parts:
            if o == self:
                k = self.__keys.get(part.upper())
                if k is None:
                    raise KeyError()
                else:
                    o = getattr(o, self.__scrub_key(k))
            else:
                o = o[part]
        return o

    def __iter__(self) -> Iterator[str]:
        """Iterate configuration keys."""
        return iter(self.__keys.values())

    def __len__(self) -> int:
        """Get the number of configuration keys."""
        return len(self.__keys)

    def __deunionize(self, t: type) -> type:
        if get_origin(t) is Union:
            t = [e for e in get_args(t) if e is not NoneType][0]
        return t

    def __recursive_bind(self, target: object, source: Configuration | dict[str, Any]) -> Any:
        if target is None:
            return None
        if hasattr(target, '__class__'):
            target_type_hints = get_type_hints(
                getattr(target, '__class__')
            )
        else:
            target_type_hints = get_type_hints(target)
        names = set(dir(target) | target_type_hints.keys())
        for aname in names:
            if aname.startswith('_'):
                continue
            lval = None if not hasattr(
                target, aname) else getattr(target, aname)
            if isinstance(lval, (types.FunctionType, types.MethodType)):
                continue
            ahint = target_type_hints.get(aname)
            rval = source.get(aname)
            if ahint is None:
                # attr has no type hints, attempt to treat as a property
                prop = getattr(type(target), aname)
                if hasattr(prop, 'fget') and getattr(prop, 'fget') is not None:
                    try:
                        lval = getattr(target, aname)
                    except AttributeError:
                        lval = None
                        self.__logger.debug(
                            f'Failed to bind {aname}', exc_info=True)
                if (not hasattr(prop, 'fset') or getattr(prop, 'fset') is None):
                    # NOTE: lval is not settable
                    if rval is None:
                        # no assigment attempt will be made
                        continue
                    elif lval is not None:
                        if rval is not None and lval == rval:
                            # same value, no need to assign
                            continue
                        elif not (issubclass(type(lval), list) and issubclass(type(rval), list)):
                            # non-list values cannot be merged
                            raise Exception(
                                f'Cannot bind `None` to attribute `{aname}`')
                phints = get_type_hints(getattr(prop, 'fget'))
                if phints is None:
                    # NOTE: can't get hints from getter, can't bind
                    continue
                ahint = phints.get('return')
                if ahint is None:
                    # NOTE: fget hint missing return spec, can't bind
                    continue
            if rval is None:
                setattr(target, aname, None)
            elif ahint is float:
                setattr(target, aname, float(rval))
            elif ahint is int:
                setattr(target, aname, int(rval))
            elif ahint is str:
                setattr(target, aname, str(rval))
            elif isinstance(rval, Configuration):
                if get_origin(ahint) is dict:
                    lval = rval.to_dict()
                    setattr(target, aname, lval)
                else:
                    if lval is None:
                        ahint = self.__deunionize(ahint)
                        lval = ahint()
                        setattr(target, aname, lval)
                    self.__recursive_bind(lval, rval)
            elif get_origin(ahint) is list:
                element_type = ahint.__args__[0]
                if lval is None:
                    ahint = self.__deunionize(ahint)
                    lval = ahint()
                    setattr(target, aname, lval)
                for e in rval:
                    lval.append(
                        self.__recursive_bind_type(element_type, e)
                    )
            elif get_origin(ahint) is set:
                element_type = ahint.__args__[0]
                if lval is None:
                    ahint = self.__deunionize(ahint)
                    lval = ahint()
                    setattr(target, aname, lval)
                for e in rval:
                    lval.add(
                        self.__recursive_bind_type(element_type, e)
                    )
            else:
                setattr(target, aname, rval)
        return target

    def __recursive_bind_type(self, element_type: type, source: Any) -> Any:
        if isinstance(source, element_type):
            return source
        elif element_type is float:
            return float(source)
        elif element_type is int:
            return int(source)
        elif element_type is str:
            return str(source)
        elif isinstance(source, (Configuration, dict)):
            v = element_type()
            return self.__recursive_bind(v, source)
        else:
            raise ConfigurationException(
                f'Recursive bind to type `{element_type}` from `{type(source)}` is not supported.')

    def __scrub_key(self, key: str) -> str:
        """Scrubs a key for use as an attribute/identifier according to the Python lexer/standard."""
        key = key.replace(':', '__').replace('.', '_')
        return key if self.__key_scrub_re is None else self.__key_scrub_re.sub(
            self.__scrub_uc,
            unicodedata.normalize(
                'NFKC',
                key))

    def __scrub_uc(self, m: re.Match[str]) -> str:
        match unicodedata.category(m[0]):
            case 'Lu' | 'Ll' | 'Lt' | 'Lm' | 'Lo' | 'Nl' | 'Mn' | 'Mc' | 'Nd' | 'Pc':
                return m[0]
            case _:
                return '_'

    def __setitem__(self, key: str, value: Any) -> None:
        """Set configuration key to specified *value*."""
        self.set(key, value)

    def __str__(self) -> str:
        """Render the configuration as a JSON string."""
        return json.dumps(self.to_dict(), indent=None, ensure_ascii=False)

    def bind(self, target: object, key: str | None = None) -> Any:
        """
        Binds the configuration values into the target object.

        Can optionally specify a configuration key to bind from.

        :param target: The object to bind configuration data into.
        :param key: An optional confguration key to bind to, defaults to None which binds to the configuration root.
        :return: The original `target` object, modified in-place.
        """
        if target is None:
            raise ConfigurationException('Missing required argument: target')
        if key is None:
            return self.__recursive_bind(target, self)
        else:
            source = self.get(key)
            if source is not None:
                source_type = type(source)
                if source_type is Configuration or source_type is dict:
                    return self.__recursive_bind(target, source)
                else:
                    raise ConfigurationException(
                        f'Bind of source type `{type(source)}` is not supported.')
            return target

    def clear(self) -> None:
        """Clear all configuration data."""
        while len(self.__keys) > 0:
            t = self.__keys.popitem()
            delattr(self, t[1])

    @staticmethod
    def from_dict(source: dict[str, Any], normalize: bool = False, scrubkeys: bool = False) -> 'Configuration':
        """
        Construct a :py:class:`~appsettings2.Configuration` instance from the supplied dictionary `source`.

        :param source: The dictionary object to populate from.
        :param normalize: Option indicating whether or not attribute names should be normalized to upper-case on the resulting :py:class:`~appsettings2.Configuration` object, defaults to False.
        :param scrubkeys: Option indicating whether or not attribute names should be scrubbed to be compatible with the Python lexer, defaults to False.
        :return: A :py:class:`~appsettings2.Configuration` object derived from the `source` parameter.
        """
        config: Configuration = Configuration(
            normalize=normalize, scrubkeys=scrubkeys)
        for kvp in source.items():
            v = kvp[1]
            if issubclass(type(v), dict):
                v = Configuration.from_dict(
                    v, normalize=normalize, scrubkeys=scrubkeys)
            config.set(kvp[0], v)
        return config

    fromDictionary = from_dict  # noqa: N815
    """⚠️ DEPRECATED: use ``from_dict(...)`` instead."""

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get the configuration data associated with the specified `key`.

        :param key: The configuration key to get data for. Supports `__` and `:` hierarchical delimiters.
        :param default: The value to be returned if `key` does not exist, defaults to None
        :return: The configuration data associated with `key`, otherwise `default`.
        """
        parts = key.replace(':', '__').split('__')
        o = self
        for part in parts:
            if o == self:
                k = self.__keys.get(part.upper())
                if k is None:
                    return default
                else:
                    o = getattr(o, self.__scrub_key(k))
            else:
                o = o.get(part, default)
        return o

    def has_key(self, key: str) -> bool:
        """Check for a specific configuration key."""
        return self.__keys.get(key.upper()) is not None

    def items(self) -> list[tuple[str, Any]]:
        """Get all key-value pairs as individal ``tuple`` items."""
        it = []
        for k in self.keys():
            v = self.get(k)
            it.append((k, v))
        return it

    def keys(self) -> list[str]:
        """Get a list of all configuration keys."""
        return list(self.__keys.values())

    def pop(self, key: str) -> Any:
        """Delete a specific configuration key."""
        value = self[key]
        del self[key]
        return value

    def set(self, key: str, value: Any) -> None:
        """
        Set the configuration value for a configuration key.

        :param key: The *key* to associate the configuration *value*.
        :param value: The *value* to be associated with the configuration *key*.
        """
        if self.__normalize:
            key = key.upper()
        parts = key.replace(':', '__').split('__')
        o = self
        for i in range(len(parts) - 1):
            if o == self:
                k = self.__keys.get(parts[i].upper())
                if k is None:
                    c = Configuration(normalize=self.__normalize, scrubkeys=(
                        self.__key_scrub_re is None))
                    setattr(o, self.__scrub_key(parts[i]), c)
                    self.__keys[parts[i].upper()] = parts[i]
                    o = c
                else:
                    o = getattr(self, self.__scrub_key(k))
            else:
                if not o.has_key(parts[i]):
                    c = Configuration(normalize=self.__normalize, scrubkeys=(
                        self.__key_scrub_re is None))
                    o.set(parts[i], c)
                    o = c
                else:
                    o = o.get(parts[i])
        vtype = type(value)
        if issubclass(vtype, dict):
            value = Configuration.from_dict(
                value, normalize=self.__normalize, scrubkeys=self.__key_scrub_re is not None)
        elif issubclass(vtype, list):
            l: list[Any] = list[Any]()
            for e in value:
                if issubclass(type(e), dict):
                    l.append(Configuration.from_dict(
                        e, normalize=self.__normalize, scrubkeys=self.__key_scrub_re is not None))
                else:
                    l.append(e)
            value = l
        key = parts[-1]
        if o == self:
            k = self.__keys.get(key.upper())
            if k is not None:
                setattr(self, self.__scrub_key(k), value)
            else:
                self.__keys[key.upper()] = key
                setattr(self, self.__scrub_key(key), value)
        else:
            o.set(key, value)

    def to_dict(self) -> dict[str, Any]:
        """
        Create a dictionary from the `Configuration` object.

        :return: A dictionary containing all keys and their associated values, in a structure that mimics the structure if the data contained within the `Configuration` object.
        """
        result = dict[str, Any]()
        for k in self.__keys.values():
            v = getattr(self, self.__scrub_key(k))
            if isinstance(v, Configuration):
                result[k] = v.to_dict()
            elif issubclass(type(v), list):
                tmp = []
                for e in v:
                    if isinstance(e, Configuration):
                        tmp.append(e.to_dict())
                    else:
                        tmp.append(e)
                result[k] = tmp
            else:
                result[k] = v
        return result

    toDictionary = to_dict  # noqa: N815
    """⚠️ DEPRECATED: use ``to_dict(...)`` instead."""

    def values(self) -> list[Any]:
        """Get a list of all configuration values."""
        values = []
        for k in self.__keys.values():
            v = getattr(self, self.__scrub_key(k))
            values.append(v)
        return values
