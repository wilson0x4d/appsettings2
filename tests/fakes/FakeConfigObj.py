# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT

import typing

FakeConfigObj = typing.ForwardRef('FakeConfigObj')

class FakeConfigObj:

    test_argv:int
    env_test:int
    some_float:float
    some_int:int
    some_list:list
    some_string:str
    some_subobj:FakeConfigObj

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