import contextlib
import dataclasses
import sys
import typing

from p2g import gbl


def max_str_len(lines):
    return len(max(lines, key=len, default=""))


def pad_to_same_width(lines):
    wid = max_str_len(lines)
    res = []
    for line in lines:
        res.append(line.ljust(wid))
    return res


def g2l(generator):
    #    @functools.wraps(generator)
    def g2l_(*args, **kwargs):
        return list(generator(*args, **kwargs))

    return g2l_


class Sentinel:
    def __init__(self, name):
        self.name = name


NOPE = Sentinel("NOPE")


def write_nl_lines(thing, outfile_path):
    if outfile_path == "-":
        for line in thing:
            print(line)
    else:
        with open(outfile_path, "w", encoding="utf-8") as outf:
            for line in thing:
                print(line, file=outf)


def same(lhs, rhs):
    if type(lhs) is not type(rhs):
        return False

    return lhs.same(rhs)


def nljoin(line_list):
    return "\n".join(line_list)


def splitnl(line):
    return line.split("\n")


######################################################################
# i/o redirection


# somewhere to put stdout or stderr during debug tests.
@dataclasses.dataclass
class SimpleOBuf:
    buf: list[str]
    tee: bool

    def __init__(self, tee=False):
        self.buf = []
        self.tee = tee

    def write(self, txt):
        if self.tee:  # no cover
            sys.__stderr__.write(txt)
            sys.__stderr__.flush()

        self.buf.append(txt)

    # def lines(self):
    #     return self.text().split("\n")

    def text(self):
        return "".join(self.buf)


@dataclasses.dataclass
class CaptureO:
    prevout: typing.Any
    preverr: typing.Any
    stdout: SimpleOBuf
    stderr: SimpleOBuf

    def __init__(self, tee=False):
        self.prevout = sys.stdout
        self.preverr = sys.stderr
        self.stdout = SimpleOBuf(tee)
        self.stderr = SimpleOBuf(tee)

    def readouterr(self):
        return self

    @property
    def out(self):
        return self.stdout.text()

    @property
    def err(self):
        return self.stderr.text()

    #    @property
    #    @g2l
    # def all_lines(self):
    #     yield from self.stdout.lines()
    #     yield from self.stderr.lines()

    def __enter__(self):
        sys.stdout = typing.cast(typing.TextIO, self.stdout)
        sys.stderr = typing.cast(typing.TextIO, self.stderr)
        return self

    def __exit__(self, *_):
        sys.stdout = self.prevout
        sys.stderr = self.preverr


@contextlib.contextmanager
def openw(name):
    if str(name) == "-":
        yield sys.stdout
    else:
        with open(name, "w", encoding="utf-8") as wfile:
            yield wfile


class SimpleIBuf:
    fromstdin: str = ""

    # def __new__(cls):
    #     breakpoint()
    #     if not hasattr(cls, "fromstdin"):
    #         cls.fromstdin = sys.stdin.read()
    #     return cls

    def __init__(self):
        if not SimpleIBuf.fromstdin:
            SimpleIBuf.fromstdin = "" if gbl.config.recursive else sys.stdin.read()

    def read(self):
        return SimpleIBuf.fromstdin


@contextlib.contextmanager
def openr(name):
    if str(name) == "-" or not str(name):
        yield SimpleIBuf()
    else:
        with open(name, "r", encoding="utf-8") as rfile:
            yield rfile
