Attribute Handling
==================

Upper-Case Attribute Names
--------------------------

:py:class:`~appsettings2.ConfigurationBuilder` accepts a parameter ``normalize:bool`` which defaults to ``False`` causing :py:class:`~appsettings2.Configuration` attributes to preserve the casing of keys from the input configuration.

If you specify ``normalize=True``, all :py:class:`~appsettings2.Configuration` instances created by that builder will normalize :py:class:`~appsettings2.Configuration` attributes to upper-case.

In both cases the :py:class:`~appsettings2.Configuration` object allows access to data in a case-insensitive fashion via :py:meth:`~appsettings2.Configuration.get`, :py:meth:`~appsettings2.Configuration.set`, and indexer methods. Normalization _ONLY_ affects **Dynamic Attributes**.

To illustrate, consider the following snippet:

.. code:: python

    configuration = Configuration(normalize=True)
    configuration.set('ConnectionStrings__SampleDb', 'blah')
    # normalized attributes looks like this:
    value = configuration.CONNECTIONSTRINGS.SAMPLEDB
    # but you can still access the data case-insensitive:
    value = configuration.get('connectionstrings__SAMPLEDB')
    value = configuration['cOnNeCtioNsTriNGs']['sampledb']
    # however, by default (where normalize=False):
    configuration = Configuration()
    configuration.set('ConnectionStrings__SampleDb', 'blah')
    # attributes look like this:
    value = configuration.ConnectionStrings.SampleDb
    # and as before, you have case-insensitive access:
    value = configuration.get('connectionstrings__SAMPLEDB')
    value = configuration['cOnNeCtioNsTriNGs']['sampledb']


.. note:: Normalization has no effect on `bind(...)`, which operates in a case-insensitive fashion internally. The casing of attributes on the bind target are preserved.

Lexer-friendly Attribute Names
------------------------------

:py:class:`~appsettings2.ConfigurationBuilder` accepts a parameter ``scrubkeys:bool`` which defaults to ``False`` causing :py:class:`~appsettings2.Configuration` attributes to preserve the keys from the input configuration even if they would be inaccessible from Python code.

If you pass ``scrubkeys=True``, all :py:class:`~appsettings2.Configuration` instances created by that builder will generate lexically accessible :py:class:`~appsettings2.Configuration` attributes.

This is not enabled by default because it introduces an edge case where configuration keys may collide, albeit very unlikely, this is explained below.

Some configuration sources might produce attribute names which are not accessible from Python code. Consider the following JSON snippet:

.. code:: json

    {
        "query-tab" : {
            "fragment#left": {
                "input": true
            }
        }
    }

This configuration will load, and you can still access the data using keyed methods such as :py:meth:`~appsettings2.Configuration.get` and :py:meth:`~appsettings2.Configuration.set`, but the resulting :py:class:`~appsettings2.Configuration` object will have attributes that cannot be accessed from Python code:

.. code:: python

    if True == configuration.query-tab.fragment#left.input:
        pass

To accomodate configurations such as these and make them accessible via :py:class:`~appsettings2.Configuration` attributes you may pass ``scrubkeys=True``. This will cause any lexically invalid characters to be transformed into an underscore `_` character.

Although attribute names are transformed, keys are not. Therefore, given the above JSON snippet the following are equivalent:

.. code:: python

    # access via object attributes
    configuration.query_tab.fragment_left.input
    # access using indexers
    configuration['query-tab']['fragment#left']
    # access using other 'key' methods
    configuration.get('query-tab').has_key('fragment#left')

Lastly, this feature makes it possible for configuration values to collide, for example:

.. code:: json

    {
        "key#1": true,
        "key-1": false
    }

Attempting to access either of these valus will return the same result for both, setting the value of one key will also set the value of the other. This is because internally there will be only one storage slot/attribute that is shared between them. Although an unlikely scenario, it is for this reason this feature is opt-in only.
