from p2g import err
from p2g import scalar


NAMES = "xyz"

# special case constant for vectors of naxes size.


class Axes(scalar.Constant):

    def __init__(self):
        super().__init__(len(NAMES))
    @property
    def _value(self):
        return len(NAMES)

    @_value.setter
    def _value(self, inset):
        pass


def low_names_v():
    return NAMES.lower()


def low_names(idx):
    return NAMES[idx]


def axis_name_to_index(axis_char):
    return NAMES.index(axis_char)


def name_to_indexes_list(name: str) -> list[int]:
    try:
        return [axis_name_to_index(ch) for ch in name]
    except ValueError:
        return err.compiler(f"Bad axis letter in '{name}'")
