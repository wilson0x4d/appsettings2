providers.CommandLineConfigurationProvider
==========================================

The `CommandLineConfigurationProvider` allows configuration data to be provided via command-line interface. This provider will process args in the following forms as key-value pairs:

.. code:: bash

    my_app \
        --ConnectionStrings__SampleDb 'my_connection_string' \
        'ConnectionStrings__SampleDb=my_connection_string' \
        --ConnectionStrings__SampleDb=my_connection_string \
        'ConnectionStrings:SampleDb=my_connection_string' \
        --force

All of the forms in the above example result in a configuration object with the following state (represented as JSON):

.. code:: json

    {
        "ConnectionStrings" : {
            "SampleDb": "my_connection_string"
        },
        "force": true
    }

.. note:: Be aware that leading dashes have been stripped, and the "switch" argument not in a key-value format has been populated as a boolean ``True`` configuration value.

The double-underscore ``__`` convention seen above (and elsewhere in the docs) is a common convention borrowed from other platforms/frameworks. The use of a colon ``:`` in lieu of a double-underscore ``__`` is also borrowed from other platforms/frameworks, although it is much less popular.

.. note:: This provider was implemented in a way that it does not interfere with libraries such as ``argparse``, and should work as expected with a well-formed command-line interface. An explicit goal of this provider was to not depend on a CLI library at all.

____

.. currentmodule:: appsettings2.providers

.. autoclass:: CommandLineConfigurationProvider
   :members:
   :show-inheritance:
   :inherited-members:
