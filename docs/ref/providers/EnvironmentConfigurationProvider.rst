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

.. currentmodule:: appsettings2.providers

.. autoclass:: EnvironmentConfigurationProvider
   :members:
   :show-inheritance:
   :inherited-members:
