# SPDX-FileCopyrightText: © 2025 Shaun Wilson
# SPDX-License-Identifier: MIT

import typing


class FakeConfigObj:
    """A fake configuration object for binding tests."""

    test_argv: int
    env_test: int
    some_float: float
    some_int: int
    some_list: list
    some_string: str
    some_subobj: 'FakeConfigObj'

    def fn1(self) -> int:
        return -1

    def fn2(self) -> int:
        return -2

    async def fn3(self) -> int:
        return -3

    def fn4(self) -> typing.Generator[int, None, None]:
        yield -4


typing.get_type_hints(FakeConfigObj)  # why? https://github.com/python/typing/issues/797
