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

## Binding to Configuration Data

It's also possible to bind configuration data to complex types. While some of the implementation is currently naive, it should work well for the vast majority of use-cases. If you find your particular edge case does not work well please reach out to me and I will work with you to implement a sensible solution.  Consider the following Python code:

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

### Projecting Configuration Data as a Dictionary

Lastly, as a convenience feature you can materialize a `Configuration` instance as a Dictionary. This is primarily included as a debugging aid, but, if you have some chunk of code that can consume a dictionary but can't consume a Python object (it happens) then you can get at a dictionary as follows:

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

config = ConfigurationBuilder(normalize=True)\
    .addProvider(JsonConfigurationProvider('example.json'))\
    .build()

print(config.ConnectionStrings.SampleDb)
```
Outputs: `my_cxn_string` (as expected.)

### TOML

The `TomlConfigurationProvider` should be functionally identical to the JSON provider, with the obvious difference that it loads Configuration data from a toml file.

### YAML

The `YamlConfigurationProvider` should be functionally identical to the JSON and TOML providers, with the obvious difference that it loads Configuration data from a yaml file.

## A note on `normalize` parameters..

`ConfigurationBuilder` accepts a parameter `normalize:bool` which defaults to `False` causing `bind()` to behave in a case-sensitive fashion.

When set to `True` it causes the internal implementation of `Configuration` to normalize all configuration keys to uppercase, and consequently, `bind(...)` is no longer case-sensitive.

However, the resulting `Configuration` object attribute names also become normalized to upper case which may not be desired by some developers.

Probably most devs and devops working in enterprise environments will want to adopt `normalize=True` as a matter of practice. This will allow devops to conform around the use of upper-case key names in configuration systems, and allow devs to use whatever casing rules make the most sense for their projects (since `bind()` will still work as expected.) This does assume developers are creating concerete configuration types (you ARE doing that, correct?)

I would have preferred to make `normalize=True` by default, but, I suspect someone out there will want to use `Configuration` instances directly rather than create bind targets and this would have resulted in attribute names that were upper case. To illustrate, one of the early examples in this doc would instead look like this:

```python
value = configuration.CONNECTIONSTRINGS.SAMPLEDB # <-- this
value = configuration.get('ConnectionStrings:SampleDb')
value = configuration.get('ConnectionStrings__SampleDb')
```

In the future I may abstract this detail away so we get the best of both worlds, but for now there is the parameter to let you control the behavior.

## Conclusion

If you made it this far, this library is probably what you were looking for. I'm certain there are other libraries which accomplish much of what I am attempting to accomplish here, but I wanted something I can directly support over the coming years. That, and the nearest equivalent to what I wanted fell out of active development nearly a decade ago and I just didn't feel comfortable adopting it for new work.
