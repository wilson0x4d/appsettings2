# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT

class FakeSuperClass:
    first:str = None

class FakeSubClass(FakeSuperClass):
    second:str = None

class FakeSubSubClass(FakeSubClass):
    third:str = None
