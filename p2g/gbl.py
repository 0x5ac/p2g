import abc
import contextlib
import functools
import sys
import typing


class Config(typing.NamedTuple):
    debug: bool = False
    narrow_output: bool = False
    bp_on_error: bool = False
    boiler_plate: bool = True
    verbose: bool = False
    logio: bool = False
    # overwrittern if we get in via main
    tin_test: bool = True


config = Config()


@contextlib.contextmanager
def save_config(**kwargs):
    global config  # pylint: disable=global-statement
    old = config
    config = config._replace(**kwargs)
    yield

    config = old


class PerTranslation:
    ebss: int
    varrefs: typing.Dict
    last_node: typing.Any

    def __init__(self):
        self.reset()

    def next_bss(self, size):
        addr = self.ebss
        self.ebss += size
        return addr

    def reset(self):
        self.varrefs = {}
        self.ebss = 100

        self.last_node = None


iface = PerTranslation()


def log(*args):
    if config.verbose:
        print(*args)


def sprint(*args):
    print(*args)


# print to redirected stderr
def eprint(*args):
    print(*args, file=sys.stderr)


@functools.cache
def logread(handle):
    res = handle.read()
    if config.logio:
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


class HasToSymTab(abc.ABC):
    user_defined = False

    @abc.abstractmethod
    def to_symtab_entry(self, _addrs_used) -> str:
        return ""
