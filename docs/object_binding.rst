Object Binding
==============

It's possible to populate complex objects using the :py:meth:`~appsettings2.Configuration.bind` method.

This makes it possible to load configuration data from multiple providers into application-specific objects, without requiring the application-specific objects to have any knowledge about :py:mod:`~appsettings2`.

To illustrate, this code unifies JSON and YAML into a single configuration object, and then binds the configuration to an application-specific object model:

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
        SampleDB:str

    class AppSettings:
        ConnectionStrings:ConnStrs
        EnableSwagger:bool
        MaxBatchSize:int

    configuration = ConfigurationBuilder()\
        .addProvider(JsonConfigurationProvider(json=json))
        .addProvider(YamlConfigurationProvider(yaml=yaml))
        .build()

    settings = AppSettings()
    configuration.bind(settings)

    print(settings.ConnectionStrings.SampleDB) # outputs: "my_cxn_string"
    print(settings.MaxBatchSize) # outputs: 100

.. note:: It's worth noting that :py:meth:`~appsettings2.Configuration.bind` is case-insensitive by design. This ensures that automation/configuration systems which can only communicate in upper-case can be used to populate complex objects which follow a strict naming convention without burdening devs/devops with extra work. The casing of attributes on the bind target is always preserved.
