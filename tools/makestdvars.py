#! /usr/bin/env python

import contextlib

# pylint: disable=too-few-public-methods
import pathlib
import re
import sys
import typing

import docopt
import rich.console

from rich.table import Table


class Secs(float):
    pass


class Time(float):
    pass


class Percent(float):
    pass


class PalletTable:
    pass


class Offsets:
    pass


NAME_WIDTH = 25
SIZE_WIDTH = 10
RANGE_WIDTH = 20


DOC = """

Creates machine specific definitions and doc.

Usage:
   makestdvars  [--txt=<txt>] [--dev=<dev>]
                [--py=<py>] [--org=<org>]
                [--html=<html>] [--dpy=<dpy>]
"""

# three sorts of py outputs, as an arrays,  as attributes to a
# class, or straight into global names.

INTO_ARRAY = 0
INDENT = "    "
INTO_ATTR = 0
INDENT = "    "

INTO_GBL = 1
INDENT = ""


def def_prefix(key):
    if INTO_ARRAY:  # no cover
        return f'dst["{key}"]'
    if INTO_ATTR:  # no cover
        return f"dst.{key}"

    return f"{key}"


# could put ".coords" here to make
# haas.py more explicit.
MAKE_PFX = ""

# pylint: disable=invalid-name
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-statements


def NAXES():
    return 20


def org_cell(width=123, align="rjust", wrap_code=True, text="text"):
    opencode = "<code>"
    closecode = "</code>"
    opencode = "="
    closecode = "="
    if wrap_code:
        width -= len(opencode) + len(closecode)
        text = f"{opencode}{text}{closecode}"
    match align:
        case "right":
            text = text.rjust(width)
        case "center":
            text = text.center(width)
        case _:  # no cover
            raise NotImplementedError
    return text


def org_line(sep, wrap_code=False, name="no name", size=None, arange="no range"):
    return (
        "".join(
            [
                "|",
                org_cell(NAME_WIDTH, "right", wrap_code=wrap_code, text=name),
                sep,
                org_cell(SIZE_WIDTH, "right", wrap_code=wrap_code, text=str(size)),
                sep,
                org_cell(RANGE_WIDTH, "center", wrap_code=wrap_code, text=arange),
                "|",
            ]
        )
    ) + "\n"


class MacroVar:
    #    size: int
    name: str
    typ: typing.Type

    def __init__(
        self,
        *,
        key,
        addr,
        alias=None,
        last=-1,
        size=-1,
        name="",
        typ: typing.Type = float,
    ):

        self.typ = typ
        self.key = key
        self.addr = addr
        self.name = name
        self.alias = alias
        self.size = size
        self.prefer_size = True

        # some ranges are prefered as a size and others
        # using their end addresses.  remember here and
        # calc the other accordingly.
        if last > 0:
            self.prefer_size = False
            self.size = last - addr + 1

    @property
    def naxis_sized(self):

        return self.size == NAXES()

    @property
    def last(self):
        return self.addr + self.size - 1

    @property
    def isrange(self):
        return self.size > 1

    @property
    def range_as_text(self):
        suffix = f" … #{self.last}" if self.isrange else ""
        return f"#{self.addr}{suffix}"

    @property
    def range_as_html(self):
        return self.range_as_text.replace("…", "&#8230;")

    def htmliter(self):
        yield self.name.rjust(NAME_WIDTH)
        yield str(self.size).rjust(SIZE_WIDTH)
        yield self.range_as_html.center(RANGE_WIDTH)

    def for_regen(self):
        funcname = self.__class__.__qualname__

        if self.prefer_size:
            arg = f"last={self.last}"
        else:
            arg = f"size={self.size}"

        restxt = f"{self.addr},{arg}"
        return f'"{self.name}" : {funcname}({restxt}),'

    # for the .txt output
    def for_txt(self):
        sizetxt = "naxes" if self.size == NAXES() else str(self.size)
        return (
            self.range_as_text,
            sizetxt,
            self.key,
            self.typ.__name__,
            self.name,
        )

    def for_org(self):
        return org_line(
            "|",
            name=self.name,
            size=self.size,
            wrap_code=True,
            arange=self.range_as_text,
        )

    # don't put gaps into python output
    def for_py_out(self):
        # return f"# {self.addr} .. {self.last_as_text} {self.name} .."
        return ""

    def __lt__(self, other):
        return self.addr < other.addr


