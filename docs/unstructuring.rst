================================
What you can unstructure and how
================================

Unstructuring is intended to convert high-level, structured Python data (like
instances of complex classes) into simple, unstructured data (like
dictionaries).

Unstructuring is simpler than structuring in that no target types are required.
Simply provide an argument to ``unstructure`` and ``convclasses`` will produce a
result based on the registered unstructuring hooks. A number of default
unstructuring hooks are documented here.

Unstructuring is primarily done using :py:attr:`.Converter.unstructure`.

Primitive types and collections
-------------------------------

Primitive types (integers, floats, strings...) are simply passed through.
Collections are copied. There's relatively little value in unstructuring
these types directly as they are already unstructured and third-party
libraries tend to support them directly.

A useful use case for unstructuring collections is to create a deep copy of
a complex or recursive collection.

.. doctest::

    >>> # A dictionary of strings to lists of tuples of floats.
    >>> data = {'a': [(1.0, 2.0), (3.0, 4.0)]}
    >>>
    >>> copy = convclasses.unstructure(data)
    >>> data == copy
    True
    >>> data is copy
    False


``dataclasses`` classes
-----------------------

``dataclasses`` classes are supported out of the box. :class:`.Converter` s
support two unstructuring strategies:

    * ``UnstructureStrategy.AS_DICT`` - similar to ``dataclasses.asdict``, unstructures ``dataclasses`` instances into dictionaries. This is the default.
    * ``UnstructureStrategy.AS_TUPLE`` - similar to ``dataclasses.astuple``, unstructures ``dataclasses`` instances into tuples.

.. doctest::

    >>> @dataclass
    ... class C:
    ...     a: Any
    ...     b: Any
    ...
    >>> inst = C(1, 'a')
    >>> converter = convclasses.Converter(unstruct_strat=convclasses.UnstructureStrategy.AS_TUPLE)
    >>> converter.unstructure(inst)
    (1, 'a')

Mixing and matching strategies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Converters publicly expose two helper metods, :meth:`.Converter.unstructure_attrs_asdict`
and :meth:`.Converter.unstructure_attrs_astuple`. These methods can be used with
custom unstructuring hooks to selectively apply one strategy to instances of
particular classes.

Assume two nested ``dataclasses`` classes, ``Inner`` and ``Outer``; instances of
``Outer`` contain instances of ``Inner``. Instances of ``Outer`` should be
unstructured as dictionaries, and instances of ``Inner`` as tuples. Here's how
to do this.

.. doctest::

    >>> @dataclass
    ... class Inner:
    ...     a: int
    ...
    >>> @dataclass
    ... class Outer:
    ...     i: Inner
    ...
    >>> inst = Outer(i=Inner(a=1))
    >>>
    >>> converter = convclasses.Converter()
    >>> converter.register_unstructure_hook(Inner, converter.unstructure_dataclass_astuple)
    >>>
    >>> converter.unstructure(inst)
    {'i': (1,)}

Of course, these methods can be used directly as well, without changing the converter strategy.

.. doctest::

    >>> @dataclass
    ... class C:
    ...     a: int
    ...     b: str
    ...
    >>> inst = C(1, 'a')
    >>>
    >>> converter = convclasses.Converter()
    >>>
    >>> converter.unstructure_dataclass_astuple(inst)  # Default is AS_DICT.
    (1, 'a')