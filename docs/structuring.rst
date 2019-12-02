==============================
What you can structure and how
==============================

The philosophy of ``convclasses`` structuring is simple: give it an instance of Python
built-in types and collections, and a type describing the data you want out.
``convclasses`` will convert the input data into the type you want, or throw an
exception.

All loading conversions are composable, where applicable. This is
demonstrated further in the examples.

Primitive values
----------------

``typing.Any``
~~~~~~~~~~~~~~

Use ``typing.Any`` to avoid applying any conversions to the object you're
loading; it will simply be passed through.

.. doctest::

    >>> convclasses.structure(1, Any)
    1
    >>> d = {1: 1}
    >>> convclasses.structure(d, Any) is d
    True

``int``, ``float``, ``str``, ``bytes``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use any of these primitive types to convert the object to the type.

.. doctest::

    >>> convclasses.structure(1, str)
    '1'
    >>> convclasses.structure("1", float)
    1.0

In case the conversion isn't possible, the expected exceptions will be
propagated out. The particular exceptions are the same as if you'd tried to
do the conversion yourself, directly.

.. code-block:: python

    >>> convclasses.structure("not-an-int", int)
    Traceback (most recent call last):
    ...
    ValueError: invalid literal for int() with base 10: 'not-an-int'

Enums
~~~~~

Enums will be structured by their values. This works even for complex values,
like tuples.

.. doctest::

    >>> @unique
    ... class CatBreed(Enum):
    ...    SIAMESE = "siamese"
    ...    MAINE_COON = "maine_coon"
    ...    SACRED_BIRMAN = "birman"
    ...
    >>> convclasses.structure("siamese", CatBreed)
    <CatBreed.SIAMESE: 'siamese'>

Again, in case of errors, the expected exceptions will fly out.

.. code-block:: python

    >>> convclasses.structure("alsatian", CatBreed)
    Traceback (most recent call last):
    ...
    ValueError: 'alsatian' is not a valid CatBreed

Collections and other generics
------------------------------

Optionals
~~~~~~~~~

``Optional`` primitives and collections are supported out of the box.

.. doctest::

    >>> convclasses.structure(None, int)
    Traceback (most recent call last):
    ...
    TypeError: int() argument must be a string, a bytes-like object or a number, not 'NoneType'
    >>> convclasses.structure(None, Optional[int])
    >>> # None was returned.

Bare ``Optional`` s (non-parameterized, just ``Optional``, as opposed to
``Optional[str]``) aren't supported, use ``Optional[Any]`` instead.

This generic type is composable with all other converters.

.. doctest::

    >>> convclasses.structure(1, Optional[float])
    1.0

Lists
~~~~~

Lists can be produced from any iterable object. Types converting to lists are:

* ``Sequence[T]``
* ``MutableSequence[T]``
* ``List[T]``

In all cases, a new list will be returned, so this operation can be used to
copy an iterable into a list. A bare type, for example ``Sequence`` instead of
``Sequence[int]``, is equivalent to ``Sequence[Any]``.

.. doctest::

    >>> convclasses.structure((1, 2, 3), MutableSequence[int])
    [1, 2, 3]

These generic types are composable with all other converters.

.. doctest::

    >>> convclasses.structure((1, None, 3), List[Optional[str]])
    ['1', None, '3']

Sets and frozensets
~~~~~~~~~~~~~~~~~~~

Sets and frozensets can be produced from any iterable object. Types converting
to sets are:

* ``Set[T]``
* ``MutableSet[T]``

Types converting to frozensets are:

* ``FrozenSet[T]``

In all cases, a new set or frozenset will be returned, so this operation can be
used to copy an iterable into a set. A bare type, for example ``MutableSet``
instead of ``MutableSet[int]``, is equivalent to ``MutableSet[Any]``.

.. doctest::

    >>> convclasses.structure([1, 2, 3, 4], Set)
    {1, 2, 3, 4}