class Gen(MacroVar):
    def __init__(
        self,
        *,
        idc,
        addr=0,
        last=-1,
        size=-1,
        typ=float,
    ):

        super().__init__(
            key=idc,
            addr=addr,
            size=size,
            last=last,
            typ=typ,
        )

    def for_py_out(self):

        if self.naxis_sized:
            sstr = "[NAXES]"
        else:
            sstr = f"[{self.size:5}]"
        return f"{def_prefix(self.name):25} = {MAKE_PFX}Fixed{sstr}(addr={self.addr:4})"


def one(addr, typ=float):
    return Gen(
        idc="v" + str(typ)[0],
        addr=addr,
        size=1,
        typ=typ,
    )


def ione(addr):
    return one(addr, typ=int)


class Alias(MacroVar):
    def __init__(self, src):
        super().__init__(key="A", addr=src.addr, size=src.size, alias=src)

    def for_regen(self):
        assert self.alias is not None

        return f'"{self.name}" : alias("{self.alias.name}"),'

    def for_py_out(self):
        assert self.alias is not None
        return f"{def_prefix(self.name)} = {def_prefix(self.alias.name)}"

    def for_txt(self):

        return (
            self.range_as_text,
            str(self.size),
            self.key,
            self.typ.__name__,
            " also " + self.name,
        )


def fixed(addr, size=-1, last=-1, typ=float):
    return Gen(
        idc="V",
        addr=addr,
        last=last,
        size=size,
        typ=typ,
    )


class Gap(MacroVar):
    C = 0

    def __init__(self, addr: int, size: int = -1, last: int = -1, name="gap"):
        super().__init__(key="_", addr=addr, size=size, last=last)
        self.name = name

    def for_regen(self):
        self.name = f"gap{Gap.C:02}"
        Gap.C += 1
        return super().for_regen()


def cwcpos(addr):
    return Gen(idc="m", addr=addr, size=NAXES())


def machinepos(addr):
    return Gen(idc="m", addr=addr, size=NAXES())


def tooltable(addr, size, typ=float):
    return Gen(
        idc="T",
        addr=addr,
        size=size,
        typ=typ,
    )


def small_tooltable(addr, typ=float):
    return tooltable(addr, size=100, typ=typ)


def large_tooltable(addr, typ=float):
    return tooltable(addr, size=200, typ=typ)


class GPalletTable(MacroVar):
    def __init__(self, addr):
        super().__init__(key="L", addr=addr, size=100, typ=PalletTable)


def GWorkOffsetTable(addr):
    return Gen(idc="m", addr=addr, size=NAXES())


class Names:
    interesting: list[MacroVar]
    do_store: bool

    def __init__(self):
        self.do_store = False
        self.interesting = []

    def py_write_to(self, out):
        for v in self.interesting:
            _ = self.do_store
            line = v.for_py_out()
            if line:
                out.write(INDENT + line + "\n")

    def __setattr__(self, key, value):

        if key == "start_names":
            self.do_store = True
        elif key == "end_names":
            self.do_store = False

        object.__setattr__(self, key, value)
        if self.do_store:
            if key[0].isupper():
                value.name = key
                self.interesting.append(value)


# pylint: disable=too-few-public-methods
class HaasNames(Names):
    title = "HAAS"

    def __init__(self):
        super().__init__()
        self.start_names = 0
        self.NULL = one(0)
        self.MACRO_ARGUMENTS = fixed(1, last=33)
        self.GP_SAVED1 = fixed(100, last=149)
        self.PROBE_VALUES = fixed(150, last=199)
        self.GAP02 = Gap(200, size=300)
        self.GP_SAVED2 = fixed(500, size=50)

        self.PROBE_CALIB1 = fixed(550, size=6)
        self.PROBE_R = fixed(556, size=3)
        self.PROBE_CALIB2 = fixed(559, size=22)

        self.GP_SAVED3 = fixed(581, size=119)
        self.GAP03 = Gap(700, size=100)
        self.GP_SAVED4 = fixed(800, size=200)
        self.INPUTS = fixed(1000, size=64)
        self.MAX_LOADS_XYZAB = fixed(1064, size=5)
        self.GAP04 = Gap(1069, size=11)
        self.RAW_ANALOG = fixed(1080, size=10)
        self.FILTERED_ANALOG = fixed(1090, size=8)
        self.SPINDLE_LOAD = one(1098)
        self.GAP05 = Gap(1099, size=165)
        self.MAX_LOADS_CTUVW = fixed(1264, size=5)
        self.GAP06 = Gap(1269, size=332)
        self.TOOL_TBL_FLUTES = large_tooltable(1601, typ=int)
        self.TOOL_TBL_VIBRATION = large_tooltable(1801)
        self.TOOL_TBL_OFFSETS = large_tooltable(2001)
        self.TOOL_TBL_WEAR = large_tooltable(2201)
        self.TOOL_TBL_DROFFSET = large_tooltable(2401)
        self.TOOL_TBL_DRWEAR = large_tooltable(2601)
        self.GAP07 = Gap(2801, size=199)
        self.ALARM = one(3000, typ=int)
        self.T_MS = one(3001, typ=Time)
        self.T_HR = one(3002, typ=Time)
        self.SINGLE_BLOCK_OFF = ione(3003)
        self.FEED_HOLD_OFF = ione(3004)
        self.GAP08 = Gap(3005, size=1)
        self.MESSAGE = ione(3006)
        self.GAP09 = Gap(3007, size=4)
        self.YEAR_MONTH_DAY = one(3011, typ=Time)
        self.HOUR_MINUTE_SECOND = one(3012, typ=Time)
        self.GAP10 = Gap(3013, size=7)
        self.POWER_ON_TIME = one(3020, typ=Time)
        self.CYCLE_START_TIME = one(3021, typ=Time)
        self.FEED_TIMER = one(3022, typ=Time)
        self.CUR_PART_TIMER = one(3023, typ=Time)
        self.LAST_COMPLETE_PART_TIMER = one(3024, typ=Time)
        self.LAST_PART_TIMER = one(3025, typ=Time)
        self.TOOL_IN_SPIDLE = ione(3026)
        self.SPINDLE_RPM = ione(3027)
        self.PALLET_LOADED = ione(3028)
        self.GAP11 = Gap(3029, size=1)
        self.SINGLE_BLOCK = ione(3030)
        self.AGAP = one(3031)
        self.BLOCK_DELETE = ione(3032)
        self.OPT_STOP = ione(3033)
        self.GAP12 = Gap(3034, size=162)
        self.TIMER_CELL_SAFE = one(3196, typ=Time)
        self.GAP13 = Gap(3197, size=4)
        self.TOOL_TBL_DIAMETER = large_tooltable(3201)
        self.TOOL_TBL_COOLANT_POSITION = large_tooltable(3401)
        self.GAP14 = Gap(3601, size=300)
        self.M30_COUNT1 = ione(3901)
        self.M30_COUNT2 = ione(3902)
        self.GAP15 = Gap(3903, size=98)
        self.PREV_BLOCK = fixed(4001, size=13)
        self.PREV_WCS = fixed(4014, size=1)
        self.PREV_BLOCK_B = Gap(4015, last=4021)
        self.GAP122 = Gap(4022, last=4100)
        self.PREV_BLOCK_ADDRESS = fixed(4101, last=4126)
        self.LAST_TARGET_POS = cwcpos(5001)
        self.MACHINE_POS = machinepos(5021)
        self.WORK_POS = cwcpos(5041)
        self.SKIP_POS = cwcpos(5061)
        self.TOOL_OFFSET = fixed(5081, size=20)
        self.GAP18 = Gap(5101, size=100)
        self.G52 = GWorkOffsetTable(5201)
        self.G54 = GWorkOffsetTable(5221)
        self.G55 = GWorkOffsetTable(5241)
        self.G56 = GWorkOffsetTable(5261)
        self.G57 = GWorkOffsetTable(5281)
        self.G58 = GWorkOffsetTable(5301)
        self.G59 = GWorkOffsetTable(5321)
        self.GAP19 = Gap(5341, size=60)
        self.TOOL_TBL_FEED_TIMERS = small_tooltable(5401, typ=Secs)
        self.TOOL_TBL_TOTAL_TIMERS = small_tooltable(5501, typ=Secs)
        self.TOOL_TBL_LIFE_LIMITS = small_tooltable(5601, typ=int)
        self.TOOL_TBL_LIFE_COUNTERS = small_tooltable(5701, typ=int)
        self.TOOL_TBL_LIFE_MAX_LOADS = small_tooltable(5801)
        self.TOOL_TBL_LIFE_LOAD_LIMITS = small_tooltable(5901)
        self.GAP20 = Gap(6001, size=197)
        self.NGC_CF = ione(6198)
        self.GAP21 = Gap(6199, size=802)
        self.G154_P1 = GWorkOffsetTable(7001)
        self.G154_P2 = GWorkOffsetTable(7021)
        self.G154_P3 = GWorkOffsetTable(7041)
        self.G154_P4 = GWorkOffsetTable(7061)
        self.G154_P5 = GWorkOffsetTable(7081)
        self.G154_P6 = GWorkOffsetTable(7101)
        self.G154_P7 = GWorkOffsetTable(7121)
        self.G154_P8 = GWorkOffsetTable(7141)
        self.G154_P9 = GWorkOffsetTable(7161)
        self.G154_P10 = GWorkOffsetTable(7181)
        self.G154_P11 = GWorkOffsetTable(7201)
        self.G154_P12 = GWorkOffsetTable(7221)
        self.G154_P13 = GWorkOffsetTable(7241)
        self.G154_P14 = GWorkOffsetTable(7261)
        self.G154_P15 = GWorkOffsetTable(7281)
        self.G154_P16 = GWorkOffsetTable(7301)
        self.G154_P17 = GWorkOffsetTable(7321)
        self.G154_P18 = GWorkOffsetTable(7341)
        self.G154_P19 = GWorkOffsetTable(7361)
        self.G154_P20 = GWorkOffsetTable(7381)
        self.GAP22 = Gap(7401, size=100)
        self.PALLET_PRIORITY = GPalletTable(7501)
        self.PALLET_STATUS = GPalletTable(7601)
        self.PALLET_PROGRAM = GPalletTable(7701)
        self.PALLET_USAGE = GPalletTable(7801)
        self.GAP23 = Gap(7901, size=599)
        self.ATM_ID = ione(8500)
        self.ATM_PERCENT = one(8501, typ=Percent)
        self.ATM_TOTAL_AVL_USAGE = ione(8502)
        self.ATM_TOTAL_AVL_HOLE_COUNT = ione(8503)
        self.ATM_TOTAL_AVL_FEED_TIME = one(8504, typ=Secs)
        self.ATM_TOTAL_AVL_TOTAL_TIME = one(8505, typ=Secs)
        self.GAP24 = Gap(8506, size=4)
        self.ATM_NEXT_TOOL_NUMBER = ione(8510)
        self.ATM_NEXT_TOOL_LIFE = one(8511, typ=Percent)
        self.ATM_NEXT_TOOL_AVL_USAGE = ione(8512)
        self.ATM_NEXT_TOOL_HOLE_COUNT = ione(8513)
        self.ATM_NEXT_TOOL_FEED_TIME = one(8514, typ=Secs)
        self.ATM_NEXT_TOOL_TOTAL_TIME = one(8515, typ=Secs)
        self.GAP25 = Gap(8516, size=34)
        self.TOOL_ID = ione(8550)
        self.TOOL_FLUTES = ione(8551)
        self.TOOL_MAX_VIBRATION = one(8552)
        self.TOOL_LENGTH_OFFSETS = one(8553)
        self.TOOL_LENGTH_WEAR = one(8554)
        self.TOOL_DIAMETER_OFFSETS = one(8555)
        self.TOOL_DIAMETER_WEAR = one(8556)
        self.TOOL_ACTUAL_DIAMETER = one(8557)
        self.TOOL_COOLANT_POSITION = ione(8558)
        self.TOOL_FEED_TIMER = one(8559, typ=Secs)
        self.TOOL_TOTAL_TIMER = one(8560, typ=Secs)
        self.TOOL_LIFE_LIMIT = one(8561)
        self.TOOL_LIFE_COUNTER = one(8562)
        self.TOOL_LIFE_MAX_LOAD = one(8563)
        self.TOOL_LIFE_LOAD_LIMIT = one(8564)
        self.GAP26 = Gap(8565, size=435)
        self.THERMAL_COMP_ACC = one(9000)
        self.GAP27 = Gap(9001, size=15)
        self.THERMAL_SPINDLE_COMP_ACC = one(9016)
        self.GVARIABLES3 = fixed(10000, last=10999)
        self.PROBE_VALUES_ = fixed(10150, last=10199)
        self.GPS1 = fixed(10200, last=10399)
        self.GPNS1 = fixed(10400, last=10499)
        self.GPS2 = fixed(10500, last=10549)
        self.PROBE_CALIB_ = fixed(10550, last=10599)
        self.GPS3 = fixed(10600, last=10699)
        self.GPNS3 = fixed(10700, last=10799)
        self.GPS4 = fixed(10800, last=10999)
        self.INPUTS1 = fixed(11000, size=256)
        self.GAP29 = Gap(11256, size=744)
        self.OUTPUT1 = fixed(12000, size=256)
        self.GAP30 = Gap(12256, size=744)
        self.FILTERED_ANALOG1 = fixed(13000, size=13)
        self.COOLANT_LEVEL = one(13013)
        self.FILTERED_ANALOG2 = fixed(13014, size=50)
        self.GAP31 = Gap(13064, size=936)
        self.SETTING = fixed(20000, size=10000)
        self.PARAMETER = fixed(30000, size=10000)

        self.TOOL_TYP = fixed(50001, size=200)
        self.TOOL_MATERIAL = fixed(50201, size=200)
        self.GAP32 = Gap(50401, last=50600)
        self.CURRENT_OFFSET = fixed(50601, size=200)
        self.GAP33 = Gap(51001, last=51300)

        self.CURRENT_OFFSET2 = fixed(50801, size=200)
        self.VPS_TEMPLATE_OFFSET = fixed(51301, size=100)
        self.WORK_MATERIAL = fixed(51401, size=200)
        self.VPS_FEEDRATE = fixed(51601, size=200)

        self.APPROX_LENGTH = fixed(51801, size=200)
        self.APPROX_DIAMETER = fixed(52001, size=200)
        self.EDGE_MEASURE_HEIGHT = fixed(52201, size=200)
        self.TOOL_TOLERANCE = fixed(52401, size=200)
        self.PROBE_TYPE = fixed(52601, size=200)

        self.PROBE = Alias(self.SKIP_POS)
        self.WORK = Alias(self.WORK_POS)

        self.MACHINE = Alias(self.MACHINE_POS)
        self.G53 = Alias(self.MACHINE_POS)
        self.end_names = 0


