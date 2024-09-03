providers.YamlConfigurationProvider
===================================
The `YamlConfigurationProvider` class allows you to load configuration data from a YAML file, YAML string, or YAML stream. Consider the following YAML:

.. code:: yaml

   logging:
      default: Debug

   ConnectionStrings:
      SampleDb: my_cxn_string

When loaded using `YamlConfigurationProvider` the resulting `Configuration` object will have attribute names and a structure which matches the YAML, consider the following Python code (where "example.yaml" contains the above YAML):

.. code:: python

    from appsettings2 import *
    from appsettings2.providers import *

    config = ConfigurationBuilder()\
        .addProvider(YamlConfigurationProvider('example.yaml'))\
        .build()

    print(config.ConnectionStrings.SampleDb) # outputs: "my_cxn_string"

____

.. currentmodule:: appsettings2.providers

.. autoclass:: YamlConfigurationProvider
   :members:
   :show-inheritance:
   :inherited-members:
