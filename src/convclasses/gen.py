import dataclasses
from typing import Optional, Sequence

from ._compat import is_sequence


@dataclasses.dataclass(frozen=True)
class AttributeOverride:
    omit_if_default: Optional[bool] = dataclasses.field(default=None)


def override(omit_if_default=None):
    return AttributeOverride(omit_if_default=omit_if_default)


_neutral = AttributeOverride()


def make_dict_unstructure_fn(cl, converter, omit_if_default=False, **kwargs):
    """Generate a specialized dict unstructuring function for a class."""
    cl_name = cl.__name__
    fn_name = "unstructure_" + cl_name
    globs = {"__c_u": converter.unstructure}
    lines = []
    post_lines = []

    fields = cl.__dataclass_fields__  # type: ignore

    lines.append("def {}(i):".format(fn_name))
    lines.append("    res = {")
    for field_name, f in fields.items():
        override = kwargs.pop(field_name, _neutral)
        default = f.default
        default_factory = f.default_factory
        if f.type is None:
            # No type annotation, doing runtime dispatch.
            if (
                (default is not dataclasses.MISSING)
                or (default_factory is not dataclasses.MISSING)
            ) and (
                (omit_if_default and override.omit_if_default is not False)
                or override.omit_if_default
            ):
                def_name = "__cattr_def_{}".format(field_name)

                if default_factory != dataclasses.MISSING:
                    globs[def_name] = default_factory
                    post_lines.append(
                        "    if i.{name} != {def_name}():".format(
                            name=field_name, def_name=def_name
                        )
                    )
                    post_lines.append(
                        "        res['{name}'] = i.{name}".format(
                            name=field_name
                        )
                    )
                else:
                    globs[def_name] = default
                    post_lines.append(
                        "    if i.{name} != {def_name}:".format(
                            name=field_name, def_name=def_name
                        )
                    )
                    post_lines.append(
                        "        res['{name}'] = __c_u(i.{name})".format(
                            name=field_name
                        )
                    )

            else:
                # No default or no override.
                lines.append(
                    "        '{name}': __c_u(i.{name}),".format(
                        name=field_name
                    )
                )
        else:
            # Do the dispatch here and now.
            type = f.type
            if is_sequence(type):
                type = Sequence
            conv_function = converter._unstructure_func.dispatch(type)
            if (
                (default is not dataclasses.MISSING)
                or (default_factory is not dataclasses.MISSING)
            ) and (
                (omit_if_default and override.omit_if_default is not False)
                or override.omit_if_default
            ):
                def_name = "__cattr_def_{}".format(field_name)

                if default_factory != dataclasses.MISSING:
                    # The default is computed every time.
                    globs[def_name] = default_factory
                    post_lines.append(
                        "    if i.{name} != {def_name}():".format(
                            name=field_name, def_name=def_name
                        )
                    )
                    if conv_function == converter._unstructure_identity:
                        # Special case this, avoid a function call.
                        post_lines.append(
                            "        res['{name}'] = i.{name}".format(
                                name=field_name
                            )
                        )
                    else:
                        unstruct_fn_name = "__cattr_unstruct_{}".format(
                            field_name
                        )
                        globs[unstruct_fn_name] = conv_function
                        post_lines.append(
                            "        res['{name}'] = {fn}(i.{name}),".format(
                                name=field_name, fn=unstruct_fn_name
                            )
                        )
                else:
                    # Default is not a factory, but a constant.
                    globs[def_name] = default
                    post_lines.append(
                        "    if i.{name} != {def_name}:".format(
                            name=field_name, def_name=def_name
                        )
                    )
                    if conv_function == converter._unstructure_identity:
                        post_lines.append(
                            "        res['{name}'] = i.{name}".format(
                                name=field_name
                            )
                        )
                    else:
                        unstruct_fn_name = "__cattr_unstruct_{}".format(
                            field_name
                        )
                        globs[unstruct_fn_name] = conv_function
                        post_lines.append(
                            "        res['{name}'] = {fn}(i.{name})".format(
                                name=field_name, fn=unstruct_fn_name
                            )
                        )
            else:
                # No omitting of defaults.
                if conv_function == converter._unstructure_identity:
                    # Special case this, avoid a function call.
                    lines.append(
                        "    '{name}': i.{name},".format(name=field_name)
                    )
                else:
                    unstruct_fn_name = "__cattr_unstruct_{}".format(field_name)
                    globs[unstruct_fn_name] = conv_function
                    lines.append(
                        "    '{name}': {fn}(i.{name}),".format(
                            name=field_name, fn=unstruct_fn_name
                        )
                    )
    lines.append("    }")

    total_lines = lines + post_lines + ["    return res"]

    eval(compile("\n".join(total_lines), "", "exec"), globs)

    fn = globs[fn_name]

    return fn
