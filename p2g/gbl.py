import contextlib
import functools
import pathlib
import sys
import typing


class Config(typing.NamedTuple):
    narrow_output: bool = False
    bp_on_error: bool = False
    verbose: int = 0
    no_version: bool = False
    emit_rtl: bool = False
    tin_test: bool = False
    force_no_tintest: bool = False  # noqa


config = Config()


class PerTranslation:
    ebss: int
    varrefs: typing.Dict

    def __init__(self):
        self.reset()

    def next_bss(self, size):
        addr = self.ebss
        self.ebss += size
        return addr

    def reset(self):
        self.varrefs = {}
        self.ebss = 100


iface = PerTranslation()


def log(*args):
    if config.verbose > 1:
        print(*args)


def v1print(*args):
    if config.verbose > 0:
        print(*args)


def v2print(*args):
    if config.verbose > 1:
        print(*args)


def sprint(*args):
    print(*args)


# print to redirected stderr
def eprint(*args):
    print(*args, file=sys.stderr)


@functools.cache
def logread(handle):
    res = handle.read()
    if config.verbose > 2:
        print(res)  # no cover
    return res


def splitnl(line):
    return line.split("\n")


######################################################################
# i/o redirection
@contextlib.contextmanager
def openr(name):
    if str(name) == "-":
        yield sys.stdin, None
    else:
        try:
            with open(name, "r", encoding="utf-8") as rfile:
                yield rfile, None
        except FileNotFoundError as err:
            yield None, err


def g2l(generator):
    def g2l_(*args, **kwargs):
        return list(generator(*args, **kwargs))

    return g2l_


def sentinel():
    # pylint: disable=too-few-public-methods
    class Sentinel:
        pass

    return Sentinel


# open accouting for '-' files.
# sourcing empty file when in test.
@contextlib.contextmanager
def openw(name):
    if str(name) == "-":
        yield sys.stdout
    else:
        with open(name, "w", encoding="utf-8") as wfile:
            yield wfile


def write_nl_lines(thing, outfile_path):
    with openw(outfile_path) as outf:
        for line in thing:
            print(line, file=outf)


def same(lhs, rhs):
    if type(lhs) is not type(rhs):
        return False
    return lhs.same(rhs)


# unwind a list of lists etc can turn generators of lists of strings
# into space joined string.
def unwind1(args):
    if isinstance(args, str):
        yield args
    else:
        for el in args:
            yield from unwind1(el)


def unwind(args):
    return " ".join(unwind1(args))


# find the file if in dist or just checkout out.
def find_ours(filename):
    for topdir in [".", ".."]:
        for subdir in ["tests", "doc", "examples"]:
            look_here = pathlib.Path(__file__).parent / topdir / subdir / filename
            if look_here.exists():
                return look_here.resolve()
    raise FileNotFoundError  # no cover


on_exit: typing.List[typing.Callable] = []
