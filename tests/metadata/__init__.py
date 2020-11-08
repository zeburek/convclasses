"""Tests for metadata functionality."""
import dataclasses
import sys
from dataclasses import MISSING
from typing import Any, Dict, List, FrozenSet, Tuple

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
    tuples, sets, frozensets,
)

from .. import gen_attr_names, make_dataclass

is_39_or_later = sys.version_info[:2] >= (3, 9)


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
    if not is_39_or_later:
        return (
                bare_typed_attrs(defaults)
                | int_typed_attrs(defaults)
                | str_typed_attrs(defaults)
                | float_typed_attrs(defaults)
                | dict_typed_attrs(defaults)
        )
    else:
        return (
                bare_typed_attrs(defaults)
                | int_typed_attrs(defaults)
                | str_typed_attrs(defaults)
                | float_typed_attrs(defaults)
                | dict_typed_attrs(defaults)
                | new_dict_typed_attrs(defaults)
                | set_typed_attrs(defaults)
                | list_typed_attrs(defaults)
                | frozenset_typed_attrs(defaults)
                | homo_tuple_typed_attrs(defaults)
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
    return _get_field(_type=str, default=default), text()


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
        _get_field(_type=Dict[str, int], default_factory=lambda: default),
        val_strat,
    )


@composite
def new_dict_typed_attrs(draw, defaults=None):
    """
    Generate a tuple of an attribute and a strategy that yields dictionaries
    for that attribute. The dictionaries map strings to integers.

    Uses the new 3.9 dict annotation.
    """
    default = MISSING
    val_strat = dictionaries(keys=text(), values=integers())
    if defaults is True or (defaults is None and draw(booleans())):
        default = lambda: draw(val_strat)
    return (_get_field(_type=dict[str, int], default_factory=default), val_strat)


@composite
def set_typed_attrs(draw, defaults=None):
    """
    Generate a tuple of an attribute and a strategy that yields sets
    for that attribute. The sets contain integers.
    """
    default = MISSING
    val_strat = sets(integers())
    if defaults is True or (defaults is None and draw(booleans())):
        default = lambda: draw(val_strat)
    return (_get_field(_type=set[int], default_factory=default), val_strat)


@composite
def frozenset_typed_attrs(draw, defaults=None):
    """
    Generate a tuple of an attribute and a strategy that yields frozensets
    for that attribute. The frozensets contain integers.
    """
    default = MISSING
    val_strat = frozensets(integers())
    if defaults is True or (defaults is None and draw(booleans())):
        default = draw(val_strat)
    return (
        _get_field(
            _type=frozenset[int] if draw(booleans()) else FrozenSet[int],
            default=default,
        ),
        val_strat,
    )


@composite
def list_typed_attrs(draw, defaults=None):
    """
    Generate a tuple of an attribute and a strategy that yields lists
    for that attribute. The lists contain floats.
    """
    default = MISSING
    val_strat = lists(floats(allow_infinity=False, allow_nan=False))
    if defaults is True or (defaults is None and draw(booleans())):
        default = lambda: draw(val_strat)
    return (
        _get_field(
            _type=list[float] if draw(booleans()) else List[float],
            default_factory=default,
        ),
        val_strat,
    )


@composite
def homo_tuple_typed_attrs(draw, defaults=None):
    """
    Generate a tuple of an attribute and a strategy that yields homogenous
    tuples for that attribute. The tuples contain strings.
    """
    default = MISSING
    val_strat = tuples(text(), text(), text())
    if defaults is True or (defaults is None and draw(booleans())):
        default = draw(val_strat)
    return (
        _get_field(
            _type=tuple[str, ...] if draw(booleans()) else Tuple[str, ...],
            default=default,
        ),
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


def new_list_of_class(tup):
    """Uses the new 3.9 list type annotation."""
    nested_cl = tup[1][0]
    nested_cl_args = tup[1][1]
    default = lambda: [nested_cl(*nested_cl_args)]
    combined_attrs = list(tup[0])
    combined_attrs.append(
        (
            _get_field(_type=list[nested_cl], default_factory=default),
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
