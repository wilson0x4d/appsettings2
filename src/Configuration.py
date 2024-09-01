# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT

from . import ConfigurationException
import json
import types
from typing import Any, TypeAlias, get_type_hints

any:TypeAlias = Any

class Configuration:
    """A configuration class which creates a layer of indirection between configuration providers and configuration consumers."""

    __normalize:bool
    __len:int = 0

    def __init__(self, *, normalize:bool = False):
        """By default keys are ingest as-is, pass `True` for `normalize` to normalize kets to lower case."""
        self.__normalize = normalize

    def __str__(self) -> str:
        d:dict = self.toDictionary()
        return json.dumps(d)

    def __getitem__(self, key:str) -> any:
        if not hasattr(self, key):
            raise KeyError()
        else:
            return self.get(key)

    def __iter__(self):
        return iter(self.keys())

    def __len__(self) -> int:
        return self.__len

    def __setitem__(self, key:str, value:any) -> None:
        self.set(key, value)

    def __delitem__(self, key:str) -> None:
        if hasattr(self, key):
            delattr(self, key)
            self.__len -= 1

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
                    # naive behavior
                    setattr(target, aname, rval)
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
        for k in self.keys():
            delattr(self, k)
            self.__len -= 1

    def get(self, key:str, default:any = None) -> any:
        """Gets the configuration element associated with the specified key."""
        if self.__normalize:
            key = key.lower()
        parts = key.replace('__', '.').replace(':', '.').split('.')
        o = self
        for part in parts:
            if not hasattr(o, part):
                return default
            o = getattr(o, part)
        return o

    def has_key(self, key:str) -> bool:
        return hasattr(self, key)

    def items(self) -> list[tuple[str,any]]:
        it = []
        for k in dir(self):
            if k.startswith('_'):
                continue
            v = getattr(self, k)
            if isinstance(v, types.FunctionType) or isinstance(v, types.MethodType):
                continue
            it.append((k, v))
        return it

    def keys(self) -> list[str]:
        keys = []
        for k in dir(self):
            if k.startswith('_'):
                continue
            v = getattr(self, k)
            if isinstance(v, types.FunctionType) or isinstance(v, types.MethodType):
                continue
            keys.append(k)
        return keys

    def pop(self, key:str) -> any:
        value = self[key]
        del self[key]
        return value

    def set(self, key:str, value:any) -> None:
        """Sets the configuration element for the specified key."""
        if self.__normalize:
            key = key.lower()
        parts = key.replace('__', '.').replace(':', '.').split('.')
        o = self
        for i in range(len(parts) - 1):
            if not hasattr(o, parts[i]):
                c = Configuration(normalize=self.__normalize)
                o.set(parts[i], c)
                o = c
            else:
                o = getattr(o, parts[i])
        if o == self:
            if hasattr(o, parts[-1]):
                delattr(o, parts[-1])
            else:
                self.__len += 1
            setattr(self, parts[-1], value)
        else:
            o.set(parts[-1], value)

    def toDictionary(self) -> dict:
        """Projects a dictionary from the configuration object."""
        result = {}
        for aname in dir(self):
            if aname.startswith('_'):
                continue
            aval = getattr(self, aname)
            if isinstance(aval, types.FunctionType) or isinstance(aval, types.MethodType):
                continue
            if isinstance(aval, Configuration):
                aval = aval.toDictionary()
            result[aname] = aval
        return result

    def values(self) -> list[any]:
        values = []
        for k in dir(self):
            if k.startswith('_'):
                continue
            v = getattr(self, k)
            if isinstance(v, types.FunctionType) or isinstance(v, types.MethodType):
                continue
            values.append(v)
        return values
