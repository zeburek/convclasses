"""Tests for generated dict functions."""
from dataclasses import MISSING

from hypothesis import assume, given

from convclasses import Converter
from convclasses.gen import make_dict_unstructure_fn, override

from . import nested_classes, simple_classes


@given(nested_classes | simple_classes())
def test_unmodified_generated_unstructuring(converter, cl_and_vals):
    cl, vals = cl_and_vals
    fn = make_dict_unstructure_fn(cl, converter)

    inst = cl(*vals)

    res_expected = converter.unstructure(inst)

    converter.register_unstructure_hook(cl, fn)

    res_actual = converter.unstructure(inst)

    assert res_expected == res_actual


@given(nested_classes | simple_classes())
def test_nodefs_generated_unstructuring(converter, cl_and_vals):
    """Test omitting default values on a per-attribute basis."""
    cl, vals = cl_and_vals

    attr_is_default = False
    for attr, val in zip(
        tuple(v for _, v in cl.__dataclass_fields__.items()), vals
    ):
        if attr.default is not MISSING:
            fn = make_dict_unstructure_fn(
                cl, converter, **{attr.name: override(omit_if_default=True)}
            )
            if attr.default == val:
                attr_is_default = True
            break
    else:
        assume(False)

    converter.register_unstructure_hook(cl, fn)

    inst = cl(*vals)

    res = converter.unstructure(inst)

    if attr_is_default:
        assert attr.name not in res


@given(nested_classes | simple_classes())
def test_nodefs_generated_unstructuring_cl(converter, cl_and_vals):
    """Test omitting default values on a per-class basis."""
    cl, vals = cl_and_vals

    for attr, val in zip(
        tuple(v for _, v in cl.__dataclass_fields__.items()), vals
    ):
        if attr.default is not MISSING:
            break
    else:
        assume(False)

    converter.register_unstructure_hook(
        cl, make_dict_unstructure_fn(cl, converter, omit_if_default=True)
    )

    inst = cl(*vals)

    res = converter.unstructure(inst)

    for attr, val in zip(
        tuple(v for _, v in cl.__dataclass_fields__.items()), vals
    ):
        if attr.default is not MISSING:
            if val == attr.default:
                assert attr.name not in res
            else:
                assert attr.name in res
        elif attr.default_factory is not MISSING:
            if val == attr.default_factory():
                assert attr.name not in res
            else:
                assert attr.name in res


@given(nested_classes | simple_classes())
def test_individual_overrides(cl_and_vals):
    """
    Test omitting default values on a per-class basis, but with individual
    overrides.
    """
    converter = Converter()
    cl, vals = cl_and_vals

    for attr, val in zip(
        tuple(v for _, v in cl.__dataclass_fields__.items()), vals
    ):
        if attr.default is not MISSING:
            break
    else:
        assume(False)

    chosen = attr

    converter.register_unstructure_hook(
        cl,
        make_dict_unstructure_fn(
            cl,
            converter,
            omit_if_default=True,
            **{attr.name: override(omit_if_default=False)}
        ),
    )

    inst = cl(*vals)

    res = converter.unstructure(inst)

    for attr, val in zip(
        tuple(v for _, v in cl.__dataclass_fields__.items()), vals
    ):
        if attr is chosen:
            assert attr.name in res
        elif attr.default is not MISSING:
            if val == attr.default:
                assert attr.name not in res
            else:
                assert attr.name in res
        elif attr.default_factory is not MISSING:
            if val == attr.default_factory():
                assert attr.name not in res
            else:
                assert attr.name in res
