import abc
import dataclasses
import itertools
import typing

from p2g import err
from p2g import gbl
from p2g import lib
from p2g import nd


COMMENT_INDENT = 34


# infront of code which isn't a label
NORMAL_PREFIX = "  "


@dataclasses.dataclass
class Label:
    idx: int
    used: bool

    def __init__(self, idx: int):
        self.idx = idx
        self.used = False

    def as_gcode_ref(self):
        return f"{self.idx}"

    def as_gcode_definition(self):
        return f"N{self.idx}"


# auto comment is a comment which comes from
# the source, rather than being typed.
# we take liberties to increase information density.


# remove bad chars from a comment.
def clean_comment_chars(txt: str):
    res = ""
    for ch in txt:
        match ch:
            case "(":
                ch = "["
            case ")":
                ch = "]"

        res += ch
    return res


def compress_and_clean(line: str):
    guts = clean_comment_chars(line)
    for too_talky in ["p2g.", "var."]:
        guts = guts.replace(too_talky, "")

    if guts.startswith("    "):
        guts = guts[4:]

    return "( " + guts.ljust(30) + ")"


@dataclasses.dataclass
class StatBase(abc.ABC):
    _comment: str

    def __init__(self, comment_txt=None):
        self.pos = err.state.last_pos

        # if specifically asked for none, then we're done.
        if comment_txt == "<none>":
            self._comment = ""
        else:
            # no comment supplied, then use source line.
            if not comment_txt:
                comment_txt = err.src_code_from_node_place(self.pos)
            comment_txt = compress_and_clean(comment_txt)
            self._comment = comment_txt

    def to_line_lhs(self) -> list[str]:
        raise AssertionError

    @gbl.g2l
    def to_full_lines(self, blockstate):
        comtxt = self._comment
        if comtxt == blockstate.prev_comtxt:
            comtxt = ""
        else:
            blockstate.prev_comtxt = comtxt

        for code_txt, com_txt in itertools.zip_longest(
            self.to_line_lhs(),
            [comtxt],
            fillvalue="",
        ):
            yield from self.yield_lines(code_txt, com_txt)

    def yield_lines(self, code_txt, com_txt):
        # If code would leak into comment, put out the comment on
        # own line.  If in narrow mode (by option,  or default if
        # in pytest or debug), put on own line too.

        if gbl.config.narrow_output:
            comment_indent = 0
        else:
            comment_indent = COMMENT_INDENT

        code_comment_gap = comment_indent - len(code_txt)
        if code_comment_gap < 0:
            first_line = com_txt
            second_line = code_txt
        else:
            if com_txt:
                first_line = code_txt + " " * code_comment_gap + com_txt
            else:
                first_line = code_txt
            second_line = ""
        if first_line:
            yield first_line
        if second_line:
            yield second_line


@dataclasses.dataclass
class Nest:
    first_label: int
    next_label: int

    prev: "Nest"
    slist: list[StatBase]
    cur: "Nest" = typing.cast("Nest", None)

    def __init__(self):
        self.prev = Nest.cur
        if gbl.config.tin_test or not Nest.cur:
            self.first_label = 1000
        else:
            self.first_label = self.prev.first_label + 1000

        Nest.cur = self
        self.next_label = self.first_label
        self.slist = []

    def get_label(self):
        res = self.next_label
        self.next_label += 1
        return Label(res)

    @classmethod
    def add_stat(cls, stat):
        Nest.cur.slist.append(stat)

    @gbl.g2l
    def to_full_lines(self):
        class BS:
            prev_comtxt = ""

        blockstate = BS()
        for line in self.slist:
            yield from line.to_full_lines(blockstate)

    def __enter__(self):
        return self

    def __exit__(self, *_exn):
        Nest.cur = self.prev


class CommentLines(StatBase):
    def __init__(self, lines):
        super().__init__()
        self.lines = lines

    def to_full_lines(self, _):
        lines = list(map(str, self.lines))

        def max_str_len(lines):
            return len(max(lines, key=len, default=""))

        def pad_to_same_width(lines):
            wid = max_str_len(lines)
            res = []
            for line in lines:
                res.append(line.ljust(wid))
            return res

        lines = pad_to_same_width(lines)

        for line in lines:
            if line.strip():
                yield "( " + clean_comment_chars(line) + " )"
            else:
                yield ""


def add_stat(stat):
    gbl.log(f"Adding {stat}")
    Nest.add_stat(stat)


def comment(*lines):
    add_stat(CommentLines(" "))
    add_stat(CommentLines(lines))


def com(*lines):
    add_stat(CommentLines(lines))


@dataclasses.dataclass
class Goto(StatBase):
    target: Label

    def __init__(self, target: Label):
        super().__init__()
        self.target = target

    def to_line_lhs(self):
        yield f"  GOTO {self.target.as_gcode_ref()}"


@dataclasses.dataclass
class If(StatBase):
    exp: typing.Any
    on_t: Label

    def __init__(self, exp, on_t: Label):
        super().__init__()

        self.exp = exp
        self.on_t = on_t

    def to_line_lhs(self):
        lhs = f"IF [{nd.to_gcode(self.exp)}] "
        rhs = f"GOTO {self.on_t.as_gcode_ref()}"
        yield NORMAL_PREFIX + lhs + rhs


@dataclasses.dataclass
class Code(StatBase):
    txt: str

    def __init__(self, txtargs, comment_txt=""):
        super().__init__(comment_txt=comment_txt)

        self.txt = lib.unwind(txtargs)

    def to_line_lhs(self):
        yield NORMAL_PREFIX + self.txt


@dataclasses.dataclass
class Dprint(StatBase):
    txt: str

    def __init__(self, txt):
        super().__init__("<none>")
        self.txt = txt

    def to_line_lhs(self):
        yield "DPRNT[" + self.txt + "]"


class Set(StatBase):
    lhs: nd.EBase
    rhs: nd.EBase

    def __init__(self, lhs: nd.EBase, rhs: nd.EBase, comtxt: str = ""):
        super().__init__(comtxt)
        assert isinstance(lhs, nd.EBase)
        self.lhs = lhs
        self.rhs = rhs

    @gbl.g2l
    def to_line_lhs(self):
        lhs = self.lhs.to_gcode(nd.NodeModifier.EMPTY)
        rhs = self.rhs.to_gcode(nd.NodeModifier.ARGUMENT)
        yield f"{NORMAL_PREFIX}{lhs}= {rhs}"


def append_set(dst, src, comtxt=""):
    if not lib.same(dst, src):
        add_stat(Set(dst, src, comtxt))


def code(*txtargs, comment_txt: str = ""):
    add_stat(Code(txtargs, comment_txt=comment_txt))


def codenl(txtlst, comtxt: str = ""):
    if isinstance(txtlst, str):
        add_stat(Code(txtlst, comtxt))
    else:
        for txt in txtlst:
            codenl(txt, comtxt)
            comtxt = ""


# take list of args and chain them
# and then join. Take care with strings.


@dataclasses.dataclass
class LabelDef(StatBase):
    labeldef: Label

    def __init__(self, labeldef: Label):
        self.labeldef = labeldef
        super().__init__()

    def to_line_lhs(self):
        yield f"{self.labeldef.as_gcode_definition()}"


def next_label():
    return Nest.cur.get_label()


def dprint(fstr):
    fstr = fstr.replace(" ", "*")
    add_stat(Dprint(fstr))


# when run from tests, sometimes we get generated
# statements by surprise.
top = Nest()
