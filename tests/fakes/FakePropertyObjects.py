# SPDX-FileCopyrightText: © 2025 Shaun Wilson
# SPDX-License-Identifier: MIT


class FakeKeyValuePropPair:

    __key: str
    __value: list

    @property
    def key(self) -> str:
        return self.__key

    @key.setter
    def key(self, value: str) -> None:
        self.__key = value

    @property
    def value(self) -> list[int]:
        return self.__value

    @value.setter
    def value(self, value: list[int]) -> None:
        self.__value = value


class FakeUninitializedSettablePropObject:

    __key_value_pairs: list[FakeKeyValuePropPair]

    @property
    def key_value_pairs(self) -> list[FakeKeyValuePropPair]:
        return self.__key_value_pairs

    @key_value_pairs.setter
    def key_value_pairs(self, value: list[FakeKeyValuePropPair]) -> None:
        self.__key_value_pairs = value


class FakeInitializedNonSettablePropObject:

    __key_value_pairs: list[FakeKeyValuePropPair]

    def __init__(self) -> None:
        self.__key_value_pairs = []

    @property
    def key_value_pairs(self) -> list[FakeKeyValuePropPair]:
        return self.__key_value_pairs

    @property
    def validity(self) -> bool:
        return False
