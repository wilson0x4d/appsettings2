# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT

from . import ConfigurationException
import json
import types
from typing import Any, TypeAlias, get_type_hints

any:TypeAlias = Any

class Configuration:
    """A configuration class which creates a layer of indirection between configuration providers and configuration consumers."""

    __keys:dict[str, str]
    __normalize:bool

    def __init__(self, *, normalize:bool = False):
        """By default keys are ingest as-is, pass `True` for `normalize` to normalize kets to lower case."""
        self.__keys = {}
        self.__normalize = normalize

    def __delitem__(self, key:str) -> None:
        key = key.upper()
        k = self.__keys.get(key)
        if k != None:
            delattr(self, k)
            self.__keys.pop(key)

    def __getitem__(self, key:str) -> any:
        parts = key.replace('__', '.').replace(':', '.').split('.')
        o = self
        for part in parts:
            if o == self:
                k = self.__keys.get(part.upper())
                if k == None:
                    raise KeyError()
                else:
                    o = getattr(o, k)
            else:
                o = o[part]
        return o

    def __iter__(self):
        return iter(self.__keys.values())

    def __len__(self) -> int:
        return len(self.__keys)

    def __recursiveBind(self, target:object, source:'Configuration') -> any:
        targetTypeHints = get_type_hints(target)
        for aname in dir(target):
            if aname.startswith('_'):
                continue
            lval = getattr(target, aname)
            if isinstance(lval, types.FunctionType) or isinstance(lval, types.MethodType):
                continue
            ahint = targetTypeHints.get(aname)
            ahintstr = str(ahint)
            rval = source.get(aname)
            if isinstance(rval, Configuration):
                if ahint is dict or ahintstr.startswith('dict['):
                    lval = rval.toDictionary()
                    setattr(target, aname, lval)
                elif ahint is list or ahintstr.startswith('list['):
                    raise ConfigurationException(f'lval ({ahint!r}) is incompatible with rval (Configuration)')
                else:
                    if lval == None:
                        lval = ahint()
                        setattr(target, aname, lval)
                    self.__recursiveBind(lval, rval)
            elif rval != None:
                if ahint is float:
                    v = float(rval)
                    setattr(target, aname, v)
                elif ahint is int:
                    v = int(rval)
                    setattr(target, aname, v)
                elif ahint is str:
                    v = str(rval)
                    setattr(target, aname, v)
                else:
                    # naive behavior
                    setattr(target, aname, rval)
            else:
                setattr(target, aname, None)
        return target


    def __setitem__(self, key:str, value:any) -> None:
        self.set(key, value)

    def __str__(self) -> str:
        return json.dumps(self.toDictionary())

    def bind(self, target:object, key:str|None = None) -> any:
        """Binds the configuration values into the target object.
        
        Can optionally specify a configuration key to bind from."""
        if not target:
            raise ConfigurationException('Missing required argument: target')
        if key == None:
            return self.__recursiveBind(target, self)
        else:
            return self.__recursiveBind(target, self.get(key))

    def clear(self) -> None:
        while len(self.__keys) > 0:
            t = self.__keys.popitem()
            delattr(self, t[1])

    def get(self, key:str, default:any = None) -> any:
        """Gets the configuration element associated with the specified key."""
        parts = key.replace('__', '.').replace(':', '.').split('.')
        o = self
        for part in parts:
            if o == self:
                k = self.__keys.get(part.upper())
                if k == None:
                    return default
                else:
                    o = getattr(o, k)
            else:
                o = o.get(part, default)
        return o

    def has_key(self, key:str) -> bool:
        return self.__keys.get(key.upper()) != None

    def items(self) -> list[tuple[str,any]]:
        it = []
        for k in self.keys():
            v = self.get(k)
            it.append((k, v))
        return it

    def keys(self) -> list[str]:
        return self.__keys.values()

    def pop(self, key:str) -> any:
        value = self[key]
        del self[key]
        return value

    def set(self, key:str, value:any) -> None:
        """Sets the configuration element for the specified key."""
        if self.__normalize:
            key = key.upper()
        parts = key.replace('__', '.').replace(':', '.').split('.')
        o = self
        for i in range(len(parts) - 1):
            if o == self:
                k = self.__keys.get(parts[i].upper())
                if k == None:
                    c = Configuration(normalize=self.__normalize)
                    setattr(o, parts[i], c)
                    self.__keys[parts[i].upper()] = parts[i]
                    o = c
                else:
                    o = getattr(self, k)
            else:
                if not o.has_key(parts[i]):
                    c = Configuration(normalize=self.__normalize)
                    o.set(parts[i], c)
                    o = c
                else:
                    o = o.get(parts[i])
        key = parts[-1]
        if o == self:
            k = self.__keys.get(key.upper())
            if k != None:
                setattr(self, k, value)
            else:
                self.__keys[key.upper()] = key
                setattr(self, key, value)
        else:
            o.set(key, value)

    def toDictionary(self) -> dict:
        """Projects a dictionary from the configuration object."""
        result = {}
        for k in self.__keys.values():
            v = getattr(self, k)
            if isinstance(v, Configuration):
                result[k] = v.toDictionary()
            else:
                result[k] = v
        return result

    def values(self) -> list[any]:
        values = []
        for k in self.__keys.values():
            v = getattr(self, k)
            values.append(v)
        return values
