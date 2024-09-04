Providers
=========

The :py:mod:`appsettings2.providers` module contains a set of built-in :py:class:`~appsettings2.providers.ConfigurationProvider` implementations for populating configuration data from:

Configuration Sources
---------------------

* Command-Line args, via :py:class:`~appsettings2.providers.CommandLineConfigurationProvider`.
* Environment variables, via :py:class:`~appsettings2.providers.EnvironmentConfigurationProvider`.
* JSON, via :py:class:`~appsettings2.providers.JsonConfigurationProvider`.
* TOML, via :py:class:`~appsettings2.providers.TomlConfigurationProvider`.
* YAML, via :py:class:`~appsettings2.providers.YamlConfigurationProvider`.

All of the built-in providers can be used together without conflict.

Custom Configration Providers
-----------------------------

Custom Configuration Providers can be implemented by subclassing :py:class:`~appsettings2.providers.ConfigurationProvider` and implementing its only method :py:meth:`~appsettings2.providers.ConfigurationProvider.populateConfiguration`:

.. code:: python

    class MyCustomConfigurationProvider(ConfigurationProvider):

        def populateConfiguration(self, configuration:Configuration) -> None:
            configuration.set('Example', [ 1, 2, 3 ])

Essentially, you read your configuration source and write the configuration data into the specified :py:class:`~appsettings2.Configuration` object using :py:meth:`~appsettings2.Configuration.set`. Much of the complexity in dealing with hierarchy and type coercion is encapsulated within the impl of :py:class:`~appsettings2.Configuration`. As a result, most providers are less than 20 lines of functional code.

.. toctree::
    :hidden:
    :titlesonly:
    :maxdepth: 2

    ConfigurationProvider <ConfigurationProvider>
    CommandLineConfigurationProvider <CommandLineConfigurationProvider>
    EnvironmentConfigurationProvider <EnvironmentConfigurationProvider>
    JsonConfigurationProvider <JsonConfigurationProvider>
    TomlConfigurationProvider <TomlConfigurationProvider>
    YamlConfigurationProvider <YamlConfigurationProvider>

.. automodule:: appsettings2.providers
