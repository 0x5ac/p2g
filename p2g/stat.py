import abc
import ast
import dataclasses
import string
import typing

from p2g import err
from p2g import gbl
from p2g import nd


WIDE_COMMENT_INDENT = 34
# infront of code which isn't optional block.
OPT_PREFIX = ""
# infront of code which isn't a label
NORMAL_PREFIX = "  "

# args to make comments


class CommentGen:  # pylint: disable=too-few-public-methods
    NONE = "no_comment"
    FROMSRC = "src_comment"
    FAIL = "FAIL"


# make translation maps from what we like
# to what the machine likes.  Like no parens
# in comments and so on
#
OK_CHARS_IN_COMMENTS = (
    string.ascii_lowercase
    + string.digits
    + "+-/* =.[]:,%_><\"'{}#&|^~!"
    + string.ascii_uppercase
)

OK_CHARS_IN_DPRNT = (
    string.ascii_uppercase
    + string.digits
    + "+-/*"
    + "[]"  # need these
    + string.ascii_lowercase  # these work for me, but aren't in the manual
    + ",#:.="
)


def setup_translations(okchars, **kwargs):
    translate_map = {
        **{chr(ch): "*" for ch in range(0, 127)},
        **{x: x for x in (okchars)},
        **kwargs,
    }

    return translate_map


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


class StatBase(abc.ABC):

    pos: ast.AST
    code_prefix: str

    translate_map = setup_translations(OK_CHARS_IN_COMMENTS, **{"(": "[", ")": "]"})

    def __init__(self, *, comtxt=CommentGen.FAIL):
        self.pos = gbl.iface.last_node
        self.comwant = comtxt
        self.code_prefix = gbl.Control.code_prefix

    @classmethod
    def clean_comment_chars(cls, txt: str):
        return "".join(cls.translate_map[ch] for ch in txt)

    # clean comment and remove some redundant
    # strings.
    @classmethod
    def compress_and_clean(cls, line: str):
        guts = cls.clean_comment_chars(line)
        for too_talky in ["p2g.", "var."]:
            guts = guts.replace(too_talky, "")
        if guts.startswith("    "):
            guts = guts[4:]
        return "( " + guts.ljust(30) + ")"

    def talkabout(self, orig):
        return f"{orig} {self.pos} {self.comwant} {self.code_prefix}"

    @gbl.g2l
    def to_line_lhs(self):
        yield "never"  # no cover

    @gbl.g2l
    # asks derived classes to provide code lhs,
    # and then fills in with the common case comment.
    def to_full_lines(self, nest):
        match self.comwant:
            case CommentGen.FROMSRC:
                comtxt = self.compress_and_clean(err.source_from_node(self.pos))
            case CommentGen.NONE:
                comtxt = CommentGen.NONE
            case txt:
                comtxt = self.compress_and_clean(txt)

        # only print a comment once.
        if comtxt == nest.prev_comtxt:
            comtxt = CommentGen.NONE
        else:
            nest.prev_comtxt = comtxt

        code_gen = self.to_line_lhs()

        # code_list is a sequence of gcode, com_txt is a comment
        # which is applied to first line if it can, otherwise
        # is yielded on own line.
        try:
            chunk = next(code_gen)
            prefix_and_code = self.code_prefix + chunk
            code_comment_gap = WIDE_COMMENT_INDENT - len(prefix_and_code)
            indented_comment = " " * code_comment_gap + comtxt

            if comtxt == CommentGen.NONE:
                yield prefix_and_code
            elif gbl.config.narrow_output or code_comment_gap < 0:
                yield comtxt
                yield prefix_and_code
            else:
                yield prefix_and_code + indented_comment

            yield from (self.code_prefix + chunk for chunk in code_gen)
        except StopIteration as exn:  # no cover
            raise AssertionError from exn


class EmacsClientState:
    last_file: str
    last_line: str

    def __init__(self):
        self.last_file = ""
        self.last_line = ""


