
nbmake [Under Construction]
===========================


.. image:: https://codecov.io/gh/treebeardtech/nbmake/branch/main/graph/badge.svg?token=9GuDM35FuO
   :target: https://codecov.io/gh/treebeardtech/nbmake
   :alt: codecov


.. image:: https://badge.fury.io/py/nbmake.svg
   :target: https://badge.fury.io/py/nbmake
   :alt: PyPI version


Pytest plugin for building notebooks

Functionality
-------------


#. Implements the pytest plugin API allowing parallel execution of notebooks via ``pytest-xdist``
#. Uses ``jupyter-book`` as a runtime, enabling caching for jupyter book builds and supporting the same presentation/execution options.

This facilitates building compute-intensive documentation. See `docs <https://treebeardtech.github.io/nbmake>`_ to get started.

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
