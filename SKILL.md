---
name: appsettings2
description: Unifies configuration sources into a Configuration object that can be bound to complex Python types or accessed directly. Covers ConfigurationBuilder, providers, object binding, helpers, and ConfigurationException. Use as a reference document for appsettings2 API and concepts.
user-invocable: true
disable-model-invocation: false
type: reference
---

# appsettings2 — AI-First Feature Reference

**Unifies configuration sources into a `Configuration` object that can be bound to complex Python types or accessed directly.** Requires Python 3.11+.

```python
from appsettings2 import ConfigurationBuilder
from appsettings2.providers import JsonConfigurationProvider, EnvironmentConfigurationProvider

config = ConfigurationBuilder()\
    .add_provider(JsonConfigurationProvider('appsettings.json'))\
    .add_provider(EnvironmentConfigurationProvider())\
    .build()
```

---

## Table of Contents

1. [ConfigurationBuilder](#1-configurationbuilder)
2. [Configuration Access Patterns](#2-configuration-access-patterns)
3. [Object Binding](#3-object-binding)
4. [Built-in Providers](#4-built-in-providers)
5. [helpers.get_configuration](#5-helpersget_configuration)
6. [CustomAttributes](#6-custom-attributes)
7. [Dictionary Conversion](#7-dictionary-conversion)
8. [ConfigurationException](#8-configurationalertionerror)

---

## 1. ConfigurationBuilder

Fluent builder that assembles one or more `ConfigurationProvider` objects into a single `Configuration`.

### Constructor

```python
ConfigurationBuilder(normalize: bool = False, scrubkeys: bool = False) -> ConfigurationBuilder
```

| Parameter | Effect |
|---|---|
| `normalize=True` | Normalises all attribute names to UPPER-CASE on the resulting `Configuration` |
| `scrubkeys=True` | Scrubs attribute names to be lexically valid Python identifiers (replaces non-identifier chars with `_`) |

### Chaining helpers

All return `ConfigurationBuilder` for fluent chaining.

```python
builder = ConfigurationBuilder()

builder.add_provider(provider)           # custom provider (most generic)
builder.add_json(filepath='s.json')      # from file or string
builder.add_toml(filepath='s.toml')      # from file or string
builder.add_yaml(filepath='s.yaml')      # from file or string
builder.add_command_line(argv=['a=1'])   # from sys.argv or custom list
builder.add_environment()                # from os.environ
builder.add_environment(required_prefix='APP_')  # only APP_* vars, prefix stripped
```

### `required` parameter on file-based providers

```python
.add_json('appsettings.Production.json', required=False)   # silently missing
.add_toml('secrets.toml', required=True)                    # raises ConfigurationException
```

### `required_prefix` on environment provider

When `required_prefix='PREFIX_'`, only environment variables starting with `PREFIX_` are loaded, and that prefix is **stripped** from the resulting config key.

```bash
export MYAPP_DB_HOST=postgres://...        # loaded as "DB_HOST"
export OTHER_KEY=value                     # ignored
```

### `build()`

```python
config = ConfigurationBuilder()\
    .add_json('base.json')\
    .add_json('appsettings.Development.json', required=False)\
    .add_environment()\
    .build()
```

**Precedence rule:** providers added later take precedence. Later providers override values from earlier providers for matching keys only.

---

## 2. Configuration Access Patterns

The `Configuration` object exposes **four** equivalent ways to read hierarchical config data, using `__` or `:` as path delimiters.

```python
# Example hierarchy produces key "ConnectionStrings__SampleDb" or "ConnectionStrings:SampleDb"

config.ConnectionStrings.SampleDb            # dynamic attribute (case-sensitive)
config.get('ConnectionStrings__SampleDb')     # get() API (case-insensitive)
config.get('ConnectionStrings:SampleDb')      # colon-delimiter (case-insensitive)
config.get('ConnectionStrings').get('SampleDb')  # chained get() (case-insensitive)
config['ConnectionStrings__SampleDb']         # indexer (case-insensitive)
config['ConnectionStrings']['SampleDb']       # chained indexer (case-insensitive)
```

### Key delimiters

`__` and `:` are **equivalent** and both case-insensitive. Attribute access is **case-sensitive**.

### Setting values

```python
config.set('Section__Key', 'value')     # hierarchical key
config['Section__Key'] = 'value'        # same via setter
```

### Other members

| Member | Signature | Description |
|---|---|---|
| `get(key, default=None)` | `Any` | Get value with fallback |
| `set(key, value)` | `None` | Set a (possibly nested) key |
| `has_key(key)` | `bool` | Check existence (case-insensitive) |
| `keys()` | `list[str]` | All top-level keys |
| `items()` | `list[tuple[str, Any]]` | Key-value pairs |
| `values()` | `list[Any]` | All values |
| `pop(key)` | `Any` | Retrieve and delete |
| `clear()` | `None` | Remove all keys |
| `__delitem__(key)` | `None` | Delete by key |
| `__iter__()` | `Iterator[str]` | Iterate keys |
| `__len__()` | `int` | Number of keys |

---

## 3. Object Binding

Map configuration data onto strongly-typed Python classes with type hints. The binding is **case-insensitive** and performs **primitive coercion**.

### Basic binding

```python
from appsettings2 import ConfigurationBuilder
from appsettings2.providers import JsonConfigurationProvider

config = ConfigurationBuilder()\
    .add_json(json='''{
        "ConnectionStrings": {"SampleDb": "conn_str_here"},
        "EnableSwagger": true,
        "MaxBatchSize": 100
    }''')\
    .build()

class ConnStrs:
    SampleDB: str

class AppSettings:
    ConnectionStrings: ConnStrs
    EnableSwagger: bool
    MaxBatchSize: int

settings = AppSettings()
config.bind(settings)

print(settings.ConnectionStrings.SampleDB)   # "conn_str_here"
```

### Partial binding (key-subset)

Bind only a slice of the configuration using the `key` parameter:

```python
conn_strs = config.bind(ConnStrs(), 'ConnectionStrings')
print(conn_strs.SampleDB)
```

Returns the target object (for method chaining).

### Collection binding

```python
from typing import List

class Node:
    host: str
    port: int

class ClusterSettings:
    servers: dict[str, Node]
    nodes: list[Node]
    ports: set[int]

config.bind(ClusterSettings())
```

- `dict[str, SomeClass]` — values are **rehydrated** into instances of `SomeClass`
- `list[SomeClass]` — each element is **rehydrated** into an instance of `SomeClass`
- `set[SomeClass]` — each element is **rehydrated** into an instance of `SomeClass`
- `dict[str, str]` — remains a plain dict (no rehydration)
- `list[int]` / `set[str]` — elements coerced to the element type

### Nullable / Optional / Union fields

```python
from typing import Optional

class Settings:
    maybe_servers: Optional[dict[str, InnerNode]]  # None if absent in config
```

### Primitive type coercion

Binding converts config values to match type hints:

| Target type | Coercion |
|---|---|
| `int` | `int(value)` |
| `float` | `float(value)` |
| `str` | `str(value)` |
| `bool` | `bool(value)` |

### Scrubbed / normalized key matching

When both the `ConfigurationBuilder` and the `Configuration` use `scrubkeys=True` or `normalize=True`, binding matches scrubbed/normalised names:

```python
config = ConfigurationBuilder(normalize=True, scrubkeys=True).build()
config.set('X-foo.1', 'hello')   # stored as 'X_FOO_1'

class Target:
    x_foo_1: str

config.bind(Target())   # Target.x_foo_1 == 'hello'
```

---

## 4. Built-in Providers

All providers subclass the abstract `ConfigurationProvider`:

```python
class ConfigurationProvider(ABC):
    @abstractmethod
    def populate_configuration(self, configuration: Configuration) -> None:
        ...
```

### 4.1 JsonConfigurationProvider

```python
from appsettings2.providers import JsonConfigurationProvider

# From file path (required by default)
JsonConfigurationProvider(filepath='appsettings.json')

# From JSON string
JsonConfigurationProvider(json='{"key": "value"}')

# From file descriptor (int)
JsonConfigurationProvider(fd=io.open('appsettings.json').fd)

# Optional / environment-override pattern
JsonConfigurationProvider(filepath='appsettings.Production.json', required=False)
```

Hierarchical JSON flattens to `__`-delimited keys. Nested dicts produce nested `Configuration` objects.

### 4.2 YamlConfigurationProvider

```python
from appsettings2.providers import YamlConfigurationProvider

YamlConfigurationProvider(filepath='appsettings.yaml')
YamlConfigurationProvider(yaml='key: value')
```

Same interface and behavior as JSON provider, using `yaml.safe_load`. **Requires `pyyaml`.**

### 4.3 TomlConfigurationProvider

```python
from appsettings2.providers import TomlConfigurationProvider

TomlConfigurationProvider(filepath='appsettings.toml')
TomlConfigurationProvider(toml='key = "value"')
```

Same interface as JSON provider, using `tomllib`. **No extra dependency — stdlib in Python 3.11+.**

### 4.4 EnvironmentConfigurationProvider

```python
from appsettings2.providers import EnvironmentConfigurationProvider

# All env vars become config keys
EnvironmentConfigurationProvider()

# Only vars with prefix (prefix stripped in output)
EnvironmentConfigurationProvider(required_prefix='APP_')
```

### 4.5 CommandLineConfigurationProvider

```python
from appsettings2.providers import CommandLineConfigurationProvider

# Uses sys.argv
CommandLineConfigurationProvider()

# Custom argv
CommandLineConfigurationProvider(argv=['--key=value', 'flag'])
```

Parses `--key=value` pairs and `--flag` switches (set to `True`). Keys may be `key__nested` for hierarchy.

### 4.6 Custom Provider

```python
from appsettings2 import Configuration
from appsettings2.providers import ConfigurationProvider

class RedisConfigurationProvider(ConfigurationProvider):
    def populate_configuration(self, configuration: Configuration) -> None:
        import redis
        client = redis.Redis()
        configuration.set('Redis__Host', client.config_get('host')['host'])
```

Most providers are under 20 lines of logic.

---

## 5. helpers.get_configuration

Convenience function for the common case of loading from well-known file variations, CLI args, and environment variables in a single call.

```python
import appsettings2

config = appsettings2.get_configuration()
```

### Parameters

| Parameter | Default | Description |
|---|---|---|
| `basename` | `'appsettings'` | Base filename for file-based providers |
| `json` | `True` | Load JSON variations |
| `toml` | `True` | Load TOML variations |
| `yaml` | `True` | Load YAML variations |
| `cli` | `True` | Load from command-line args |
| `environment` | `True` | Load from environment variables |
| `variations` | `['', 'prod', 'production', 'stage', 'staging', 'qa', 'dev', 'development', 'local']` | Filename suffixes (e.g. `appsettings.Development.json`) |
| `env_prefix` | `None` | If set, only load env vars with this prefix (stripped from key) |

### Examples

```python
# Default: loads appsettings.json, appsettings.dev.json, etc.
config = appsettings2.get_configuration()

# Custom base name and skip TOML
config = appsettings2.get_configuration('myapp', toml=False)

# Custom variation list (dev only, nothing else)
config = appsettings2.get_configuration('appsettings', variations=['dev', 'staging'])

# Only load env vars with prefix, skip all file-based providers
config = appsettings2.get_configuration(
    json=False, toml=False, yaml=False, cli=False,
    environment=True, env_prefix='MYAPP_'
)

# pathlib.Path support
from pathlib import Path
config = appsettings2.get_configuration(Path('configs') / 'settings')
```

Each variation file is loaded with `required=False` so missing files are silently skipped.

---

## 6. CustomAttributes

### `normalize`

When `normalize=True` on the builder, all keys are stored in **UPPER-CASE** on the resulting `Configuration` object. Attribute access becomes case-insensitive too.

```python
config = ConfigurationBuilder(normalize=True).build()
config.set('Section__Key', 'value')
print(config.SECTION__KEY)   # 'value'
```

### `scrubkeys`

When `scrubkeys=True`, keys are rewritten to be valid Python identifiers — non-identifier characters are replaced with `_`.

```python
config = ConfigurationBuilder(scrubkeys=True).build()
config.set('X-foo.bar', 'hello')
print(config.X_FOO_BAR)   # 'hello'
```

---

## 7. Dictionary Conversion

### Transform Configuration to dict

```python
d = config.to_dict()
```

Returns a recursive copy. Nested Configuration objects become nested dicts.

### Create Configuration from dict (static factory)

```python
from appsettings2 import Configuration

config = Configuration.from_dict({
    'Section': {
        'Key1': 'value1',
        'Key2': 42
    }
})

# With custom options
config = Configuration.from_dict(data, normalize=True, scrubkeys=True)
```

---

## 8. ConfigurationException

```python
from appsettings2 import ConfigurationException

try:
    config = ConfigurationBuilder()\
        .add_json('missing_required.json', required=True)\
        .build()
except ConfigurationException as e:
    print(e.reason)   # "Missing required file: missing_required.json"
```

Raised when a required configuration source (file) is not found.

---

## Export summary

| Symbol | Module | Description |
|---|---|---|
| `Configuration` | `appsettings2` | Main config object |
| `ConfigurationBuilder` | `appsettings2` | Builder with fluent API |
| `ConfigurationException` | `appsettings2` | Error type |
| `get_configuration()` | `appsettings2` | Quick-start helper |
| `helpers` | `appsettings2` | Namespace for helpers module |
| `providers` | `appsettings2` | Namespace for provider modules |
| `ConfigurationProvider` | `appsettings2.providers` | Abstract base for custom providers |
| `JsonConfigurationProvider` | `appsettings2.providers` | JSON file/string |
| `YamlConfigurationProvider` | `appsettings2.providers` | YAML file/string |
| `TomlConfigurationProvider` | `appsettings2.providers` | TOML file/string |
| `EnvironmentConfigurationProvider` | `appsettings2.providers` | os.environ |
| `CommandLineConfigurationProvider` | `appsettings2.providers` | CLI args |