@dataclasses.dataclass
class Nest:
    first_label: int
    next_label: int
    prev_comtxt: str
    slist: list[StatBase]
    cur: typing.Optional["Nest"] = None
    ecs: EmacsClientState = EmacsClientState()

    def __init__(self):
        self.prev_comtxt = ""
        self.first_label = 1000
        self.next_label = self.first_label
        self.slist = []

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
        super().__init__(comtxt=CommentGen.NONE)
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
                yield "( " + StatBase.clean_comment_chars(line) + " )"
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
        super().__init__(comtxt=CommentGen.NONE)
        self.target = target

    def to_line_lhs(self):
        yield f"{NORMAL_PREFIX}GOTO {self.target.as_gcode_ref()}"


@dataclasses.dataclass
class If(StatBase):
    exp: typing.Any
    on_t: Label

    def __init__(self, exp, on_t: Label):
        super().__init__(comtxt=CommentGen.FROMSRC)
        self.exp = exp
        self.on_t = on_t

    def to_line_lhs(self):
        lhs = f"IF [{nd.to_gcode(self.exp)}] "
        rhs = f"GOTO {self.on_t.as_gcode_ref()}"
        yield f"{NORMAL_PREFIX}{lhs}{rhs}"


@dataclasses.dataclass
class IfSet(StatBase):
    cond: typing.Any
    ass: "Set"

    def __init__(self, cond, ass, comment_txt=CommentGen.FROMSRC):
        super().__init__(comtxt=comment_txt)
        self.cond = cond
        self.ass = ass

    def to_line_lhs(self):
        yield f"{NORMAL_PREFIX}IF [{nd.to_gcode(self.cond)}] {self.ass}"


class Code(StatBase):
    txt: str

    def __init__(self, txtargs, comment_txt=CommentGen.FROMSRC):
        super().__init__(comtxt=comment_txt)
        self.txt = gbl.unwind(txtargs)

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
    translate_map = setup_translations(
        OK_CHARS_IN_DPRNT,
        #        **{x: x.upper() for x in (string.ascii_lowercase)},
    )

    def __init__(self, txt):
        super().__init__(comtxt=CommentGen.NONE)

        self.txt = "".join(Dprint.translate_map[ch] for ch in txt)

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
        comment_txt=CommentGen.FROMSRC,
    ):
        super().__init__(comtxt=comment_txt)
        assert isinstance(lhs, nd.EBase)
        self.args = [lhs, rhs]
        self.msg_txt = msg_txt

    def to_line_lhs(self):
        yield f"{NORMAL_PREFIX}{self}"

    def __repr__(self):
        lhs = nd.to_gcode(self.args[0])
        rhs = nd.to_gcode(self.args[1], modifier=nd.NodeModifier.EMPTY)
        msg_txt = (
            " ( " + self.clean_comment_chars(self.msg_txt) + " )" if self.msg_txt else ""
        )
        return f"{lhs}= {rhs}{msg_txt}"


def append_set(dst, src, comment_txt=CommentGen.FROMSRC):
    if not gbl.same(dst, src):
        add_stat(Set(dst, src, comment_txt=comment_txt))


def code(*txtargs, comment_txt=CommentGen.FROMSRC):
    add_stat(Code(txtargs, comment_txt))


def codenl(txtlst, comment_txt=CommentGen.FROMSRC):
    if isinstance(txtlst, str):
        add_stat(Code(txtlst, comment_txt))
    else:
        for txt in txtlst:
            codenl(txt, comment_txt)
            comment_txt = CommentGen.NONE


# contents evaluate when needed, not when
# created.
class Lazy(StatBase):
    todo: typing.Generator[str, None, None]

    def __init__(self, todo: typing.Generator[str, None, None]):
        super().__init__(comtxt=CommentGen.NONE)
        self.todo = todo

    def to_full_lines(self, _):
        if self.todo:
            yield from self.todo


@dataclasses.dataclass
class LabelDef(StatBase):
    labeldef: Label

    def __init__(self, labeldef: Label):
        self.labeldef = labeldef
        super().__init__(comtxt=CommentGen.NONE)

    def to_line_lhs(self):
        yield f"{self.labeldef.as_gcode_definition()}"


@dataclasses.dataclass
class Percent(StatBase):
    def __init__(self):
        super().__init__(comtxt=CommentGen.NONE)

    def to_line_lhs(self):
        yield "%"


next_label = Nest.get_label
