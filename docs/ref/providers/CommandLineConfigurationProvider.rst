providers.CommandLineConfigurationProvider
==========================================

The `CommandLineConfigurationProvider` allows configuration data to be provided via command-line interface. This provider will process variables in the following forms as key-value pairs:

``--ConnectionStrings__SampleDb 'my_connection_string'``

``'ConnectionStrings__SampleDb=my_connection_string'``

``--ConnectionStrings__SampleDb=my_connection_string``

All three of these forms result in a configuration object with the following state (represented as JSON):

.. code:: json

    {
        "ConnectionStrings" : {
            "SampleDb": "my_connection_string"
        }
    }

(Take note that leading dashes have been stripped.)

The double-underscore convention seen above is borrowed from other platforms/frameworks. It's also possible to use a colon in lieu of a double_underscore, but this may have unintended side-effects depending on the shell or platform being used:

``'ConnectionStrings:SampleDb=my_connection_string'``

This provider was implemented in a way that it does not interfere with libraries such as `argparse`, and should work as expected with a well-formed command-line interface. An explicit goal of this provider was to not depend on a CLI library at all.

____

.. currentmodule:: appsettings2.providers

.. autoclass:: CommandLineConfigurationProvider
   :members:
   :show-inheritance:
   :inherited-members:
