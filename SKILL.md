---
name: appsettings2
description: Configuration skill for Python. MUST load when user mentions 'app settings', 'appsettings.json', or 'appsettings2', or has questions about loading configuration from JSON, YAML, TOML, Environment Variables, or CLI args.
user-invocable: true
disable-model-invocation: false
---

# appsettings2 — AI Directive

## PRIORITY (highest → lowest)

1. **Rules** — override all other guidance when in conflict.
2. **Core API** — use these patterns for every code snippet you generate.
3. **Provider reference** — only when the user asks about custom providers.
4. Everything else is optional context; do not repeat it unless asked.

## RULES (AI — always enforce)

### Provider precedence
Providers are merged in order of addition — **last provider wins**. Missing keys in a later provider do *not* erase earlier values. Default `get_configuration()` precedence:
```
appsettings.{variation}.{json,yaml,toml}  (lowest)
CLI args
Environment variables                      (highest)
```

### Type coercion (bind rules)

| Target annotation | Coercion | Gotcha |
|-------------------|----------|--------|
| `str` | `str(value)` | — |
| `int` | `int(value)` | Non-numeric → ValueError |
| `float` | `float(value)` | — |
| `bool` | **`bool(value)`** (Python truthiness) | `'false'`, `'0'`, `'anything'` → True. Only `''`, `0`, `None` → False. No JSON-style boolean parsing. |

For JSON-style boolean parsing, bind to `str` and check explicitly: `config.get('flag') == 'true'`.

### Key access conventions
- Prefer `config.get('Key__SubKey')` — case-insensitive, supports `:` and `__` delimiters interchangeably.
- `[key]` raises `KeyError`; `get(key)` returns `default` (None). Always use defaults when a key *may* be absent.
- Chained dict access works for hierarchies: `config['ConnectionStrings']['SampleDb']`.
- Dynamic attributes preserve casing of the input: `config.get('fooBar').FooBar` (casing depends on what was set, not what you asked).

### Binding (`bind`) rules
- Returns the target object **modified in-place**; do not assign the result as if it were a clone.
- Nested dicts bind by instantiating the value-type via `__init__()` then recursing.
- `list[T]` and `set[T]`: each dict entry is rehydrated into `T()`. Plain-element lists/sets are coerced directly.
- `Union[X, None]` (i.e. `Optional[X]`): unwrap to `X`; if source key maps to a complex sub-object, instantiate `X()` and recurse.
- Case-insensitive matching: `'maxBatchSize'` in JSON → `MaxBatchSize` on target.

### normalize / scrubkeys
- `normalize=True` only affects dynamic attribute names (upper-cases them). It does *not* affect `get()`, `[key]`, or `bind()` — those remain case-insensitive regardless.
- `scrubkeys=True` transforms non-Python-identifier characters (`-`, `.`, `#`, etc.) into `_`. Can cause key collisions (`'key#1'` and `'key-1'` collide). Use only when needed.

## SKIP (AI — do not do these)

- Do not re-document `add_json`, `add_yaml`, `add_toml` signatures separately — they share the same params: `(filepath=None, string_param=None, fd=None, required=True)` where `string_param` is `json`/`yaml`/`toml`.
- Do not list the 9 default variations of `get_configuration()` in full. Say "defaults to `['', 'prod', 'production', 'stage', 'staging', 'qa', 'dev', 'development', 'local']`".
- Do not document deprecated names (`getConfiguration`, `fromDictionary`, `addJson`, etc.) unless the user explicitly references them.
- Do not re-explain provider order — covered in RULES above.
- Do not generate boilerplate imports when context already makes the import obvious.

## CORE API

### Loading config

```python
# Fluent builder (recommended)
from appsettings2 import ConfigurationBuilder
config = ConfigurationBuilder()\
    .add_json('appsettings.json')\
    .add_environment(env_prefix='APP')\  # only APP_* vars loaded
    .build()
```

### One-liner

```python
from appsettings2 import get_configuration
# basename: str | pathlib.Path · defaults to 'appsettings'
config = get_configuration(env_prefix='APP')
```

All source flags default True (json, toml, yaml, cli, environment). Set any to False to skip. `variations` are tried per-file-type as `{basename}.{variation}.{ext}` — missing files silently skipped.

### Accessing values

```python
# Recommended: .get() with optional default
db = config.get('ConnectionStrings__Primary', '')

# Existence check (avoid KeyError)
if config.has_key('EnableSwagger'): ...

# Convert entire tree to plain dict
tree = config.to_dict()
```

### Typed binding

```python
from dataclasses import dataclass

@dataclass
class AppSettings:
    EnableSwagger: bool
    MaxBatchSize: int
    ConnectionStrings: str  # or a nested config class

config = get_configuration()
settings = AppSettings()
config.bind(settings)           # in-place; returns settings
# Or bind a subtree only:
config.bind(settings, 'AppSettings')
```

## PROVIDER REFERENCE (only when needed)

### ConfigurationBuilder fluent methods

| Method | Source | Key params |
|--------|--------|------------|
| `add_json(filepath, json, fd, required=True)` | JSON file/string/fd | `filepath`, `json` (str), `fd` (int), `required` |
| `add_toml(...)` | TOML | Same pattern |
| `add_yaml(...)` | YAML | Same pattern |
| `add_command_line(argv=None)` | sys.argv | `argv` override |
| `add_environment(required_prefix=None)` | os.environ | Filter to `<prefix>_*` vars only |
| `add_provider(provider)` | Any subclass | — |

### Custom provider

```python
from appsettings2 import Configuration
from appsettings2.providers import ConfigurationProvider

class MyProvider(ConfigurationProvider):
    def populate_configuration(self, configuration: Configuration) -> None:
        configuration.set('my_key', 'my_value')
```

Providers are typically < 20 lines. Use `set()` with dot-notation keys; hierarchy builds automatically.

## EDGE CASES (link for full details)

- Complex binding scenarios (Union'd types, optional sub-objects): [docs/object_binding.rst](docs/object_binding.rst)
- normalize / scrubkeys behavior: [docs/attribute_handling.rst](docs/attribute_handling.rst)
- Full API reference: <https://appsettings2.readthedocs.io/>
