from p2g import coords
from p2g import gbl
from p2g import haas
from p2g import stat
from p2g import vector
import p2g


def load_tool(tool):
    stat.codenl(f"T{tool:02} M06")


class Optional:
    prev: bool

    def __init__(self):
        self.prev = p2g.Control.block_delete
        p2g.Control.block_delete = True

    def __enter__(self):
        pass

    def __exit__(self, *_):
        p2g.Control.block_delete = self.prev


class WCS:
    def __init__(self, mvar):
        self.prev = coords.Var()
        self.prev.var = haas.LAST_WCS
        self.mvar = mvar
        stat.code(f"G{(mvar.get_address() - 5221)//20 + 54}")

    def __enter__(self):
        return self.mvar

    def __exit__(self, *_):
        stat.code(f"G{self.prev.var}", comment_txt="Restore wcs")


def base_addr(new_base=None):
    #    ._wcs = (val._addr - 5221) // 20 + 54
    if new_base is not None:
        gbl.iface.ebss = new_base
    return gbl.iface.ebss


class BSS:
    def __init__(self):
        self.prev = gbl.iface.ebss
        stat.comment(f"Save bss at {self.prev}")

    def __enter__(self):
        pass

    def __exit__(self, *_):
        gbl.iface.ebss = self.prev
        stat.comment(f"Restore bss to {self.prev}")


# don't fill in the comment text with the  srcline
# since we're printing it.
def message(dst, txt: str):
    stat.code(f"{dst.to_gcode()} = 101 ({txt})", comment_txt=stat.CType.NO_COMMENT)


def address(src):
    # special case for vecs, give address
    # anyway.
    wrapped = vector.wrap_mustbe_vector(src)
    add = wrapped.get_address()
    return add


# pylint: disable=too-few-public-methods
class SupportFuncs:
    need_no_lookahead: bool

    def __init__(self):
        self.need_no_lookahead = False


sf = SupportFuncs()


def on_exit():
    if sf.need_no_lookahead:
        stat.comment("No lookahead")
        stat.codenl(
            [
                "N123",
                "G103 P1",
                "G04 P1",
                "G04 P1",
                "G04 P1",
                "G04 P1",
                "M99",
            ],
            comment_txt=stat.CType.NO_COMMENT,
        )
    sf.need_no_lookahead = False


def no_lookahead():
    sf.need_no_lookahead = True
    stat.codenl("M97 P123", comment_txt="No lookahead")


gbl.on_exit.append(on_exit)
