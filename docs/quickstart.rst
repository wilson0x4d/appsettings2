Quick Start
============

Installation
------------

You can install the library from `PyPI <https://pypi.org/project/appsettings2/>`_ using typical methods, such as ``pip``:

.. code:: bash

   python3 -m pip install appsettings2

Usage
-----

Using :py:mod:`~appsettings2` is straightforward:

1. Construct a :py:class:`~appsettings2.ConfigurationBuilder` object.
2. Add one or more :py:class:`~appsettings2.providers.ConfigurationProvider` objects to it.
3. Call :py:meth:`~appsettings2.ConfigurationBuilder.build` to get a :py:class:`~appsettings2.Configuration` object populated with configuration data.

.. code:: python

   config = ConfigurationBuilder()\
      .addJson('appsettings.json')\
      .addJson('appsettings.Development.json', required=False)\
      .addEnvironment()\
      .build()

Provider Order
--------------

The order that providers are added to the :py:class:`~appsettings2.ConfigurationBuilder` is important. The configuration data populated by multiple providers is merged together, and providers appearing first will have their configuration values overwritten by providers appearing last.

With the above code snippet, consider the following configuration files:

.. rubric:: appsettings.json:
  
This file comes from source-control to implement application defaults.

.. code:: json

    {
        "Secret": "not-set",
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

    print(config.get('LOGGING__LEVEL', 'WARN')) # outputs: "DEBUG"
    print(config['ConnectionStrings']['SampleDb']) # outputs: "Server=localhost"
    print(config.AppSettings.EnableSwagger) # outputs: True
    print(config.AppSettings.MaxBatchSize) # outputs: 100


Additionally, because :py:class:`~appsettings2.providers.EnvironmentConfigurationProvider` is added to the builder last (via :py:meth:`~appsettings2.ConfigurationBuilder.addEnvironment`) it is possible to use Environment variables to overwrite any configuration values which were populated by either of the JSON providers. Consider the following ``bash`` export and associated python code, assume these are set on the developer workstation in addition to the above two configuration files:

.. code:: bash

    # in `bash`, set env vars
    export CONNECTIONSTRINGS__SAMPLEDB="Server=prod"
    export APPSETTINGS__ENABLESWAGGER=0

.. code:: python

    # in python, check the config
    print(config.ConnectionStrings.SampleDb) # outputs: "Server=prod"
    print(config.AppSettings.EnableSwagger) # outputs: False

This makes it easy for developers to implement a default configuration that devops can then override as part of the Environment config of a deployment. This is a popular approach for configuring containers without leaking details into source control, particularly useful for keeping secrets like API keys and database details out of source control.
