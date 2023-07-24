import abc
import dataclasses
import itertools
import typing

import p2g
from p2g import err
from p2g import gbl
from p2g import nd


WIDE_COMMENT_INDENT = 34
# infront of code which isn't optional block.
OPT_PREFIX = ""
# infront of code which isn't a label
NORMAL_PREFIX = "  "

# args to make comments


class CType:  # pylint: disable=too-few-public-methods
    NO_COMMENT = "no_comment"
    SRC_COMMENT = "src_comment"
    FAIL_COMMENT = "FAIL"


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
    for el in txt:
        match el:
            case "(":
                el = "["
            case ")":
                el = "]"
        res += el
    return res


def compress_and_clean(line: str):
    guts = clean_comment_chars(line)
    for too_talky in ["p2g.", "var."]:
        guts = guts.replace(too_talky, "")
    if guts.startswith("    "):
        guts = guts[4:]
    return "( " + guts.ljust(30) + ")"


class StatBase(abc.ABC):
    _comment: str

    def __init__(self, *, comment_txt=CType.FAIL_COMMENT):
        if p2g.Control.block_delete == True:
            self.prefix = "/ "
        else:
            self.prefix = ""
        self.pos = err.state.last_pos
        assert comment_txt is not None
        assert comment_txt != CType.FAIL_COMMENT
        # if specifically asked for no comment, then we're done.
        if comment_txt == CType.NO_COMMENT:
            self._comment = ""
            return
        # no comment supplied, then use source line.
        if comment_txt == CType.SRC_COMMENT:
            comment_txt = err.src_code_from_node_place(self.pos)
        comment_txt = compress_and_clean(comment_txt)
        self._comment = comment_txt

    @abc.abstractmethod
    def rtl_arg_info_(self):
        return []

    @abc.abstractmethod
    def rtl_get_arg_(self, _idx):
        raise IndexError

    def talkabout(self, orig):
        return f"{orig} {self._comment}"

    def to_line_lhs(self) -> list[str]:
        raise AssertionError

    @gbl.g2l
    def stat_to_rtl(self):

        yield from nd.to_rtl(self)

    @gbl.g2l
    def to_full_lines(self, nest):
        comtxt = self._comment
        if comtxt == nest.prev_comtxt:
            comtxt = ""
        else:
            nest.prev_comtxt = comtxt
        for code_txt, com_txt in itertools.zip_longest(
            self.to_line_lhs(),
            [comtxt],
            fillvalue="",
        ):
            yield from self.yield_lines(code_txt, com_txt)

    def yield_lines(self, code_txt, com_txt):
        # narrow output - emit comment and then code on different
        # lines, then done.  If code is too wide for comment to start
        # in the right place, also done.
        code_comment_gap = WIDE_COMMENT_INDENT - len(code_txt)
        if not gbl.config.narrow_output and code_comment_gap >= 0 and com_txt:
            code_txt = code_txt + " " * code_comment_gap + com_txt
            com_txt = ""
        if com_txt:
            yield com_txt
        if code_txt:
            yield self.prefix + code_txt


@dataclasses.dataclass
class Nest:
    first_label: int
    next_label: int
    prev_comtxt: str
    slist: list[StatBase]
    cur: typing.Optional["Nest"] = None

    def __init__(self):
        self.prev_comtxt = ""
        self.first_label = 1000
        self.next_label = self.first_label
        self.slist = []

    def nest_to_rtl(self):

        for stat in self.slist:

            yield "".join(stat.stat_to_rtl())

    @classmethod
    def get_label(cls):
        assert cls.cur is not None
        res = cls.cur.next_label
        cls.cur.next_label += 1
        return Label(res)

    @classmethod
    def add_stat(cls, stat):
        gbl.v2print(f"Adding {stat}")
        if Nest.cur is None:
            return
        Nest.cur.slist.append(stat)

    @gbl.g2l
    def to_full_lines(self):
        for line in self.slist:
            yield from line.to_full_lines(self)

    @classmethod
    def __enter__(cls):
        assert cls.cur is None
        cls.cur = Nest()
        return cls.cur

    @classmethod
    def __exit__(cls, *_exn):
        cls.cur = None


class CommentLines(StatBase):
    def __init__(self, lines):
        super().__init__(comment_txt=CType.NO_COMMENT)
        self.lines = lines

    def rtl_arg_info_(self):
        return []

    def rtl_get_arg_(self, _idx):
        raise AssertionError

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


add_stat = Nest.add_stat


def comment(*lines):
    add_stat(CommentLines(" "))
    add_stat(CommentLines(lines))


def com(*lines):
    add_stat(CommentLines(lines))


@dataclasses.dataclass
class Goto(StatBase):
    target: Label

    def __init__(self, target: Label):
        super().__init__(comment_txt=CType.SRC_COMMENT)
        self.target = target

    def to_line_lhs(self):
        yield f"{NORMAL_PREFIX}GOTO {self.target.as_gcode_ref()}"

    def rtl_arg_info_(self):
        return ["labelref"]

    def rtl_get_arg_(self, _idx):
        return self.target


@dataclasses.dataclass
class If(StatBase):
    exp: typing.Any
    on_t: Label

    def __init__(self, exp, on_t: Label):
        super().__init__(comment_txt=CType.SRC_COMMENT)
        self.exp = exp
        self.on_t = on_t

    def rtl_arg_info_(self):
        return ["exp", "labelref"]

    def rtl_get_arg_(self, idx):
        if idx == 0:
            return self.exp
        return self.on_t

    def to_line_lhs(self):
        lhs = f"IF [{nd.to_gcode(self.exp)}] "
        rhs = f"GOTO {self.on_t.as_gcode_ref()}"
        yield f"{NORMAL_PREFIX}{lhs}{rhs}"


@dataclasses.dataclass
class IfSet(StatBase):
    cond: typing.Any
    ass: "Set"

    def __init__(self, cond, ass, comment_txt=CType.SRC_COMMENT):
        super().__init__(comment_txt=comment_txt)
        self.cond = cond
        self.ass = ass

    def rtl_arg_info_(self):
        return ["exp", "dst", "src"]

    def rtl_get_arg_(self, idx):
        if idx == 0:
            return self.cond

        if idx == 1:
            return self.ass.args[0]
        return self.ass.args[1]

    def to_line_lhs(self):
        yield f"{NORMAL_PREFIX}IF [{nd.to_gcode(self.cond)}] {self.ass}"


class Code(StatBase):
    txt: str

    def __init__(self, txtargs, comment_txt=CType.SRC_COMMENT):
        super().__init__(comment_txt=comment_txt)
        self.txt = gbl.unwind(txtargs)

    def rtl_arg_info_(self):
        return ["?string"]

    def rtl_get_arg_(self, _idx):
        return self.txt

    def to_line_lhs(self):
        if self.txt and (self.txt[0] in "O%LN"):
            yield self.txt
        else:
            yield f"{NORMAL_PREFIX}{self.txt}"

    def __repr__(self):
        return self.talkabout(f"Code: {self.txt}")


@dataclasses.dataclass
class Dprint(StatBase):
    txt: str

    def __init__(self, txt):
        super().__init__(comment_txt=CType.NO_COMMENT)
        self.txt = txt

    def rtl_get_arg_(self, _idx):
        raise AssertionError

    def rtl_arg_info_(self):
        return []

    def to_line_lhs(self):
        yield "DPRNT[" + self.txt + "]"


class Set(StatBase):
    args: list[nd.EBase]
    msg_txt: str

    def __init__(
        self,
        lhs: nd.EBase,
        rhs: nd.EBase,
        *,
        msg_txt: str = "",
        comment_txt=CType.SRC_COMMENT,
    ):
        super().__init__(comment_txt=comment_txt)
        assert isinstance(lhs, nd.EBase)
        self.args = [lhs, rhs]
        self.msg_txt = msg_txt

    @gbl.g2l
    def to_line_lhs(self):
        yield f"{NORMAL_PREFIX}{self}"

    def rtl_arg_info_(self):
        return ["dst", "src"]

    def rtl_get_arg_(self, idx):
        return self.args[idx]

    def __repr__(self):
        lhs = nd.to_gcode(self.args[0])
        rhs = nd.to_gcode(self.args[1], modifier=nd.NodeModifier.ARGUMENT)
        msg_txt = " ( " + clean_comment_chars(self.msg_txt) + " )" if self.msg_txt else ""
        return f"{lhs}= {rhs}{msg_txt}"


def append_set(dst, src, comment_txt=CType.SRC_COMMENT):
    if not gbl.same(dst, src):
        add_stat(Set(dst, src, comment_txt=comment_txt))


def code(*txtargs, comment_txt=CType.SRC_COMMENT):
    add_stat(Code(txtargs, comment_txt))


def codenl(txtlst, comment_txt=CType.SRC_COMMENT):
    if isinstance(txtlst, str):
        add_stat(Code(txtlst, comment_txt))
    else:
        for txt in txtlst:
            codenl(txt, comment_txt)
            comment_txt = CType.NO_COMMENT


# contents evaluate when needed, not when
# created.
class Lazy(StatBase):
    todo: typing.Generator[str, None, None]

    def __init__(self, todo: typing.Generator[str, None, None]):
        super().__init__(comment_txt=CType.NO_COMMENT)
        self.todo = todo

    def rtl_arg_info_(self):
        return []

    def rtl_get_arg_(self, _idx):
        raise AssertionError

    @gbl.g2l
    def to_full_lines(self, _):
        if self.todo:
            yield from self.todo


@dataclasses.dataclass
class LabelDef(StatBase):
    labeldef: Label

    def __init__(self, labeldef: Label):
        self.labeldef = labeldef
        super().__init__(comment_txt=CType.NO_COMMENT)

    def rtl_arg_info_(self):
        return ["labeldef"]

    def rtl_get_arg_(self, _idx):

        return self.labeldef

    def to_line_lhs(self):
        yield f"{self.labeldef.as_gcode_definition()}"


def dprint(fstr):
    fstr = fstr.replace(" ", "*")
    add_stat(Dprint(fstr))


next_label = Nest.get_label
