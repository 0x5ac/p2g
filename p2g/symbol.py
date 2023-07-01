import collections
import typing


# symbol tables made by watching every assignment from a vector
# constructor to a name and remembering all the address constants
# used.  walk through all address constants, find the symbols
# assocaited and mark them as useful.  then print them out.
class Table:
    print = False
    print_all = False

    # store in this way to keep multiple definitions.
    name_to_thing: typing.Dict[str, typing.Set] = collections.defaultdict(set)
    addrs_used: typing.Set[int] = set()

    @classmethod
    def yield_section_lines(cls, phase, key, new_values):
        old_rhs = ""
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

    # go through table of all known macro names,
    # find out if used, and print nicely.
    @classmethod
    def yield_section(cls, phase, sorted_names):
        for key in sorted_names:
            new_values = cls.name_to_thing[key]

            yield from cls.yield_section_lines(phase, key, new_values)

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
    def yield_table(cls):
        #        breakpoint()
        if not cls.print and not cls.print_all:
            return

        # get object names and sort them.
        sorted_names = sorted(cls.name_to_thing.keys(), key=str.casefold)

        def yield_all_sections():
            for phase in ["#", ",", "xyz"]:
                yield from cls.yield_section(phase, sorted_names)

        lcols, rcols = zip(*yield_all_sections())

        def max_str_len(lines):
            return len(max(lines, key=len, default=""))

        lsize = max_str_len(lcols)
        rsize = max_str_len(rcols)
        for key, value in zip(lcols, rcols):
            yield "( " + key.ljust(lsize) + " : " + value.ljust(rsize) + " )"

    @classmethod
    def reset(cls):
        cls.name_to_thing = collections.defaultdict(set)
        cls.addrs_used = set()
        cls.print = False
