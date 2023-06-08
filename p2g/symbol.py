from p2g import gbl
from p2g import lib
from p2g import nd
from p2g import stat
from p2g import vector
import typing
import dataclasses
import collections
import itertools


# symbol tables made by watching every assignment from a vector
# constructor to a name and remembering all the address constants
# used.  walk through all address constants, find the symbols
# assocaited and mark them as useful.  then print them out.
@dataclasses.dataclass
class Table:
    print = False

    thing_to_name = {}
    const_to_name = {}

    addrs_used = {}
    # Called for every store to a name, so remember when a vector is
    # given an association.

    @classmethod
    def remember_store(cls, ns, key, thing):
        pass

    @classmethod
    def remember_load(cls, key, thing):
        if isinstance(thing, vector.MemVec):
            cls.thing_to_name[thing] = key
        if isinstance(thing, vector.ConstVec):
            cls.const_to_name[thing] = key

    @classmethod
    def add_varref(cls, addr, pos):
        cls.addrs_used[int(addr)] = pos

    @classmethod
    def yield_lines(cls):
        #        breakpoint()
        if not cls.print:
            return

        # sort all used symbols by address.

        by_addr = sorted(cls.thing_to_name.items(), key=lambda v: v[0].get_address())
        by_const = sorted(cls.const_to_name.items())
        # #  run through all symbols, see if address used.
        # for value, key in by_addr:
        #     try:
        #         addr = value.get_address()

        #         if addr is None:
        #             continue
        #         size = value.nelements()

        #         for i in range(addr.to_int(), addr.to_int() + size):
        #             if i in cls.addrs_used:
        #                 used_symbols.add(key)
        #     except AttributeError:
        #         # some things in table don't have addresses.
        #         pass

        lcols = []
        rcols = []

        # go through table of all known macro names,
        # find out if used, and print nicely.
        for value, key in itertools.chain(by_addr, by_const):
            lcols.append(key)
            rcols.append(value.to_symtab_entry(cls.addrs_used))

        lsize = lib.max_str_len(lcols)
        rsize = lib.max_str_len(rcols)
        for key, value in zip(lcols, rcols):
            yield "( " + key.ljust(lsize) + " : " + value.ljust(rsize) + " )"

    @classmethod
    def reset(cls):
        cls.name_to_vec_store = collections.defaultdict(nd.EBase)
        cls.thing_to_name = {}
        cls.const_to_name = {}
        cls.addrs_used = {}
        cls.print = False
