getConfiguration
================

The ``getConfiguration`` function simplifies loading of configuration settings, example:

.. code:: python

    from appsettings2 import getConfiguration

    config = getConfiguration()

This is roughly equivalent to:

.. code:: python

    import appsettings2

    config = appsettings2.ConfigurationBuilder()\
        .addJson('appsettings.json', required=False)\
        .addJson('appsettings.prod.json', required=False)\
        .addJson('appsettings.production.json', required=False)\
        .addJson('appsettings.stage.json', required=False)\
        .addJson('appsettings.staging.json', required=False)\
        .addJson('appsettings.qa.json', required=False)\
        .addJson('appsettings.dev.json', required=False)\
        .addJson('appsettings.developer.json', required=False)\
        .addJson('appsettings.local.json', required=False)\
        .addToml('appsettings.json', required=False)\
        .addToml('appsettings.prod.json', required=False)\
        .addToml('appsettings.production.json', required=False)\
        .addToml('appsettings.stage.json', required=False)\
        .addToml('appsettings.staging.json', required=False)\
        .addToml('appsettings.qa.json', required=False)\
        .addToml('appsettings.dev.json', required=False)\
        .addToml('appsettings.developer.json', required=False)\
        .addToml('appsettings.local.json', required=False)\
        .addYaml('appsettings.json', required=False)\
        .addYaml('appsettings.prod.json', required=False)\
        .addYaml('appsettings.production.json', required=False)\
        .addYaml('appsettings.stage.json', required=False)\
        .addYaml('appsettings.staging.json', required=False)\
        .addYaml('appsettings.qa.json', required=False)\
        .addYaml('appsettings.dev.json', required=False)\
        .addYaml('appsettings.developer.json', required=False)\
        .addYaml('appsettings.local.json', required=False)\
        .addCommandLine()\
        .addEnvironment()\
        .build()

You can see this may save quite a bit of typing/repetition if you're working over multiple projects.

Syntax
------

.. py:function:: getConfiguration(baseName, json, toml, yaml, cli, environment, variations)
    :canonical: appsettings2.helpers.getConfiguration

    :param str baseName: The "base name" used to construct filenames for file-based providers. Default: ``"appsettings"``.
    :param bool json: A flag indicating that :py:class:`~appsettings2.providers.JsonConfigurationProvider` should be used. Default is ``True``.
    :param bool toml: A flag indicating that :py:class:`~appsettings2.providers.TomlConfigurationProvider` should be used. Default is ``True``.
    :param bool yaml: A flag indicating that :py:class:`~appsettings2.providers.YamlConfigurationProvider` should be used. Default is ``True``.
    :param bool cli: A flag indicating that :py:class:`~appsettings2.providers.CommandLineConfigurationProvider` should be used. Default is ``True``.
    :param bool environment: A flag indicating that :py:class:`~appsettings2.providers.EnvironmentConfigurationProvider` should be used. Default is ``True``.
    :param list[str] variations: A list of variations to be applied when constructing files for file-based providers.

Filename Construction Logic
---------------------------

When constructing filenames for file-based Providers, the following format is used:

``{baseName}.{variation}.{extension}``.

The ``extension`` is inferred based on the provider type, and is one of ``json``, ``toml``, or ``yaml``.

The ``baseName`` is received as a parameter, the default value if not specified is ``appsettings``.

The ``variation`` is received as a list parameter, the default list if not specified is:

.. code:: python

    [
        '',
        'prod',
        'production',
        'stage',
        'staging',
        'qa',
        'dev',
        'development',
        'local'
    ]

The order of the list is also the order of evaluation.

The default list is based on conventions typical to various corporate/enterprise environments.

Provider Order
--------------

The provider order is fixed, and follows the parameter order of the function:

* JsonConfigurationProvider
* TomlConfigurationProvider
* YamlConfigurationProvider
* CommandLineConfigurationProvider
* EnvironmentConfigurationProvider

The overall ordering being config files, then cli, then environment variables is based on conventions typical to cloud and containerized environments. Often Environment Variables are as the final arbiter of what a configuration setting should be. CLI args are often baked into container images or similar, and config files come from source control, making them less-preferred by operators (and conversely more-preferred by developers.)
