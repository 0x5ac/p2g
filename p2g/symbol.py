import abc
import collections
import enum
import typing

from p2g import gbl


class Group(enum.IntEnum):
    IGNORE = enum.auto()
    USER = enum.auto()
    VECTOR = enum.auto()
    GOTO = enum.auto()


class Entry(typing.NamedTuple):
    major_key: Group
    key: str
    info: str

    def sort_key(self):
        return f"{self.major_key}{self.key}{self.info}"


# marks class as being able to emit special symtab table entries.
# pylint: disable=too-few-public-methods
class HasToSymTabEntry(abc.ABC):
    @abc.abstractmethod
    def to_symtab_entry(self, _addrs_used) -> typing.Tuple[Group, str]:
        return Group.IGNORE, ""


# symbol tables made by watching every assignment from a vector
# constructor to a name and remembering all the address constants
# used.  walk through all address constants, find the symbols
# assocaited and mark them as useful.  then print them out.
class Table:
    print_all = False
    name_to_thing: typing.Dict[str, list[HasToSymTabEntry]] = collections.defaultdict(
        list
    )
    addrs_used: typing.Set[int] = set()

    @classmethod
    def _remember(cls, key, thing):
        if key in ("xyz", "xy", "x", "y", "z", "val"):
            return
        if cls.print_all or isinstance(thing, HasToSymTabEntry):
            cls.name_to_thing[key].append(thing)

    @classmethod
    def remember_load(cls, key, thing):
        cls._remember(key, thing)

    @classmethod
    def remember_store(cls, key, thing):
        cls._remember(key, thing)

    @classmethod
    # remember a used macro var.
    def add_varref(cls, addr, _pos):
        cls.addrs_used.add(int(addr))

    @classmethod
    def yield_table(cls):
        if not gbl.Control.symbol_table and not cls.print_all:
            return
        lsize = 0
        rsize = 0

        def entries():
            nonlocal lsize
            nonlocal rsize
            for key, things in cls.name_to_thing.items():
                lsize = max(lsize, len(key))
                for thing in things:
                    major_key, info = thing.to_symtab_entry(cls.addrs_used)
                    rsize = max(rsize, len(info))
                    if key and info:
                        yield Entry(major_key, key, info)

        prev = Entry(Group.IGNORE, "", "")
        yield "( Symbol Table )"
        for entry in sorted(entries(), key=Entry.sort_key):
            if prev == entry:
                continue
            if prev.major_key != entry.major_key:
                yield ""
            yield " ( " + entry.key.ljust(lsize) + " : " + entry.info.ljust(rsize) + " )"
            prev = entry
        # blank line after symbol table
        yield ""

    @classmethod
    def reset(cls):
        cls.name_to_thing = collections.defaultdict(list)
        cls.addrs_used = set()
        gbl.Control.symbol_table = False


class TSUB:
    pass
