Direct Access
=============

There are three methods of accessing configuration values directly via :py:class:`~appsettings2.Configuration`:

* Dynamic Attributes generated from configuration data.
* Configuration keys accessed by calling :py:meth:`~appsettings2.Configuration.get` and :py:meth:`~appsettings2.Configuration.set` methods.
* Configuration keys accessed using dictionary-like indexer syntax.

All of the above **Direct Access** methods are equivalent and refer to the same underlying data (no copies are made.)


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

In addition to the above indexer syntax, :py:class:`~appsettings2.Configuration` also supports additional dictionary-like methods such as ``items()``, ``keys()``, and ``values()`` (and others) -- in most cases :py:class:`~appsettings2.Configuration` can be used as a stand-in where a ``dict`` would normally be used. However, type-checking will show that it is not a ``dict`` subclass. If you have some code that strictly requires a ``dict`` you can use the :py:meth:`~appsettings2.Configuration.toDictionary` method to acquire an actual dictionary.
