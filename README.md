# `appsettings2`

A python library that unifies configuration sources into a Configuration object that can be bound to complex types, or accessed directly for configuration data.

## Why?

Because I write a lot of containerized applications where I typically supply configuration settings using a combination of Configuration Files and Environment Variables.

When I debug those applications I often need to override Configuration using Command-Line Arguments, Configuration Files, Environment Variables, or a combination thereof.

## Usage

Construct a `ConfigurationBuilder` instance, add one or more `ConfigurationProvider` instances to it, and then use it to build a `Configuration` object containing your unified configuration data.

```python
from appsettings2 import *
from appsettings2.providers import *

def get_configuration() -> Configuration:
    return ConfigurationBuilder()\
        .addProvider(JsonConfigurationProvider(f'appsettings.json'))\
        .addProvider(JsonConfigurationProvider(f'appsettings.Development.json', required=False))\
        .addProvider(EnvironmentConfigurationProvider())\
        .build()
```

In the above example two JSON Configuration Providers are added to the builder. The first will fail if "appsettings.json" is not found, the second will succeed whether or not the "appsettings.Development.json" exists (because `required=False`). This allows for an optional development configuration to exist on development workstations without requiring a code change.

A third Configuration Provider is also added, an `EnvironmentConfigurationProvider`, which allows configuration to be loaded from Environment Variables.

The order of providers determines precedence of configuration data. Providers added last will take precedence over providers added first. Values which are not provided by later registrations will not override values provided by earlier registrations.

Given the example above, this means that configuration data provided via Environment Variables will override configuration data provided via JSON files.

## Accessing Configuration Data

There are two methods of directly accessing Configuration data. The first is by using first-class attributes, and the second is by using a `get(...)` method. 

Consider the following code which demonstrates both methods, where all three of these statements are equivalent:

```python
value = configuration.ConnectionStrings.SampleDb
value = configuration.get('ConnectionStrings:SampleDb')
value = configuration.get('ConnectionStrings__SampleDb')
```

When accessing hierarchical data with `get(...)` you can use a double-underscore delimiter or a colon delimiter, they are equivalent. Devs and Ops from different walks will likely prefer one form over the other, so both are supported.

### Binding to Configuration Data

It's also possible to bind configuration data to complex types. While some of the implementation is currently naive, it should work well for the vast majority of use cases. If you find your particular case does not work well please reach out to me and I will work with you to implement a sensible solution.  Consider the following Python code:

```python
json = """{
  "ConnectionStrings": {
    "SampleDb": "my_cxn_string"
  },
  "EnableSwagger": true,
  "MaxBatchSize": 100
}"""

class ConnStrs:
    """An ugly class name to demonstrate the class name does not matter."""
    SampleDb:str = None

class AppSettings:
    ConnectionStrings:ConnStrs = None
    EnableSwagger:bool = None
    MaxBatchSize:int = None

configuration = ConfigurationBuilder()\
    .addProvider(JsonConfigurationProvider(json=json))
    .build()

settings = AppSettings()
configuration.bind(settings)
```

The resulting `settings` object will contain all of the configuration data properly typed according to type hints.

It is also possible to bind to a subset of a configuration, building upon the above, consider the following:

```python
connectionStrings = configuration.bind(ConnStrs(), 'ConnectionStrings')
print(connectionStrings.SampleDb)
```

### Accessing Configuration Data as a Dictionary

`Configuration` is dict-like (with minor exceptions such as not supporting dynamic views) and in most cases can be used as if it were a dict where strict type checks would not otherwise prevent it.

Alternatively, you can project a `Configuration` instnace into a dictionary (as a copy.) This is primarily included as a debugging aid, but, if you have some chunk of code that can consume a dictionary but can't consume a Python object (it happens) then you can get at a proper dictionary instance as follows:

```python
config:Configuration = builder.build()
my_dict = config.toDictionary()
print(my_dict)
```

## Providers

### Command-Line

The `CommandLineConfigurationProvider` allows configuration data to be provided via command-line interface. This provider will process variables in the following forms as key-value pairs:

```
--ConnectionStrings__SampleDb 'my_connection_string'
```

```
'ConnectionStrings__SampleDb=my_connection_string'
```

```
--ConnectionStrings__SampleDb=my_connection_string
```

All three of these forms result in a configuration object with the following state (represented as JSON):

```json
{
    "ConnectionStrings" : {
        "SampleDb": "my_connection_string"
    }
}
```

Take note that the leading dashes are stripped.

This double-underscore convention is a convention borrowed from other platforms/frameworks.

It's also possible to use a colon in lieu of a double_underscore, but this may have unintended side-effects depending on the shell or platform being used:

```
'ConnectionStrings:SampleDb=my_connection_string'
```

This provider was implemented in a way that it does not interfere with libraries such as `argparse`, and should work as expected with a well-formed command-line interface. 

### Environment Variables

The `EnvironmentConfigurationProvider` consumes environment variables as key-value pairs. For example, consider these `bash` exports:

