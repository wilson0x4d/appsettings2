Direct Access
=============

There are three methods of accessing configuration values directly via :py:class:`~appsettings2.Configuration`:

* Dynamic Attributes generated from configuration data.
* Configuration keys accessed by calling :py:meth:`~appsettings2.Configuration.get` and :py:meth:`~appsettings2.Configuration.set` methods.
* Configuration keys accessed using dictionary-like indexer syntax.

Dynamic Attributes
------------------

When configuration values are populated into a :py:class:`~appsettings2.Configuration` object, attributes are dynamically attached to the object based on configuration keys used in the configuration source. These dynamic attributes can be used to read/write configuration values:

.. code:: python

   config = ConfigurationBuilder()\
        .addProvider(JsonConfigurationProvider(json="""
        {
            "ConnectionStrings": {
                "SampleDb": "my_cxn_string"
            },
        }
        """))\
        .build()

    print(config.ConnectionStrings.SampleDb) # outputs: "my_cxn_string"

The :py:meth:`~appsettings2.Configuration.get` and :py:meth:`~appsettings2.Configuration.set` Methods
-----------------------------------------------------------------------------------------------------

Configuration values can be accessed using their associated keys by calling :py:meth:`~appsettings2.Configuration.get` and :py:meth:`~appsettings2.Configuration.set` methods:

.. code:: python

    print(config.get('ConnectionStrings:SampleDb')) # outputs: "my_cxn_string"
    print(config.get('ConnectionStrings__SampleDb')) # outputs: "my_cxn_string"
    print(config.get('ConnectionStrings').get('SampleDb')) # outputs: "my_cxn_string"

Dictionary-like Interface
-------------------------

:py:class:`~appsettings2.Configuration` also exposes a dictionary-like interface providing keyed access to configuration values using indexer syntax:

.. code:: python

    print(config['ConnectionStrings:SampleDb']) # outputs: "my_cxn_string"
    print(config['ConnectionStrings__SampleDb']) # outputs: "my_cxn_string"
    print(config['ConnectionStrings']['SampleDb']) # outputs: "my_cxn_string"


All of the above **Direct Access** methods are equivalent and refer to the same underlying data (a single configuration value.)

