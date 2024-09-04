Quick Start
============

Using :py:mod:`~appsettings2` is straightforward:

1. Construct a :py:class:`~appsettings2.ConfigurationBuilder` object.
2. Add one or more :py:class:`~appsettings2.providers.ConfigurationProvider` objects to it.
3. Call :py:meth:`~appsettings2.ConfigurationBuilder.build` to get a :py:class:`~appsettings2.Configuration` object populated with configuration data.

.. code:: python

   config = ConfigurationBuilder()\
      .addProvider(JsonConfigurationProvider(f'appsettings.json'))\
      .addProvider(JsonConfigurationProvider(f'appsettings.Development.json', required=False))\
      .addProvider(EnvironmentConfigurationProvider())\
      .build()

Provider Order
--------------

The order that providers are added to the :py:class:`~appsettings2.ConfigurationBuilder` is important. The configuration data populated by multiple providers is merged together, and providers appearing first will have their configuration values overwritten by providers appearing last.

With the above code snippet, consider the following configuration files:

.. rubric:: appsettings.json:
  
This file comes from source-control to implement application defaults.

.. code:: json

    {
        "Logging": {
            "Level": "WARN"
        },
        "AppSettings": {
            "EnableSwagger": false,
            "MaxBatchSize": 100
        }
    }

.. rubric:: appsettings.Development.json:

This file only exists on the developer workstation to implement local settings useful for development and testing.
  
.. code:: json

    {
        "Logging": {
            "Level": "DEBUG"
        },
        "ConnectionStrings": {
            "SampleDb": "Server=localhost;"
        },
        "AppSettings": {
            "EnableSwagger": true
        }
    }

On the developer workstation, the resulting :py:class:`~appsettings2.Configuration` object contains the following:

.. code:: python

    print(config.get('LOGGING_LEVEL', 'WARN')) # outputs: "DEBUG"
    print(config['ConnectionStrings']['SampleDb']) # outputs: "Server=localhost"
    print(config.AppSettings.EnableSwagger) # outputs: True


Additionally, because :py:class:`~appsettings2.providers.EnvironmentConfigurationProvider` is added to the builder last it is possible to use Environment variables to overwrite any configuration values which were populated by either of the JSON providers.

This makes it easy for developers to implement a default configuration that devops can then override as part of Environment config. This is a popular approach for configuring environment-specific settings without leaking those details into source control, particularly useful for keeping secrets like API keys and production database details out of source control.
