JsonConfigurationProvider
=========================

The `JsonConfigurationProvider` class allows you to load configuration data from a JSON file, JSON string, or JSON stream. Consider the following JSON:

.. code:: json

    {
        "Logging": {
            "Default": "Debug"
        },
        "ConnectionStrings": {
            "SampleDb": "my_cxn_string"
        },
    }

When loaded using :py:class:`~appsettings2.providers.JsonConfigurationProvider` the resulting :py:class:`~appsettings2.Configuration` object will have attribute names and a structure which matches the JSON, consider the following (where "example.json" contains the above JSON):

.. code:: python

    from appsettings2 import *
    from appsettings2.providers import *

    config = ConfigurationBuilder()\
        .addProvider(JsonConfigurationProvider('example.json'))\
        .build()

    print(config['LOGGING_DEFAULT']) # outputs: "Debug"
    print(config.ConnectionStrings.SampleDb) # outputs: "my_cxn_string"

____

.. currentmodule:: appsettings2.providers

.. autoclass:: JsonConfigurationProvider
   :members:
   :show-inheritance:
   :inherited-members:
