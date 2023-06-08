from p2g import err
from p2g import gbl
from p2g import scalar
from p2g import stat
from p2g import vector


def set_wcs(new_wcs: vector.Vec):
    gcode = (new_wcs.get_address() - 5221) // 20 + 54
    stat.code(f"G{gcode}")


def base_addr(new_base=None):
    #    ._wcs = (val._addr - 5221) // 20 + 54
    if new_base is not None:
        gbl.iface.ebss = new_base
    return gbl.iface.ebss


def message(dst, txt: str):
    breakpoint()
    stat.code(f"{dst[0]} = 101 ( {txt} )", "")


def as_address(src):
    return src


def address(src):
    # special case for vecs, give address
    # anyway.
    src = vector.wrap_maybe_vec(src)
    add = src.get_address()
    if add is None:
        err.compiler("Can only take address of something with location.")
    return add


def alias(thing):
    return thing
