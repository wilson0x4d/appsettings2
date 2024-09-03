providers.TomlConfigurationProvider
===================================

The `TomlConfigurationProvider` class allows you to load configuration data from a TOML file, TOML string, or TOML stream. Consider the following TOML:

.. code:: toml

   [logging]
   default = "Debug"

   [ConnectionStrings]
   SampleDb = "my_cxn_string"

When loaded using `TomlConfigurationProvider` the resulting `Configuration` object will have attribute names and a structure which matches the TOML, consider the following Python code (where "example.toml" contains the above TOML):

.. code:: python

    from appsettings2 import *
    from appsettings2.providers import *

    config = ConfigurationBuilder()\
        .addProvider(TomlConfigurationProvider('example.toml'))\
        .build()

    print(config.ConnectionStrings.SampleDb) # outputs: "my_cxn_string"

____

.. currentmodule:: appsettings2.providers

.. autoclass:: TomlConfigurationProvider
   :members:
   :show-inheritance:
   :inherited-members:
