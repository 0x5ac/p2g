import collections
import typing
from p2g import lib
from p2g import nd


# symbol tables made by watching every assignment from a vector
# constructor to a name and remembering all the address constants
# used.  walk through all address constants, find the symbols
# assocaited and mark them as useful.  then print them out.
class Table:
    print = False
    print_all = False

    # store in this way to keep multiple definitions.
    name_to_thing: typing.Dict[str, typing.Set[nd.HasToSymTab]] = collections.defaultdict(
        set
    )
    addrs_used: typing.Set[int] = set()
    # Called for every store to a name, so remember when a vector is
    # given an association.

    @classmethod
    def remember_store(cls, key, thing):
        cls.remember_load(key, thing)

    @classmethod
    def remember_load(cls, key, thing):
        if key in ("machine", "probe", "relative", "work", "goto", "r9810"):
            return
        try:
            cls.name_to_thing[key].add(thing)
        except TypeError:
            # some things are unhashable.
            pass

    @classmethod
    def add_varref(cls, addr, _pos):
        cls.addrs_used.add(int(addr))

    @classmethod
    def yield_lines(cls):
        #        breakpoint()
        if not cls.print and not cls.print_all:
            return

        # get object names and sort them.
        sorted_names = sorted(cls.name_to_thing.keys(), key=str.casefold)

        # go through table of all known macro names,
        # find out if used, and print nicely.
        def yield_table_part(phase):
            old_rhs = ""
            for key in sorted_names:
                new_values = cls.name_to_thing[key]
                for rhsobj in new_values:
                    try:
                        if not cls.print_all and not rhsobj.user_defined:
                            continue
                        new_rhs = rhsobj.to_symtab_entry(cls.addrs_used)
                        if phase in new_rhs:
                            if new_rhs != old_rhs:
                                yield (key, new_rhs)
                                old_rhs = new_rhs
                    except AttributeError:
                        continue

        @lib.g2l
        def yield_all_parts():
            for phase in ["#", ",", "xyz"]:
                yield from yield_table_part(phase)

        lcols, rcols = zip(*yield_all_parts())
        lsize = lib.max_str_len(lcols)
        rsize = lib.max_str_len(rcols)
        for key, value in zip(lcols, rcols):
            yield "( " + key.ljust(lsize) + " : " + value.ljust(rsize) + " )"

    @classmethod
    def reset(cls):
        cls.name_to_thing = collections.defaultdict(set)
        cls.addrs_used = set()
        cls.print = False
