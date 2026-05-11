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

.. py:function:: get_configuration(basename, json, toml, yaml, cli, environment, variations)
    :canonical: appsettings2.helpers.get_configuration

    :param str|pathlib.Path|pathlib.PosixPath basename: The "base name" used to construct filenames for file-based providers.  Default: ``"appsettings"``.
    :param bool json: A flag indicating that :py:class:`~appsettings2.providers.JsonConfigurationProvider` should be used.  Default is ``True``.
    :param bool toml: A flag indicating that :py:class:`~appsettings2.providers.TomlConfigurationProvider` should be used.  Default is ``True``.
    :param bool yaml: A flag indicating that :py:class:`~appsettings2.providers.YamlConfigurationProvider` should be used.  Default is ``True``.
    :param bool cli: A flag indicating that :py:class:`~appsettings2.providers.CommandLineConfigurationProvider` should be used.  Default is ``True``.
    :param bool environment: A flag indicating that :py:class:`~appsettings2.providers.EnvironmentConfigurationProvider` should be used.  Default is ``True``.
    :param list[str] variations: A list of variations to be applied when constructing files for file-based providers.

Filename Construction Logic
---------------------------

When constructing filenames for file-based Providers, the following format is used:

``{basename}.{variation}.{extension}``.

The ``extension`` is inferred based on the provider type, and is one of ``json``, ``toml``, or ``yaml``.

The ``basename`` is received as a parameter, the default value if not specified is ``appsettings``.

The ``variation`` is received as a list parameter, the default list if not specified is:

.. code:: python

    [
        '',            # appsettings.json
        'prod',        # appsettings.prod.json
        'production',  # appsettings.production.json
        'stage',       # appsettings.stage.json
        'staging',     # appsettings.staging.json
        'qa',          # appsettings.qa.json
        'dev',         # appsettings.dev.json
        'development', # appsettings.development.json
        'local'        # appsettings.local.json
    ]

The order of the list is the order of variation evaluation (per-Provider.)

Provider Order
--------------

The provider order of ``get_configuration`` is fixed, and follows the parameter order of the function.  Specifically:

* JsonConfigurationProvider
* TomlConfigurationProvider
* YamlConfigurationProvider
* CommandLineConfigurationProvider
* EnvironmentConfigurationProvider

The overall ordering being config files first, then command-line args, and finally environment variables.  This ordering is based on conventions typical to cloud and containerized environments.  Often Environment Variables are the final arbiter of what a configuration setting should be (avoiding weird things like sidecars.) CLI args are often baked into container images or similar making them less-attractive over a broader range of deployments, and config files come from source control, making them the least-preferred by ops teams (and conversely more-preferred by developers.)

``pathlib`` Support
-------------------

For convenience, ``basename`` may be a ``pathlib``-generated object, for example:

.. code:: python

    from appsettings2 import get_configuration

    config = get_configuration(Path.home() / '.config' / 'app_directory_name' / 'settings_file_name')


