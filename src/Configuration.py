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

    def __init__(self, *, normalize:bool = False):
        """By default keys are ingest as-is, pass `True` for `normalize` to normalize kets to lower case."""
        self.__normalize = normalize

    def __str__(self) -> str:
        d:dict = self.toDictionary()
        return json.dumps(d)
    
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

    def set(self, key:str, value:any) -> None:
        """Sets the configuration element for the specified key."""
        if self.__normalize:
            key = key.lower()
        parts = key.replace('__', '.').replace(':', '.').split('.')
        o = self
        for i in range(len(parts) - 1):
            if not hasattr(o, parts[i]):
                setattr(o, parts[i], Configuration(normalize=self.__normalize))
            o = getattr(o, parts[i])
        if hasattr(o, parts[-1]):
            delattr(o, parts[-1])
        setattr(o, parts[-1], value)

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
