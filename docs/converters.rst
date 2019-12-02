==========
Converters
==========

All ``convclasses`` functionality is exposed through a ``convclasses.Converter`` object.
Global ``convclasses`` functions, such as ``convclasses.unstructure()``, use a single
global converter. Changes done to this global converter, such as registering new
``structure`` and ``unstructure`` hooks, affect all code using the global
functions.

Global converter
----------------

A global converter is provided for convenience as ``convclasses.global_converter``.
The following functions implicitly use this global converter:

* ``convclasses.structure``
* ``convclasses.unstructure``
* ``convclasses.structure_dataclass_fromtuple``
* ``convclasses.structure_dataclass_fromdict``

Changes made to the global converter will affect the behavior of these
functions.

Larger applications are strongly encouraged to create and customize a different,
private instance of ``Converter``.

Converter objects
-----------------

To create a private converter, simply instantiate a ``convclasses.Converter``.
Currently, a converter contains the following state:

* a registry of unstructure hooks, backed by a ``singledispatch`` and a ``function_dispatch``.
* a registry of structure hooks, backed by a different ``singledispatch`` and ``function_dispatch``.
* a LRU cache of union disambiguation functions.
* a reference to an unstructuring strategy (either AS_DICT or AS_TUPLE).
* a ``dict_factory`` callable, used for creating ``dicts`` when dumping
  ``dataclasses`` classes using AS_DICT.
