"""Test both structuring and unstructuring."""
from dataclasses import dataclass, fields, make_dataclass, field, MISSING
from typing import Optional, Union

import pytest
from hypothesis import assume, given
from hypothesis.strategies import sampled_from

from convclasses import Converter, UnstructureStrategy, mod

from . import nested_typed_classes, simple_typed_attrs, simple_typed_classes

unstructure_strats = sampled_from(list(UnstructureStrategy))


@given(simple_typed_classes(), unstructure_strats)
def test_simple_roundtrip(cls_and_vals, strat):
    """
    Simple classes with metadata can be unstructured and restructured.
    """
    converter = Converter(unstruct_strat=strat)
    cl, vals = cls_and_vals
    inst = cl(*vals)
    assert inst == converter.structure(converter.unstructure(inst), cl)


@given(simple_typed_attrs(defaults=True), unstructure_strats)
def test_simple_roundtrip_defaults(cls_and_vals, strat):
    """
    Simple classes with metadata can be unstructured and restructured.
    """
    a, _ = cls_and_vals
    cl = make_dataclass("HypClass", [("a", a.type, a)])
    converter = Converter(unstruct_strat=strat)
    inst = cl()
    assert inst == converter.structure(converter.unstructure(inst), cl)


@given(simple_typed_classes())
def test_simple_name_modifiers(cls_and_vals):
    """
    Simple classes with metadata can be unstructured and restructured.
    """
    a, vals = cls_and_vals
    converter = Converter()
    if len(fields(a)) > 0:
        fld = mod.name("t-t", fields(a)[0])
        cl = make_dataclass("HypClass", [("t_t", fld.type, fld)])
        inst = cl(vals[0])
        assert converter.unstructure(inst).get("t-t", MISSING) is not MISSING
    else:
        cl = make_dataclass("HypClass", [])
        inst = cl()
    assert inst == converter.structure(converter.unstructure(inst), cl)


@given(nested_typed_classes, unstructure_strats)
def test_nested_roundtrip(cls_and_vals, strat):
    """
    Nested classes with metadata can be unstructured and restructured.
    """
    converter = Converter(unstruct_strat=strat)
    cl, vals = cls_and_vals
    # Vals are a tuple, convert into a dictionary.
    inst = cl(*vals)
    assert inst == converter.structure(converter.unstructure(inst), cl)


@given(
    simple_typed_classes(defaults=False),
    simple_typed_classes(defaults=False),
    unstructure_strats,
)
def test_union_field_roundtrip(cl_and_vals_a, cl_and_vals_b, strat):
    """
    Classes with union fields can be unstructured and structured.
    """
    converter = Converter(unstruct_strat=strat)
    cl_a, vals_a = cl_and_vals_a
    cl_b, vals_b = cl_and_vals_b
    a_field_names = {a.name for a in fields(cl_a)}
    b_field_names = {a.name for a in fields(cl_b)}
    assume(a_field_names)
    assume(b_field_names)

    common_names = a_field_names & b_field_names
    assume(len(a_field_names) > len(common_names))

    @dataclass
    class C(object):
        a: Union[cl_a, cl_b]

    inst = C(a=cl_a(*vals_a))

    if strat is UnstructureStrategy.AS_DICT:
        assert inst == converter.structure(converter.unstructure(inst), C)
    else:
        # Our disambiguation functions only support dictionaries for now.
        with pytest.raises(ValueError):
            converter.structure(converter.unstructure(inst), C)

        def handler(obj, _):
            return converter.structure(obj, cl_a)

        converter._union_registry[Union[cl_a, cl_b]] = handler
        assert inst == converter.structure(converter.unstructure(inst), C)
        del converter._union_registry[Union[cl_a, cl_b]]


@given(simple_typed_classes(defaults=False))
def test_optional_field_roundtrip(cl_and_vals):
    """
    Classes with optional fields can be unstructured and structured.
    """
    converter = Converter()
    cl, vals = cl_and_vals

    @dataclass
    class C(object):
        a: Optional[cl]

    inst = C(a=cl(*vals))
    assert inst == converter.structure(converter.unstructure(inst), C)

    inst = C(a=None)
    unstructured = converter.unstructure(inst)

    assert inst == converter.structure(unstructured, C)
