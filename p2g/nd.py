import enum


class NodeModifier(enum.IntFlag):
    # so 0 is an error
    EMPTY = enum.auto()
    ADDRESS = enum.auto()
    ARGUMENT = enum.auto()
    NOSPACE = enum.auto()


# common base class for scalar and vector.
class EBase:
    def to_gcode(self, _modifier: NodeModifier) -> str:
        return ""  # no cover

    def to_symtab_entry(self, varrefs):
        return str(self)

    def symbol_name(self, _x):
        pass

    def symbol_key(self):
        return ""


DECIMALS = 4


def to_gcode_from_float(thing):
    res = str(round(float(thing), DECIMALS))
    if res.endswith(".0"):
        res = res[:-1]
    return res


def to_gcode(thing, modifier=NodeModifier.EMPTY) -> str:
    if isinstance(thing, (float, int)):
        return to_gcode_from_float(thing)

    return thing.to_gcode(modifier)
