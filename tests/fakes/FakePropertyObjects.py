# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT

class FakeKeyValuePropPair:

    __key:str = None
    __value:list = None

    @property
    def key(self) -> str:
        return self.__key
    
    @key.setter
    def key(self, value:str) -> str:
        self.__key = value
    
    @property
    def value(self) -> list[int]:
        return self.__value

    @value.setter
    def value(self, value:str) -> list[int]:
        self.__value = value

class FakeUninitializedSettablePropObject:

    __keyValuePairs:list[FakeKeyValuePropPair]

    @property
    def keyValuePairs(self) -> list[FakeKeyValuePropPair]:
        return self.__keyValuePairs

    @keyValuePairs.setter
    def keyValuePairs(self, value:list[FakeKeyValuePropPair]) -> list[FakeKeyValuePropPair]:
        self.__keyValuePairs = value

class FakeInitializedNonSettablePropObject:

    __keyValuePairs:list[FakeKeyValuePropPair] = []

    @property
    def keyValuePairs(self) -> list[FakeKeyValuePropPair]:
        return self.__keyValuePairs

    @property
    def validity(self) -> bool:
        return False
