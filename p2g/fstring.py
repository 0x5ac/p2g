# turn fstrings for print into the right runes for dprnt
import ast
import re

import p2g

from p2g import axis
from p2g import gbl
from p2g import nd
from p2g import op


# takes a python format and turns it into something
# in the new formatty way.
#    ###.## makes f3.2
#     ?xyz  makes xyz only show up between elements.
#     A     makes axis letter print
#     !     makes axis number print
#   anything else is just copied out.
def py_fmt_to_gcode(fmt):

    if fmt in ("", "f"):
        return "#####.###"

    if fmt[0].isdigit() or fmt[0] == ".":
        # standard f fmt.

        groups = re.match("(?P<n_total>\\d*).(?P<n_frac>\\d*)(f?)(?P<rest>:.*)?", fmt)
        if groups:
            gdict = groups.groupdict()
            n_total = int(gdict["n_total"])
            n_frac = gdict.get("n_frac")

            if n_frac == "":
                n_frac = 0
            else:
                n_frac = int(gdict["n_frac"])
            restp = gdict["rest"] if gdict["rest"] else ""
            n_mant = max(n_total - n_frac - 1, 1)
            return ("#" * n_mant) + "." + ("#" * n_frac) + restp
    return fmt


@gbl.g2s
def expand_magic_chars(gcode_fmt, vector_idx):
    for el in gcode_fmt:
        if el == "@":
            yield axis.hi_names(vector_idx)
        elif el == "!":
            yield str(vector_idx)
        else:
            yield el


def get_number_insert(val, prefix_digits, suffix_digits):
    konst = op.get_constant(val)

    if konst:
        pyfmt = f"{prefix_digits+suffix_digits + 1}.{suffix_digits}f"
        number_insert = format(konst.to_float(), pyfmt)
    else:
        node = op.reload(val)
        number_insert = nd.to_gcode(node) + f"[{prefix_digits}{suffix_digits}]"
    return number_insert


# passed a magical my format gcode format,
# like "####.###, " which will generate
# a dprint foo[42], bar[42], zap[42]
# etc
@gbl.g2s
def format_for_one(val, gcode_fmt, idx):

    groups = re.match(
        "(?P<prefix>[^#?]*)"
        "((?P<mant>#*)\\.?(?P<frac>#*))?"
        "(?P<suffix>[^?]*)(\\?(?P<between>.*))?",
        gcode_fmt,
    )

    if groups:
        gdict = groups.groupdict()
        if idx > 0 and gdict["between"]:
            yield from expand_magic_chars(gdict["between"], idx)
        yield from (expand_magic_chars(gdict["prefix"], idx))
        yield from (get_number_insert(val, len(gdict["mant"]), len(gdict["frac"])))
        yield from (expand_magic_chars(gdict["suffix"], idx))


@gbl.g2s
def format_expand(val, gcode_fmt):
    for (idx, el) in enumerate(val.everything()):
        yield format_for_one(el, gcode_fmt, idx)


def format_for_n(val, fmt):
    if isinstance(val, str):
        return val
    if not fmt:
        fmt = "7.2f"
    gcode_fmt = py_fmt_to_gcode(fmt)
    if nd.get_nelements(val) > 1:
        return format_expand(val, gcode_fmt)
    return format_for_one(p2g.scalar.wrap_scalar(val), gcode_fmt, 0)


def one_float(interp, value):

    val = interp.visit(value.value)

    fmt = interp.visit(value.format_spec)
    el = format_for_n(val, fmt)
    return el


@gbl.g2s
def joinedstr(interp, node):
    for value in node.values:
        match type(value):
            case ast.Constant:
                yield value.value
            case _:
                el = one_float(interp, value)
                yield el
