import dataclasses
import pathlib
import sys
import typing

from p2g import gbl
from p2g import lib


@dataclasses.dataclass
class NodePlace:
    col_offset_first: int
    col_offset_past: int
    lineno: int
    funcname: str
    filename: str


@dataclasses.dataclass
class State:
    last_pos: NodePlace

    def __init__(self):
        self.last_pos = NodePlace(0, 0, 0, "", "")


state = State()


def mark_pos(last_pos):
    state.last_pos = last_pos


def src_code_from_line_near(pos, lineno):
    with lib.openr(pos.filename) as inf:
        src = inf.read()
        lines = lib.splitnl(src)
        return lines[lineno - 1]


def src_code_from_node_place(pos):
    return src_code_from_line_near(pos, pos.lineno)


def note_from_node_place(pos, absolute_lines, topfn=None):
    relfixer = 1
    if (gbl.config.relative_lines or (not absolute_lines)) and topfn is not None:
        relfixer = topfn.__code__.co_firstlineno

    filename = pos.filename
    if gbl.config.relative_paths:
        orig = pathlib.Path(filename)
        filename = "/".join(orig.parts[-3:])

    reportable_line = pos.lineno - relfixer + 1
    col_offset = pos.col_offset_first
    col_width = pos.col_offset_past - col_offset
    pfx = ":".join(
        [
            str(filename),
            str(reportable_line),
            str(pos.col_offset_first),
            str(pos.col_offset_past),
            " ",
        ]
    )

    return pfx, " " * (len(pfx) + col_offset) + "^" * col_width


class CompilerError(Exception):
    pos: NodePlace
    message: str

    # def __str__(self):
    #     return str(self.message)

    def __init__(self, pos, message: str):
        super().__init__()
        self.pos = pos
        self.message = message

    def error_lines(self, absolute_lines, topfn):
        sourceline = src_code_from_node_place(self.pos)
        pfx, carat = note_from_node_place(self.pos, absolute_lines, topfn)

        return [self.message, pfx + sourceline, carat]

    def report_error(self, outf=None, absolute_lines=True, topfn=None):
        if outf is None:
            outf = sys.stderr

        for line in self.error_lines(absolute_lines, topfn):
            print(line, file=outf)


def compiler(message, exc=None, err_pos=None) -> typing.NoReturn:
    if gbl.config.bp_on_error:  # for debug
        breakpoint()
        breakpoint()

    if not err_pos:
        err_pos = state.last_pos
    raise CompilerError(err_pos, str(message)) from exc