These generic types are composable with all other converters.

.. doctest::

    >>> convclasses.structure([[1, 2], [3, 4]], Set[FrozenSet[str]])
    {frozenset({'1', '2'}), frozenset({'4', '3'})}

Dictionaries
~~~~~~~~~~~~

Dicts can be produced from other mapping objects. To be more precise, the
object being converted must expose an ``items()`` method producing an iterable
key-value tuples, and be able to be passed to the ``dict`` constructor as an
argument. Types converting to dictionaries are:

* ``Dict[K, V]``
* ``MutableMapping[K, V]``
* ``Mapping[K, V]``

In all cases, a new dict will be returned, so this operation can be
used to copy a mapping into a dict. Any type parameters set to ``typing.Any``
will be passed through unconverted. If both type parameters are absent,
they will be treated as ``Any`` too.

.. doctest::

    >>> from collections import OrderedDict
    >>> convclasses.structure(OrderedDict([(1, 2), (3, 4)]), Dict)
    {1: 2, 3: 4}

These generic types are composable with all other converters. Note both keys
and values can be converted.

.. doctest::

    >>> convclasses.structure({1: None, 2: 2.0}, Dict[str, Optional[int]])
    {'1': None, '2': 2}

Homogeneous and heterogeneous tuples
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Homogeneous and heterogeneous tuples can be produced from iterable objects.
Heterogeneous tuples require an iterable with the number of elements matching
the number of type parameters exactly. Use:

* ``Tuple[A, B, C, D]``

Homogeneous tuples use:

* ``Tuple[T, ...]``

In all cases a tuple will be returned. Any type parameters set to
``typing.Any`` will be passed through unconverted.

.. doctest::

    >>> convclasses.structure([1, 2, 3], Tuple[int, str, float])
    (1, '2', 3.0)

The tuple conversion is composable with all other converters.

.. doctest::

    >>> convclasses.structure([{1: 1}, {2: 2}], Tuple[Dict[str, float], ...])
    ({'1': 1.0}, {'2': 2.0})

Unions
~~~~~~

Unions of ``NoneType`` and a single other type are supported (also known as
``Optional`` s). All other unions a require a disambiguation function.

Automatic Disambiguation
""""""""""""""""""""""""

In the case of a union consisting exclusively of ``dataclasses`` classes, ``convclasses``
will attempt to generate a disambiguation function automatically; this will
succeed only if each class has a unique field. Given the following classes:

.. code-block:: python

    >>> @dataclass
    ... class A:
    ...     a: Any
    ...     x: Any
    ...
    >>> @dataclass
    ... class B:
    ...     a: Any
    ...     y: Any
    ...
    >>> @dataclass
    ... class C:
    ...     a: Any
    ...     z: Any
    ...

``convclasses`` can deduce only instances of ``A`` will contain `x`, only instances
of ``B`` will contain ``y``, etc. A disambiguation function using this
information will then be generated and cached. This will happen automatically,
the first time an appropriate union is structured.

