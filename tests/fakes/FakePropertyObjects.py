# SPDX-FileCopyrightText: © 2025 Shaun Wilson
# SPDX-License-Identifier: MIT


class FakeKeyValuePropPair:

    __key:str
    __value:list

    @property
    def key(self) -> str:
        return self.__key
    
    @key.setter
    def key(self, value:str) -> None:
        self.__key = value
    
    @property
    def value(self) -> list[int]:
        return self.__value

    @value.setter
    def value(self, value:list[int]) -> None:
        self.__value = value


class FakeUninitializedSettablePropObject:

    __keyValuePairs:list[FakeKeyValuePropPair]

    @property
    def keyValuePairs(self) -> list[FakeKeyValuePropPair]:
        return self.__keyValuePairs

    @keyValuePairs.setter
    def keyValuePairs(self, value:list[FakeKeyValuePropPair]) -> None:
        self.__keyValuePairs = value


class FakeInitializedNonSettablePropObject:

    __keyValuePairs:list[FakeKeyValuePropPair]

    def __init__(self) -> None:
        self.__keyValuePairs = []

    @property
    def keyValuePairs(self) -> list[FakeKeyValuePropPair]:
        return self.__keyValuePairs

    @property
    def validity(self) -> bool:
        return False