# def openw(outname):
#    yield sys.stdout if outname == "-" else open(outname, "w", encoding="utf-8")


@contextlib.contextmanager
def openw(outname):
    if outname == "-":
        yield sys.stdout

    else:
        yield open(outname, "w", encoding="utf-8")


def txt_out(outname, names):
    guts = Table(
        title=f"{names.title} Macro Variables",
        caption=f"Generated by {__file__}",
    )

    guts.add_column("Range", justify="center")
    guts.add_column("N", justify="right")
    guts.add_column("K", justify="right")
    guts.add_column("Type", justify="center")
    guts.add_column("Name", justify="left")

    snames = sorted(names.interesting)
    for el in snames:
        guts.add_row(*el.for_txt())

        if el.alias:
            el = el.alias

    with openw(outname) as out:

        console = rich.console.Console(file=out)
        console.width = 2000
        console.print(guts, style=None)
        print("Generated ", outname)


def regen_out(outname, defs):
    with openw(outname) as out:
        for el in sorted(defs.interesting):
            out.write("        " + el.for_regen() + "\n")


col_titles = ["Name", "Size", "Address"]


def unwind(lst):
    if isinstance(lst, str):
        return lst

    res = ""
    for x in lst:
        res += unwind(x)
    return res


def bracket(bname, text, nl=False):

    text = unwind(text)
    if nl:
        suffix = "\n"
    else:
        suffix = ""
    return bname + text + bname[0] + "/" + bname[1:] + suffix


