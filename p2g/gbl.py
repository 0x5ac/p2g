import typing


class Config:
    opt_relative_lines: bool
    opt_relative_paths: bool
    debug: bool
    opt_narrow_output: bool
    in_pytest: bool
    bp_on_error: bool
    recursive: bool

    def __init__(self):
        self.bp_on_error = False
        self.opt_relative_lines = False
        self.opt_relative_paths = False
        self.opt_narrow_output = False
        self.debug = False
        self.in_pytest = True
        self.recursive = False

    @property
    def relative_lines(self):
        return self.opt_relative_lines or self.in_pytest

    @property
    def relative_paths(self):
        return self.opt_relative_paths or self.in_pytest

    @property
    def narrow_output(self):
        return self.opt_narrow_output or self.in_pytest


config = Config()


class PerTranslation:
    ebss: int
    varrefs: typing.Dict
    last_node: typing.Any

    def next_bss(self, size):
        addr = self.ebss
        self.ebss += size
        return addr

    def __init__(self):
        self.reset()

    def reset(self):
        self.varrefs = {}
        self.ebss = 100

        self.last_node = None

    #        self.next_label = 1000

    def add_varref(self, idx):
        try:
            self.varrefs[idx.to_int()] = True
        except NotImplementedError:
            pass


iface = PerTranslation()
