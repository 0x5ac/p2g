import ast
import contextlib
import functools
import pathlib
import sys
import typing


class Config(typing.NamedTuple):
    narrow_output: bool = False
    bp_on_error: bool = False
    verbose: int = 0
    no_id: bool = False
    short_filenames: bool = False
    in_pytestwant: bool = False
    first_line: int = -1


config = Config()

# pylint: disable=too-few-public-methods


class Control:
    code_prefix = ""
    symbol_table = False
    emacsclient = False


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


######################################################################


# needs to be cacheable cause stdin is possible.
# needs to be clearable because get called with stdin
# with different contents


@functools.cache
def get_lines(name):
    # pylint: disable=consider-using-with
    if str(name) == "-":
        file = sys.stdin
    else:
        file = open(name, encoding="utf-8")

    return file.read().split("\n")

    # print("IN GETLINES ", name)
    # # parse command line
    # if str(name) != "-":
    #     inf = open(name, encoding="utf-8")
    #     guts = inf.read().split("\n")

    # else:
    #     guts = sys.stdin.read().split("\n")
    #     print("READ", guts)

    # return guts


def g2l(generator):
    def g2l_(*args, **kwargs):
        return list(generator(*args, **kwargs))

    return g2l_


# generator returning one string from a yield of many
def g2s(generator):
    def g2s_(*args, **kwargs):
        return "".join(generator(*args, **kwargs))

    return g2s_


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
        for subdir in ["docs", "examples"]:
            look_here = pathlib.Path(__file__).parent / topdir / subdir / filename
            if look_here.exists():
                return look_here.resolve()
    raise FileNotFoundError  # no cover


on_exit: typing.List[typing.Callable] = []


def set_ast_file_name(node: ast.AST, name):

    setattr(node, "file_name", name)


def ast_file_name(node: ast.AST):
    return getattr(node, "file_name")


def make_fake_node(filename, lineno, offset, end_offset):
    fake_node = ast.AST()
    set_ast_file_name(fake_node, filename)
    fake_node.lineno = lineno
    fake_node.col_offset = offset
    fake_node.end_col_offset = end_offset
    return fake_node


ASTNONE = make_fake_node(None, 1, 0, 0)


class PerTranslation:
    ebss: int
    varrefs: typing.Dict
    last_node: ast.AST

    def __init__(self):
        self.ebss = 100

        self.varrefs = {}
        self.last_node = ASTNONE

    def next_bss(self, size):
        addr = self.ebss
        self.ebss += size
        return addr


iface: "PerTranslation" = PerTranslation()


def reset():
    #
    # pylint: disable=global-statement
    global iface
    get_lines.cache_clear()
    iface = PerTranslation()
