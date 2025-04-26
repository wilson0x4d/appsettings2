# SPDX-FileCopyrightText: Copyright (C) Shaun Wilson
# SPDX-License-Identifier: MIT

class FakeKeyValuePair:
    key:str
    value:str

class FakeComplexObject:
    keyValuePairs:list[FakeKeyValuePair]
