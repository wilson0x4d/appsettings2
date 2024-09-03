.. toctree::
   :titlesonly:
   :maxdepth: 3
   :hidden:

   Introduction <self>
   Accessing Values <accessing>
   appsettings2.* <ref/appsettings2>

Introduction
============

:py:mod:`appsettings2` unifies configuration sources into a :py:class:`~appsettings2.Configuration` object that can be bound to complex types, or accessed directly for configuration data.

Quick start
============

Construct a :py:class:`~appsettings2.ConfigurationBuilder` instance, add one or more :py:class:`~appsettings2.providers.ConfigurationProvider` instances to it, and then call :py:meth:`~appsettings2.ConfigurationBuilder.build` to create a :py:class:`~appsettings2.Configuration` object populated with configuration data.

.. code:: python

    from appsettings2 import *
    from appsettings2.providers import *

    def get_configuration() -> Configuration:
        return ConfigurationBuilder()\
            .addProvider(JsonConfigurationProvider(f'appsettings.json'))\
            .addProvider(JsonConfigurationProvider(f'appsettings.Development.json', required=False))\
            .addProvider(EnvironmentConfigurationProvider())\
            .build()

Provider Order
--------------

The order that providers are added is important, the last provider to populate configuration data will overwrite any earlier provider which populated the same configuration data.

In the above example, because :py:class:`~appsettings2.providers.EnvironmentConfigurationProvider` is added to the builder last it is possible to use Environment variables to overwrite any configuration values which were populated by either of the JSON providers.

Provider Compatibility
----------------------

All of the built-in providers can be used at the same time without conflict.

Provider Availability
---------------------

There are providers for populating configuration values from:

* Command-Line args, via :py:class:`~appsettings2.providers.CommandLineConfigurationProvider`.
* Environment variables, via :py:class:`~appsettings2.providers.EnvironmentConfigurationProvider`.
* JSON, via :py:class:`~appsettings2.providers.JsonConfigurationProvider`.
* TOML, via :py:class:`~appsettings2.providers.TomlConfigurationProvider`.
* YAML, via :py:class:`~appsettings2.providers.YamlConfigurationProvider`.