```bash
export ConnectionStrings__SampleDb=my_cxn_string
export ConnectionStrings__AnotherDb=another_cxn_string
```

The above will result in a Configuration object with the following state (represented as JSON):

```json
{
    "ConnectionStrings": {
        "SampleDb": "my_cxn_string",
        "AnotherDb": "another_cxn_string"
    }
}
```

### JSON

The `JsonConfigurationProvider` class allows you to load configuration data from a JSON file, JSON string, or JSON stream. Consider the following JSON:

```json
{
    "Logging": {
        "Default": "Debug"
    },
    "ConnectionStrings": {
        "SampleDb": "my_cxn_string"
    },
}
```

When loaded using `JsonConfigurationProvider` the resulting `Configuration` object will have attribute names and a structure which matches the JSON, consider the following Python code (where "example.json" contains the above JSON):

```python
from appsettings2 import *
from appsettings2.providers import *

config = ConfigurationBuilder()\
    .addProvider(JsonConfigurationProvider('example.json'))\
    .build()

print(config.ConnectionStrings.SampleDb)
```
Outputs: `my_cxn_string` (as expected.)

### TOML

The `TomlConfigurationProvider` should be functionally identical to the JSON provider, with the obvious difference that it loads Configuration data from a toml file.

### YAML

The `YamlConfigurationProvider` should be functionally identical to the JSON and TOML providers, with the obvious difference that it loads Configuration data from a yaml file.

## Special Attribute Name Handling

### Upper-Case Attribute Names

`ConfigurationBuilder` accepts a parameter `normalize:bool` which defaults to `False` causing `Configuration` attributes to preserve the casing of keys from the input configuration.

If you pass `normalize=True`, all `Configuration` instances created by that builder will normalize `Configuration` attributes to upper-case.

In both cases the `Configuration` object allows access to data in a case-insensitive fashion. Normalization _ONLY_ affects the resulting object attributes.

To illustrate, consider the following snippet:

```python
configuration = Configuration(normalize=True)
configuration.set('ConnectionStrings__SampleDb', 'blah')
# normalized attributes looks like this:
value = configuration.CONNECTIONSTRINGS.SAMPLEDB
# but you can still access the data case-insensitive:
value = configuration.get('connectionstrings__SAMPLEDB')
value = configuration['cOnNeCtioNsTriNGs']['sampledb']
# however, by default (where normalize=False):
configuration = Configuration()
configuration.set('ConnectionStrings__SampleDb', 'blah')
# attributes look like this:
value = configuration.ConnectionStrings.SampleDb
# and as before, you have case-insensitive access:
value = configuration.get('connectionstrings__SAMPLEDB')
value = configuration['cOnNeCtioNsTriNGs']['sampledb']
```

Normalization has no effect on `bind(...)`, which operates in a case-insensitive fashion internally.

### Lexer-friendly Attribute Names

`ConfigurationBuilder` accepts a parameter `scrubkeys:bool` which defaults to `False` causing `Configuration` attributes to preserve the keys from the input configuration even if they would be inaccessible from Python code.

If you pass `scrubkeys=True`, all `Configuration` instances created by that builder will generate lexically accessible `Configuration` attributes.

This is not enabled by default because it introduces an edge case where configuration keys may collide, albeit very unlikely, this is explained below.

Some configuration sources might produce attribute names which are not accessible from Python code. Consider the following JSON snippet:

```json
{
  "query-tab" : {
    "fragment#left": {
        "input": true
    }
  }
}
```

This configuration will load, and you can still access the data using keyed methods such as `get(...)` and `set(...)`, but the resulting `Configuration` object will have attributes that cannot be accessed from Python code:

```python
if True == configuration.query-tab.fragment#left.input:
    pass
```

To accomodate configurations such as these and make them accessible via `Configuration` attributes you may pass `scrubkeys=True`. This will cause any lexically invalid characters to be transformed into an underscore `_` character.

Although attribute names are transformed, keys are not. Therefore, given the above JSON snippet the following are equivalent:

```python
# access via object attributes
configuration.query_tab.fragement_left.input
# access using indexers
configuration['query-tab']['fragment#left']
# access using other 'key' methods
configuration.get('query-tab').has_key('fragment#left')
```

Lastly, this _does_ make it possible for configuration values to collide, for example, these two keys will collide:

```json
{
  "key#1": true,
  "key-1": false
}
```

Attempting to access these values will result in a value of `False` being returned, and setting the value of one key will affect the value of the other, this is because internally there will be only one storage slot/attribute that is shared between them. Although an unlikely scenario, it is for this reason the feature is opt-in only.

## Conclusion

If you made it this far, this library is probably what you were looking for. I'm certain there are other libraries which accomplish much of what I am attempting to accomplish here, but I wanted something I can directly support over the coming years. That, and the nearest equivalent to what I wanted fell out of active development nearly a decade ago and I just didn't feel comfortable adopting it for new work.