def bnl(bname, text, nl=True):
    return bracket(bname, text, nl)


def html_out(ofile, defs):
    ofile.write(
        bracket(
            "<body>",
            [
                bnl(
                    "<style>",
                    (
                        "table,td {border-collapse:collapse; border:1px solid black;}\n"
                        "th {border:3px solid black;}\n"
                        "th {padding:0.1em 0.5em;font-size: 150%}\n"
                        "td {padding:0.1em 1em;}\n"
                        "tr,td:nth-child(1) {text-align:right;}\n"
                        "tr,td:nth-child(2) {text-align:right;font-family:monospace;}\n"
                        "tr,td:nth-child(3) {text-align:center;font-family:monospace;}\n"
                    ),
                ),
                bracket(
                    "<table>",
                    [
                        bnl(
                            '<tr border="1">',
                            (bracket("<th>", title) for title in col_titles),
                        ),
                        "\n",
                        [
                            bnl(
                                "<tr>",
                                (bracket("<td>", chunk) for chunk in row.htmliter()),
                            )
                            for row in sorted(defs.interesting)
                        ],
                    ],
                ),
            ],
        )
    )


#   for el in sorted(defs.interesting):
W1 = 30
W2 = 5
W3 = 10


def org_out(outname, defs):

    with openw(outname) as out:

        out.write(
            org_line("|", wrap_code=True, name="Name", size="Size", arange="Address")
        )
        out.write(
            org_line(
                "+",
                wrap_code=False,
                name="-" * NAME_WIDTH,
                size="-" * SIZE_WIDTH,
                arange="-" * RANGE_WIDTH,
            )
        )

        for el in sorted(defs.interesting):
            if el.name != "-":
                out.write(el.for_org())


