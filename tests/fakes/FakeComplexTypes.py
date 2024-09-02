# SPDX-FileCopyrightText: © 2024 Shaun Wilson
# SPDX-License-Identifier: MIT

class FakeKeyValuePair:
    key:str = None
    value:str = None

class FakeComplexObject:
    keyValuePairs:list[FakeKeyValuePair] = None
