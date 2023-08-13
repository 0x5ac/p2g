from p2g import coords
from p2g import gbl
from p2g import haas
from p2g import stat
from p2g import vector


NLOOKAHEAD_OFF = 123


# pylint: disable=redefined-builtin
def print(fstr):
    stat.add_stat(stat.Dprint(fstr))


def load_tool(tool):
    stat.codenl(f"T{tool:02} M06")


class Optional:
    prev: str

    def __init__(self):
        self.prev = gbl.Control.code_prefix
        gbl.Control.code_prefix = "/"

    def __enter__(self):
        pass

    def __exit__(self, *_):
        gbl.Control.code_prefix = self.prev


class WCS:
    def __init__(self, mvar):
        self.prev = coords.Var()
        self.prev.var = haas.PREV_WCS
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
    quiet: bool
    prev: int

    def __init__(self, quiet=True):
        self.prev = gbl.iface.ebss
        self.quiet = quiet
        if not self.quiet:
            stat.comment(f"Save bss at {self.prev}")

    def __enter__(self):
        pass

    def __exit__(self, *_):
        gbl.iface.ebss = self.prev
        if not self.quiet:
            stat.comment(f"Restore bss to {self.prev}")


# don't fill in the comment text with the  srcline
# since we're printing it.
def message(dst, txt: str):
    stat.code(f"{dst.to_gcode()} = 101 ({txt})", comment_txt=stat.CommentGen.NONE)


def address(src):
    # special case for vecs, give address
    # anyway.
    wrapped = vector.wrap_mustbe_vector(src)
    add = wrapped.get_address()
    return add


turn_off_lookahead = [
    f"N{NLOOKAHEAD_OFF}",
    "G103 P1",
    "G04 P1",
    "G04 P1",
    "G04 P1",
    "G04 P1",
    "M99",
]


class Lookahead:
    prev_lookahead: bool
    machine_lookahead = True
    head_comment: str
    tail_comment: str
    need_off_code = False

    def __init__(self, lookahead=True):
        self.prev_lookahead = Lookahead.machine_lookahead
        self.set_lookahead(lookahead)

    @classmethod
    def on(cls):
        cls.set_lookahead(True)

    @classmethod
    def off(cls):
        cls.set_lookahead(False)

    @classmethod
    def on_exit(cls):
        cls.machine_lookahead = True

        if not cls.need_off_code:
            return
        stat.codenl(
            turn_off_lookahead,
            comment_txt=stat.CommentGen.NONE,
        )
        cls.need_off_code = False

    @classmethod
    def set_lookahead(cls, lookahead=True):
        if lookahead != Lookahead.machine_lookahead:
            if lookahead:
                stat.codenl("G103")
            else:
                cls.need_off_code = True
                stat.codenl(f"M97 P{NLOOKAHEAD_OFF}")

            Lookahead.machine_lookahead = lookahead

    def __enter__(self):
        #        self.status()
        pass

    def __exit__(self, *_):
        #        self.status()
        self.set_lookahead(self.prev_lookahead)


gbl.on_exit.append(Lookahead.on_exit)
