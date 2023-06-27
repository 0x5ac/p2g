import contextlib
import pathlib
import sys


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


def nljoin(line_list):
    return "\n".join(line_list)


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
    for dir in [".", ".."]:
        for subdir in ["tests", "doc", "examples"]:
            look_here = pathlib.Path(__file__).parent / dir / subdir / filename

            if look_here.exists():
                return look_here.resolve()

    raise FileNotFoundError  # no cover
