# SPDX-FileCopyrightText: © 2025 Shaun Wilson
# SPDX-License-Identifier: MIT


class FakeKeyValuePair:

    key: str
    value: str


class FakeComplexObject:

    key_value_pairs: list[FakeKeyValuePair]
