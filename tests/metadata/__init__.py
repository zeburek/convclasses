"""Tests for metadata functionality."""
import dataclasses
from dataclasses import MISSING
from typing import Any, Dict, List

from hypothesis.strategies import (
    booleans,
    composite,
    dictionaries,
    floats,
    integers,
    just,
    lists,
    recursive,
    text,
    tuples,
)

from convclasses._compat import unicode

from .. import gen_attr_names, make_dataclass


def _get_field(_type=None, **kwargs):
    f = dataclasses.field(**kwargs)
    f.type = _type
    return f


def fields_sorting(t):
    return (t[0].default is not MISSING) or (
        t[0].default_factory is not MISSING
    )


def simple_typed_classes(defaults=None):
    """Similar to simple_classes, but the attributes have metadata."""
    return lists_of_typed_attrs(defaults).flatmap(_create_hyp_class)


def lists_of_typed_attrs(defaults=None):
    # Python functions support up to 255 arguments.
    return lists(simple_typed_attrs(defaults), max_size=50).map(
        lambda l: sorted(l, key=fields_sorting)
    )


def simple_typed_attrs(defaults=None):
    return (
        bare_typed_attrs(defaults)
        | int_typed_attrs(defaults)
        | str_typed_attrs(defaults)
        | float_typed_attrs(defaults)
        | dict_typed_attrs(defaults)
    )


def _create_hyp_class(attrs_and_strategy):
    """
    A helper function for Hypothesis to generate attrs classes.

    The result is a tuple: an attrs class, and a tuple of values to
    instantiate it.
    """

    attrs_and_strat = sorted(attrs_and_strategy, key=fields_sorting)
    attrs = [a[0] for a in attrs_and_strat]
    vals = tuple((a[1]) for a in attrs_and_strat)
    return tuples(
        just(
            make_dataclass(
                "HypClass",
                zip(gen_attr_names(), [a.type for a in attrs], attrs),
            )
        ),
        tuples(*vals),
    )


@composite
def bare_typed_attrs(draw, defaults=None):
    """
    Generate a tuple of an attribute and a strategy that yields values
    appropriate for that attribute.
    """
    default = MISSING
    if defaults is True or (defaults is None and draw(booleans())):
        default = None
    return _get_field(_type=Any, default=default), just(None)


@composite
def int_typed_attrs(draw, defaults=None):
    """
    Generate a tuple of an attribute and a strategy that yields ints for that
    attribute.
    """
    default = MISSING
    if defaults is True or (defaults is None and draw(booleans())):
        default = draw(integers())
    return _get_field(_type=int, default=default), integers()


@composite
def str_typed_attrs(draw, defaults=None):
    """
    Generate a tuple of an attribute and a strategy that yields strs for that
    attribute.
    """
    default = MISSING
    if defaults is True or (defaults is None and draw(booleans())):
        default = draw(text())
    return _get_field(_type=unicode, default=default), text()


@composite
def float_typed_attrs(draw, defaults=None):
    """
    Generate a tuple of an attribute and a strategy that yields floats for that
    attribute.
    """
    default = MISSING
    if defaults is True or (defaults is None and draw(booleans())):
        default = draw(floats())
    return _get_field(_type=float, default=default), floats()


@composite
def dict_typed_attrs(draw, defaults=None):
    """
    Generate a tuple of an attribute and a strategy that yields dictionaries
    for that attribute. The dictionaries map strings to integers.
    """
    default = MISSING
    val_strat = dictionaries(keys=text(), values=integers())
    if defaults is True or (defaults is None and draw(booleans())):
        default = draw(val_strat)
    return (
        _get_field(_type=Dict[unicode, int], default_factory=lambda: default),
        val_strat,
    )


def just_class(tup):
    # tup: Tuple[List[Tuple[_CountingAttr, Strategy]],
    #            Tuple[Type, Sequence[Any]]]
    nested_cl = tup[1][0]
    nested_cl_args = tup[1][1]
    combined_attrs = list(tup[0])
    combined_attrs.append(
        (
            _get_field(
                _type=nested_cl,
                default_factory=lambda: nested_cl(*nested_cl_args),
            ),
            just(nested_cl(*nested_cl_args)),
        )
    )
    return _create_hyp_class(combined_attrs)


def list_of_class(tup):
    nested_cl = tup[1][0]
    nested_cl_args = tup[1][1]
    combined_attrs = list(tup[0])
    combined_attrs.append(
        (
            _get_field(
                _type=List[nested_cl],
                default_factory=lambda: [nested_cl(*nested_cl_args)],
            ),
            just([nested_cl(*nested_cl_args)]),
        )
    )
    return _create_hyp_class(combined_attrs)


def dict_of_class(tup):
    nested_cl = tup[1][0]
    nested_cl_args = tup[1][1]
    combined_attrs = list(tup[0])
    combined_attrs.append(
        (
            _get_field(
                _type=Dict[str, nested_cl],
                default_factory=lambda: {"cls": nested_cl(*nested_cl_args)},
            ),
            just({"cls": nested_cl(*nested_cl_args)}),
        )
    )
    return _create_hyp_class(combined_attrs)


def _create_hyp_nested_strategy(simple_class_strategy):
    """
    Create a recursive attrs class.
    Given a strategy for building (simpler) classes, create and return
    a strategy for building classes that have as an attribute:
        * just the simpler class
        * a list of simpler classes
        * a dict mapping the string "cls" to a simpler class.
    """
    # A strategy producing tuples of the form ([list of attributes], <given
    # class strategy>).
    attrs_and_classes = tuples(lists_of_typed_attrs(), simple_class_strategy)

    return (
        attrs_and_classes.flatmap(just_class)
        | attrs_and_classes.flatmap(list_of_class)
        | attrs_and_classes.flatmap(dict_of_class)
    )


nested_typed_classes = recursive(
    simple_typed_classes(), _create_hyp_nested_strategy
)
