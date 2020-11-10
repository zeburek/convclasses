=========
Modifiers
=========

Change structuring/unstructuring name in dict
---------------------------------------------

Sometimes you may face a problem, when you need to structure data,
that has fields that could not be created in python:

.. doctest::

    >>> @dataclass
    ... class TestModel:
    ...     user_agent: str
    ...
    >>> convclasses.structure({"User-Agent": "curl/7.71.1"}, TestModel)
    Traceback (most recent call last):
     ...
    TypeError: __init__() missing 1 required positional argument: 'user_agent'

Now you can avoid this, and also use convclasses with such structures:

.. doctest::

    >>> from convclasses import mod
    >>> @dataclass
    ... class TestModel:
    ...     user_agent: str = mod.name("User-Agent")
    ...     other_field: str = mod.name("other field", field(default=None))
    ...
    >>> obj = convclasses.structure({"User-Agent": "curl/7.71.1"}, TestModel)
    >>> obj
    TestModel(user_agent='curl/7.71.1', other_field=None)
    >>> convclasses.unstructure(obj)
    {'User-Agent': 'curl/7.71.1', 'other field': None}
