Accessing Configuration Values
==============================

Accessing configuration values can be broken down into two categories; **Direct Access** and **Object Binding**.

Direct Access
-------------

There are three methods of accessing configuration values directly via :py:class:`~appsettings2.Configuration`:

* Dynamic attributes which represent your configuration data.
* Configuration keys; by calling :py:meth:`~appsettings2.Configuration.get` and :py:meth:`~appsettings2.Configuration.set` methods.
* Configuration keys; using a dictionary-like interface exposing configuration data via indexer syntax.

.. rubric:: Dynamic Attributes

When configuration values are populated into a :py:class:`~appsettings2.Configuration` object, attributes are dynamically attached to the object based on the associated configuration keys. These dynamic attributes can be used to read/write configuration values:

.. code:: python

   config = ConfigurationBuilder()\
        .addProvider(JsonConfigurationProvider("""
        {
            "ConnectionStrings": {
                "SampleDb": "my_cxn_string"
            },
        }
        """))\
        .addProvider(JsonConfigurationProvider(f'appsettings.Development.json', required=False))\
        .addProvider(EnvironmentConfigurationProvider())\
        .build()

    print(config.ConnectionStrings.SampleDb) # outputs: "my_cxn_string"

.. rubric:: The ``get()`` and ``set()`` Methods

Configuration values can be accessed using their associated keys by calling :py:meth:`~appsettings2.Configuration.get` and :py:meth:`~appsettings2.Configuration.set` methods:

.. code:: python

    print(config.get('ConnectionStrings:SampleDb')) # outputs: "my_cxn_string"
    print(config.get('ConnectionStrings__SampleDb')) # outputs: "my_cxn_string"
    print(config.get('ConnectionStrings').get('SampleDb')) # outputs: "my_cxn_string"

.. rubric:: Dictionary-like Interface

:py:class:`~appsettings2.Configuration` also exposes a dictionary-like interface providing keyed access to configuration values using indexer syntax:

.. code:: python

    print(config['ConnectionStrings:SampleDb']) # outputs: "my_cxn_string"
    print(config['ConnectionStrings__SampleDb']) # outputs: "my_cxn_string"
    print(config['ConnectionStrings']['SampleDb']) # outputs: "my_cxn_string"


All of the above **Direct Access** methods are equivalent and refer to the same underlying data (a single configuration value.)

Object Binding
--------------

It's possible to populate complex objects using the :py:meth:`~appsettings2.Configuration.bind` method.

This makes it possible to load configuration unified from multiple sources into an application-specific objects without requiring them to have any knowledge about the configuration sources nor :py:mod:`~appsettings2``.

To illustrate, this code unifies JSON and YAML and then binds it to a hierarchical model:

.. code:: python

    json = """
    {
        "ConnectionStrings": {
            "SampleDb": "my_cxn_string"
        }
    }
    """

    yaml = """
    enableSwagger: true
    maxBatchSize: 100
    """

    class ConnStrs:
        """An ugly class name to demonstrate the class name does not matter."""
        SampleDB:str = None

    class AppSettings:
        ConnectionStrings:ConnStrs = None
        EnableSwagger:bool = None
        MaxBatchSize:int = None

    configuration = ConfigurationBuilder()\
        .addProvider(JsonConfigurationProvider(json=json))
        .addProvider(YamlConfigurationProvider(yaml=yaml))
        .build()

    settings = AppSettings()
    configuration.bind(settings)

    print(settings.ConnectionStrings.SampleDB) # outputs: "my_cxn_string"
    print(settings.MaxBatchSize) # outputs: 100

It's worth pointing out that :py:meth:`~appsettings2.Configuration.bind` is case-insensitive by design. This ensures that automation/configuration systems which can only communicate in upper-case can be used to populate by complex objects which follow a different naming convention without burdening devs/devops with extra work.
