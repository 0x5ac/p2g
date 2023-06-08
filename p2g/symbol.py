from os import sched_get_priority_max
import p2g
from p2g import gbl
from p2g import lib
from p2g import nd
from p2g import stat
from p2g import vector
from p2g import goto
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

    # store in this way to keep multiple definitions.
    name_to_thing = collections.defaultdict(set)
    addrs_used = {}
    # Called for every store to a name, so remember when a vector is
    # given an association.

    @classmethod
    def remember_store(cls, ns, key, thing):
        cls.remember_load(key, thing)

    @classmethod
    def remember_load(cls, key, thing):
        try:
            cls.name_to_thing[key].add(thing)
        except TypeError:
            # some things are unhashable.
            pass

    @classmethod
    def add_varref(cls, addr, pos):
        cls.addrs_used[int(addr)] = pos

    @classmethod
    def yield_lines(cls):
        #        breakpoint()
        if not cls.print:
            return

        # get object names and sort them.
        sorted_names = sorted(cls.name_to_thing.keys(), key=str.casefold)
        lcols = []
        rcols = []
        old_rhs = ""
        # go through table of all known macro names,
        # find out if used, and print nicely.
        for phase in ["#", ",", "xyz"]:
            for key in sorted_names:
                new_values = cls.name_to_thing[key]
                for rhsobj in new_values:
                    try:
                        if not rhsobj.user_defined:
                            continue
                    except AttributeError:
                        continue
                    new_rhs = rhsobj.to_symtab_entry(cls.addrs_used)
                    if phase in new_rhs:
                        if new_rhs != old_rhs:
                            lcols.append(key)
                            rcols.append(new_rhs)
                            old_rhs = new_rhs

        lsize = lib.max_str_len(lcols)
        rsize = lib.max_str_len(rcols)
        for key, value in zip(lcols, rcols):
            yield "( " + key.ljust(lsize) + " : " + value.ljust(rsize) + " )"

    @classmethod
    def reset(cls):
        cls.name_to_thing = collections.defaultdict(set)
        cls.addrs_used = {}
        cls.print = False