def dpy_out(out, defs):
    defs.py_write_to(out)


def py_out(target_filename, defs):
    tmp_filepath = pathlib.Path(target_filename).with_suffix(".tmp")

    with open(target_filename, encoding="utf-8") as inf:
        repl = re.match(
            "(.*?# MACHINE GEN BELOW.*?).*(.*?# MACHINE.*)",
            inf.read(),
            flags=re.DOTALL,
        )
    if repl is not None:
        with open(tmp_filepath, "w", encoding="utf-8") as out:
            out.write(repl.group(1) + "\n")
            defs.py_write_to(out)
            out.write(INDENT + repl.group(2))
        tmp_filepath.rename(target_filename)


# run through attributes and make sure
# there's nothing that stupid around and
# turn attributes into vector.


def insert_gaps(interesting):
    prev = None

    for now in interesting:
        yield now
        if prev:
            if now.addr != prev.last + 1:
                # something has bad math.
                yield Gap(
                    addr=prev.last + 1,
                    last=now.addr - 1,
                    name="an error",
                )
        prev = now


def main(argv=None):
    opts = docopt.docopt(argv=argv, doc=DOC)

    try:
        machine = HaasNames()

        machine.interesting = list(insert_gaps(machine.interesting))

        for names in [machine]:
            if out := opts["--txt"]:
                txt_out(out, names)
            if out := opts["--dev"]:
                regen_out(out, names)
            if out := opts["--org"]:
                org_out(out, names)
            if out := opts["--py"]:
                py_out(out, names)
            if out := opts["--dpy"]:
                with openw(out) as ofile:
                    dpy_out(ofile, names)
            if out := opts["--html"]:
                with openw(out) as ofile:
                    html_out(ofile, names)

    except FileNotFoundError as exc:  # no cover
        print(f"FAIL {exc.args[1]} '{exc.filename}'")
        return 1
    return 0


if __name__ == "__main__":
    main()  # no cover
