
nbmake [Under Construction]
===========================


.. image:: https://codecov.io/gh/treebeardtech/nbmake/branch/main/graph/badge.svg?token=9GuDM35FuO
   :target: https://codecov.io/gh/treebeardtech/nbmake
   :alt: codecov


.. image:: https://badge.fury.io/py/nbmake.svg
   :target: https://badge.fury.io/py/nbmake
   :alt: PyPI version


Pytest plugin for testing notebooks

Functionality
-------------


#. Runs notebooks individually through `jupyter-book <https://github.com/executablebooks/jupyter-book>`_\ , allowing the same options such as allowing exceptions on individual cell.
#. Works everywhere pytest does, allowing testing locally, on pre-commit, and in the cloud
#. Builds an HTML report of each test run which can be uploaded to hosting providers such as Netlify.

See `docs <https://treebeardtech.github.io/nbmake>`_ to get started.

Developing
----------

Install local package
^^^^^^^^^^^^^^^^^^^^^

.. code-block::

   poetry install

Activate shell
^^^^^^^^^^^^^^

.. code-block::

   poetry shell

Run static checks
^^^^^^^^^^^^^^^^^

.. code-block::

   pre-commit run --all-files
   pre-commit install

Run tests
^^^^^^^^^

.. code-block::

   pytest