Manual Disambiguation
"""""""""""""""""""""

To support arbitrary unions, register a custom structuring hook for the union
(see `Registering custom structuring hooks`_).

``dataclasses`` classes
-----------------------

Simple ``dataclasses`` classes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``dataclasses`` classes using primitives, collections of primitives and their own
converters work out of the box. Given a mapping ``d`` and class ``A``,
``convclasses`` will simply instantiate ``A`` with ``d`` unpacked.

.. doctest::
   :pyversion: > 3.6

    >>> @dataclass
    ... class A:
    ...     a: Any
    ...     b: int
    ...
    >>> convclasses.structure({'a': 1, 'b': '2'}, A)
    A(a=1, b=2)

``dataclasses`` classes deconstructed into tuples can be structured using
``convclasses.structure_attrs_fromtuple`` (``fromtuple`` as in the opposite of
``dataclasses.astuple`` and ``converter.unstructure_attrs_astuple``).

.. doctest::

    >>> # Loading from tuples can be made the default by creating a new
    ... @dataclass
    ... class A:
    ...     a: Any
    ...     b: int
    ...
    >>> convclasses.structure_dataclass_fromtuple(['string', '2'], A)
    A(a='string', b=2)

Loading from tuples can be made the default by creating a new ``Converter`` with
``unstruct_strat=convclasses.UnstructureStrategy.AS_TUPLE``.

.. doctest::

    >>> converter = convclasses.Converter(unstruct_strat=convclasses.UnstructureStrategy.AS_TUPLE)
    >>> @dataclass
    ... class A:
    ...     a: Any
    ...     b: int
    ...
    >>> converter.structure(['string', '2'], A)
    A(a='string', b=2)

Structuring from tuples can also be made the default for specific classes only;
see registering custom structure hooks below.

Complex ``dataclasses`` classes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Complex ``dataclasses`` classes are classes with type information available for some
or all attributes. These classes support almost arbitrary nesting.

Type information can be set using type annotations when using Python 3.6+.

.. doctest::

    >>> @dataclass
    ... class A:
    ...     a: int
    ...
    >>> fields(A) #doctest: +ELLIPSIS
    (Field(name='a',type=<class 'int'>,default=<dataclasses._MISSING_TYPE object at 0x...>,default_factory=<dataclasses._MISSING_TYPE object at 0x...>,init=True,repr=True,hash=None,compare=True,metadata=mappingproxy({}),_field_type=_FIELD),)

Type information, when provided, can be used for all attribute types, not only
attributes holding ``dataclasses`` classes.

.. doctest::

    >>> @dataclass
    ... class A:
    ...     a: int = field(default=0)
    ...
    >>> @dataclass
    ... class B:
    ...     b: A
    ...
    >>> convclasses.structure({'b': {'a': '1'}}, B)
    B(b=A(a=1))

Registering custom structuring hooks
------------------------------------

``convclasses`` doesn't know how to structure non-``dataclasses`` classes by default,
so it has to be taught. This can be done by registering structuring hooks on
a converter instance (including the global converter).

Here's an example involving a simple, classic (i.e. non-``dataclasses``) Python class.

.. doctest::

    >>> class C(object):
    ...     def __init__(self, a):
    ...         self.a = a
    ...     def __repr__(self):
    ...         return f'C(a={self.a})'
    >>> convclasses.structure({'a': 1}, C)
    Traceback (most recent call last):
    ...
    ValueError: Unsupported type: <class '__main__.C'>. Register a structure hook for it.
    >>> convclasses.register_structure_hook(C, lambda d, t: C(**d))
    >>> convclasses.structure({'a': 1}, C)
    C(a=1)

The structuring hooks are callables that take two arguments: the object to
convert to the desired class and the type to convert to.
The type may seem redundant but is useful when dealing with generic types.

When using ``convclasses.register_structure_hook``, the hook will be registered on the global converter.
If you want to avoid changing the global converter, create an instance of ``convclasses.Converter`` and register the hook on that.

In some situations, it is not possible to decide on the converter using typing mechanisms alone (such as with dataclasses classes). In these situations,
convclasses provides a register_structure_func_hook instead, which accepts a function to determine whether that type can be handled instead.

The function-based hooks are evaluated after the class-based hooks. In the case where both a class-based hook and a function-based hook are present, the class-based hook will be used.

.. doctest::

    >>> class D(object):
    ...     custom = True
    ...     def __init__(self, a):
    ...         self.a = a
    ...     def __repr__(self):
    ...         return f'D(a={self.a})'
    ...     @classmethod
    ...     def deserialize(cls, data):
    ...         return cls(data["a"])
    >>> convclasses.register_structure_hook_func(lambda cls: getattr(cls, "custom", False), lambda d, t: t.deserialize(d))
    >>> convclasses.structure({'a': 2}, D)
    D(a=2)
