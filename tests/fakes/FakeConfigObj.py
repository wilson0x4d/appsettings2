# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT

import typing

FakeConfigObj = typing.ForwardRef('FakeConfigObj')

class FakeConfigObj:

    test_argv:int = None
    env_test:int = None
    some_float:float = None
    some_int:int = None
    some_list:list = None
    some_string:str = None
    some_subobj:FakeConfigObj = None

    def fn1(self):
        return -1

    def fn2(self) -> int:
        return -2

    async def fn3(self):
        return -3

    def fn4(self):
        yield -4

# why? https://github.com/python/typing/issues/797
typing.get_type_hints(FakeConfigObj)