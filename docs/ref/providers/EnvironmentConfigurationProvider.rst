providers.EnvironmentConfigurationProvider
==========================================

The `EnvironmentConfigurationProvider` consumes environment variables as key-value pairs. For example, consider these `bash` exports:

.. code:: bash

   export ConnectionStrings__SampleDb=my_cxn_string
   export ConnectionStrings__AnotherDb=another_cxn_string

The above will result in a Configuration object with the following state (represented as JSON):

.. code:: json

   {
      "ConnectionStrings": {
         "SampleDb": "my_cxn_string",
         "AnotherDb": "another_cxn_string"
      }
   }

____

Filtering by prefix
-------------------

Pass ``required_prefix`` to include only environment variables whose names start with that string, and have the prefix stripped from each key in the output configuration:

.. code:: python

   provider = EnvironmentConfigurationProvider(required_prefix="APP_")
   # APP_DATABASE_URL=postgres://...  →  config["DATABASE_URL"] == "postgres://..."
   provider.populate_configuration(config)

With the environment variables below::

   export APP_DATABASE_URL=postgres://localhost/db
   export APP_SECRET_KEY=abc123
   export DATABASE_URL=mysql://other/host    # no prefix match — ignored

the configuration will contain only:

.. code:: json

   {
      "DATABASE_URL": "postgres://localhost/db",
      "SECRET_KEY": "abc123"
   }

____

.. currentmodule:: appsettings2.providers

.. autoclass:: EnvironmentConfigurationProvider
   :members:
   :show-inheritance:
   :inherited-members:
