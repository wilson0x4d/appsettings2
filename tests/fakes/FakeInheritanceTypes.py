# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT

class FakeSuperClass:
    first:str

class FakeSubClass(FakeSuperClass):
    second:str

class FakeSubSubClass(FakeSubClass):
    third:str
