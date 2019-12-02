=====================
Common Usage Examples
=====================

This section covers common use examples of convclasses features.

Using Pendulum for Dates and Time
---------------------------------

To use the excellent Arrow_ library for datetimes, we need to register
structuring and unstructuring hooks for it.

First, we need to decide on the unstructured representation of a datetime
instance. Since all our datetimes will use the UTC time zone, we decide to
use the UNIX epoch timestamp as our unstructured representation.

Define a class using Arrow's DateTime:

.. code-block:: python

    import arrow
    from arrow import Arrow

    @dataclass
    class MyRecord:
        a_string: str
        a_datetime: Arrow

Next, we register hooks for the ``Arrow`` class on a new :class:`.Converter` instance.

.. code-block:: python

    converter = Converter()

    converter.register_unstructure_hook(Arrow, lambda ar: ar.float_timestamp)

    converter.register_structure_hook(Arrow, lambda ts, _: arrow.get(ts))

And we can proceed with unstructuring and structuring instances of ``MyRecord``.

.. testsetup:: arrow

    import arrow
    from arrow import Arrow

    @dataclass
    class MyRecord:
        a_string: str
        a_datetime: Arrow

    converter = convclasses.Converter()
    converter.register_unstructure_hook(Arrow, lambda ar: ar.float_timestamp)
    converter.register_structure_hook(Arrow, lambda ts, _: arrow.get(ts))

.. doctest:: arrow

    >>> my_record = MyRecord('test', arrow.Arrow(2018, 7, 28, 18, 24))
    >>> my_record
    MyRecord(a_string='test', a_datetime=<Arrow [2018-07-28T18:24:00+00:00]>)

    >>> converter.unstructure(my_record)
    {'a_string': 'test', 'a_datetime': 1532802240.0}

    >>> converter.structure({'a_string': 'test', 'a_datetime': 1532802240.0}, MyRecord)
    MyRecord(a_string='test', a_datetime=<Arrow [2018-07-28T18:24:00+00:00]>)


After a while, we realize we *will* need our datetimes to have timezone information.
We decide to switch to using the ISO 8601 format for our unstructured datetime instances.

.. testsetup:: arrow-iso8601

    import arrow
    from arrow import Arrow

    @dataclass
    class MyRecord:
        a_string: str
        a_datetime: Arrow

.. doctest:: arrow-iso8601

    >>> converter = convclasses.Converter()
    >>> converter.register_unstructure_hook(Arrow, lambda dt: dt.isoformat())
    >>> converter.register_structure_hook(Arrow, lambda isostring, _: arrow.get(isostring))

    >>> my_record = MyRecord('test', arrow.Arrow(2018, 7, 28, 18, 24, tzinfo='Europe/Paris'))
    >>> my_record
    MyRecord(a_string='test', a_datetime=<Arrow [2018-07-28T18:24:00+02:00]>)

    >>> converter.unstructure(my_record)
    {'a_string': 'test', 'a_datetime': '2018-07-28T18:24:00+02:00'}

    >>> converter.structure({'a_string': 'test', 'a_datetime': '2018-07-28T18:24:00+02:00'}, MyRecord)
    MyRecord(a_string='test', a_datetime=<Arrow [2018-07-28T18:24:00+02:00]>)


.. _Arrow: https://arrow.readthedocs.io/