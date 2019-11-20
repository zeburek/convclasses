"""Tests for auto-disambiguators."""
import pytest
from dataclasses import dataclass, fields, asdict

from hypothesis import assume, given

from convclasses.disambiguators import create_uniq_field_dis_func

from . import simple_classes


def test_edge_errors():
    """Edge input cases cause errors."""

    @dataclass
    class A(object):
        pass

    with pytest.raises(ValueError):
        # Can't generate for only one class.
        create_uniq_field_dis_func(A)

    @dataclass
    class B(object):
        pass

    with pytest.raises(ValueError):
        # No fields on either class.
        create_uniq_field_dis_func(A, B)

    @dataclass
    class C(object):
        a: str

    @dataclass
    class D(object):
        a: str

    with pytest.raises(ValueError):
        # No unique fields on either class.
        create_uniq_field_dis_func(C, D)


@given(simple_classes(defaults=False))
def test_fallback(cl_and_vals):
    """The fallback case works."""
    cl, vals = cl_and_vals

    assume(fields(cl))  # At least one field.

    @dataclass
    class A(object):
        pass

    fn = create_uniq_field_dis_func(A, cl)

    assert fn({}) is A
    assert fn(asdict(cl(*vals))) is cl

    attr_names = {a.name for a in fields(cl)}

    if "xyz" not in attr_names:
        fn({"xyz": 1}) is A  # Uses the fallback.


@given(simple_classes(), simple_classes())
def test_disambiguation(cl_and_vals_a, cl_and_vals_b):
    """Disambiguation should work when there are unique fields."""
    cl_a, vals_a = cl_and_vals_a
    cl_b, vals_b = cl_and_vals_b

    req_a = {a.name for a in fields(cl_a)}
    req_b = {a.name for a in fields(cl_b)}

    assume(len(req_a))
    assume(len(req_b))

    assume((req_a - req_b) or (req_b - req_a))

    fn = create_uniq_field_dis_func(cl_a, cl_b)

    assert fn(asdict(cl_a(*vals_a))) is cl_a
