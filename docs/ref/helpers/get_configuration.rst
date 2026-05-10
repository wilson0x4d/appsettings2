get_configuration
=================

The ``get_configuration`` function simplifies loading of configuration settings, example:

.. code:: python

    from appsettings2 import get_configuration

    config = get_configuration()

This is roughly equivalent to:

.. code:: python

    import appsettings2

    config = appsettings2.ConfigurationBuilder()\
        .add_json('appsettings.json', required=False)\
        .add_json('appsettings.prod.json', required=False)\
        .add_json('appsettings.production.json', required=False)\
        .add_json('appsettings.stage.json', required=False)\
        .add_json('appsettings.staging.json', required=False)\
        .add_json('appsettings.qa.json', required=False)\
        .add_json('appsettings.dev.json', required=False)\
        .add_json('appsettings.developer.json', required=False)\
        .add_json('appsettings.local.json', required=False)\
        .add_toml('appsettings.json', required=False)\
        .add_toml('appsettings.prod.json', required=False)\
        .add_toml('appsettings.production.json', required=False)\
        .add_toml('appsettings.stage.json', required=False)\
        .add_toml('appsettings.staging.json', required=False)\
        .add_toml('appsettings.qa.json', required=False)\
        .add_toml('appsettings.dev.json', required=False)\
        .add_toml('appsettings.developer.json', required=False)\
        .add_toml('appsettings.local.json', required=False)\
        .add_yaml('appsettings.json', required=False)\
        .add_yaml('appsettings.prod.json', required=False)\
        .add_yaml('appsettings.production.json', required=False)\
        .add_yaml('appsettings.stage.json', required=False)\
        .add_yaml('appsettings.staging.json', required=False)\
        .add_yaml('appsettings.qa.json', required=False)\
        .add_yaml('appsettings.dev.json', required=False)\
        .add_yaml('appsettings.developer.json', required=False)\
        .add_yaml('appsettings.local.json', required=False)\
        .add_command_line()\
        .add_environment()\
        .build()

You can see this may save quite a bit of typing/repetition if you're working over multiple projects.

Syntax
------

.. py:function:: get_configuration(baseName, json, toml, yaml, cli, environment, variations)
    :canonical: appsettings2.helpers.get_configuration

    :param str|pathlib.Path|pathlib.PosixPath baseName: The "base name" used to construct filenames for file-based providers. Default: ``"appsettings"``.
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

``pathlib`` Support
-------

For convenience, ``baseName`` may be a ``pathlib``-generated object, for example:

.. code:: python

    from appsettings2 import get_configuration

    config = get_configuration(Path.home() / '.config' / 'app_directory_name' / 'settings_file_name')


