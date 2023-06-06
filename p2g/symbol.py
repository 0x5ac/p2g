from p2g import err
from p2g import gbl
from p2g import lib
from p2g import stat
from p2g import vector


class Symbols:
    table = None

    def __init__(self):
        object.__setattr__(self, "guts", {})
        object.__setattr__(self, "revguts", {})
        object.__setattr__(self, "read", set())
        Symbols.table = self

    # after init run, clear out all use counts to
    # reset incorrect uswage info made by aliasing refs.

    def init_finished(self):
        object.__setattr__(self, "read", set())

    def table_of_macro_vars(self, varrefs, show_all_names):
        lcols = []
        rcols = []

        # go through table of all known macro names,
        # find out if used, and print nicely.
        for key, value in self.guts.items():
            if not show_all_names and key not in self.read:
                continue

            lcols.append(key)
            rcols.append(value.to_symtab_entry(varrefs))

        lsize = lib.max_str_len(lcols)
        rsize = lib.max_str_len(rcols)
        for key, value in zip(lcols, rcols):
            yield "( " + key.ljust(lsize) + " : " + value.ljust(rsize) + " )"

    def insert_symbol_table(self, show_all_names=False):
        stat.ByLambda.emit(
            lambda: self.table_of_macro_vars(
                gbl.iface.varrefs,
                show_all_names,
            )
        )

    def __getattr__(self, key):
        self.read.add(key)
        return self.guts[key]

    def __setattr__(self, key, value):
        if key in self.guts:
            err.compiler(f"Redefinition of {key}.")
        try:
            newv = vector.wrap_maybe_vec(value)
        except TypeError:
            newv = value

        self.guts[key] = newv
        # keep the most original version of an alias.
        if newv not in self.revguts:
            self.revguts[newv] = key

    @classmethod
    def reset(cls):
        cls.table = None


def table():
    if Symbols.table:
        return Symbols.table.table_of_macro_vars(
            gbl.iface.varrefs,
            False,
        )
    return []
