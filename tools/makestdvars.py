#! /usr/bin/env python
import pathlib
import re
import sys

import docopt
import rich.console

from rich.table import Table


DOC = """

Creates machine specific definitions and doc.

Usage:
   makestdvars  [--txt=<txt>] [--dev=<dev>] [--py=<py>] [--org=<org>]
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


MAKE_PFX = "coords."

# pylint: disable=invalid-name
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-statements


def NAXES():
    return "NAXES"


class MacroVar:
    def __init__(self, *, key, addr, alias=None, size=None, name="", typ=""):
        self.typ = typ
        self.key = key
        self.addr = addr

        self.name = name
        self.alias = alias
        self.size = size
        suffix = ""
        self.last = None
        if isinstance(self.size, str):
            self.size_as_text = "naxes"
            self.last = NAXES
            suffix = "…"
        else:
            self.last = self.addr + self.size - 1
            # that's a non breaking space
            self.size_as_text = f"{self.size:5}"

            if self.last != self.addr:
                suffix = f" … #{self.last:5}"
        self.range_as_text = f"#{self.addr:5}{suffix}".center(15)

    def for_regen(self):
        funcname = self.__class__.__qualname__
        res = [str(self.addr)]
        if self.size is not None:
            res.append(f"size={self.size}")
        restxt = ", ".join(res)
        return f"{def_prefix(self.name)} = {funcname}({restxt})"

    # for the .txt output
    def for_txt(self):
        return (
            self.range_as_text,
            str(self.size),
            self.key,
            self.typ,
            self.name,
        )

    def for_org(self):
        return (
            f"| <code>{self.name}</code> "
            f"| <code>{self.size_as_text}</code>"
            f"| <code>{self.range_as_text}</code> |\n"
        )

    def for_py_out(self):
        return f"# {self.addr} .. {self.last} {self.name} .."

    def __lt__(self, other):
        return self.addr < other.addr


class Gen(MacroVar):
    def __init__(
        self,
        *,
        exp_name,
        idc,
        addr,
        size=None,
        typ,
    ):
        self.exp_name = exp_name

        super().__init__(
            key=idc,
            addr=addr,
            size=size,
            typ=typ,
        )

    def for_py_out(self):
        rs = ""

        sstr = ""
        if self.size is not None and self.size != 1:
            sstr = f"[{self.size}]"
        return f"{def_prefix(self.name)} = {MAKE_PFX}Fixed{sstr}({rs}addr={self.addr})"


def one(addr, typ="Float"):
    return Gen(
        exp_name="Fixed",
        idc="v" + typ[0],
        addr=addr,
        size=1,
        typ=typ,
    )


def ione(addr):
    return one(addr, typ="Int")


class Alias(MacroVar):
    def __init__(self, src):
        super().__init__(key="A", addr=src.addr, size=src.size, alias=src)

    def for_regen(self):
        assert self.alias is not None
        return f"{def_prefix(self.name.ljust(20))} = alias({def_prefix}{self.alias.name})"

    def for_py_out(self):
        assert self.alias is not None
        return f"{def_prefix(self.name)} = {def_prefix(self.alias.name)}"

    def for_txt(self):
        return (
            self.range_as_text,
            str(self.size),
            self.key,
            self.typ,
            " also " + self.name,
        )


def fixed(addr, size, typ="Float"):
    return Gen(
        exp_name="Fixed",
        idc="V",
        addr=addr,
        size=size,
        typ=typ,
    )


class Gap(MacroVar):
    C = 0

    def __init__(self, addr, size=None):
        super().__init__(key="_", addr=addr, size=size)
        self.name = "-"

    def for_regen(self):
        self.name = f"gap{Gap.C:02}"
        Gap.C += 1
        return super().for_regen()


def cwcpos(addr):
    return Gen(exp_name="CWCPos", idc="m", addr=addr, size=NAXES(), typ="Float")


def machinepos(addr):
    return Gen(exp_name="MachinePos", idc="m", addr=addr, size=NAXES(), typ="Float")


def workoffsettable(addr):
    return Gen(exp_name="WorkOffsetTable", idc="W", addr=addr, typ="Float", size=NAXES())


def tooltable(addr, size, typ="Float"):
    return Gen(exp_name="ToolTable", idc="T", addr=addr, size=size, typ=typ)


class PalletTable(MacroVar):
    def __init__(self, addr, size):
        super().__init__(key="L", addr=addr, size=size, typ="Int")


class Names:
    interesting: list[MacroVar]

    def __init__(self):
        object.__setattr__(self, "interesting", [])

    def py_write_to(self, out):
        for v in self.interesting:
            out.write(INDENT + v.for_py_out() + "\n")

    def __setattr__(self, key, value):
        if key[0].isupper():
            value.name = key
            object.__setattr__(self, key, value)

        self.interesting.append(value)


# pylint: disable=too-few-public-methods
class HaasNames(Names):
    title = "HAAS"

    def __init__(self):
        super().__init__()

        self.NULL = one(0)
        self.MACRO_ARGUMENTS = fixed(1, size=33)
        self.GAP01 = Gap(34, size=66)
        self.GP_SAVED1 = fixed(100, size=100)
        self.GAP02 = Gap(200, size=300)
        self.GP_SAVED2 = fixed(500, size=50)

        self.PROBE_CALIBRATION1 = fixed(550, size=6)
        self.PROBE_R = fixed(556, size=3)
        self.PROBE_CALIBRATION2 = fixed(559, size=22)

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
        self.TOOL_TBL_FLUTES = tooltable(1601, size=200, typ="Int")
        self.TOOL_TBL_VIBRATION = tooltable(1801, size=200)
        self.TOOL_TBL_OFFSETS = tooltable(2001, size=200)
        self.TOOL_TBL_WEAR = tooltable(2201, size=200)
        self.TOOL_TBL_DROFFSET = tooltable(2401, size=200)
        self.TOOL_TBL_DRWEAR = tooltable(2601, size=200)
        self.GAP07 = Gap(2801, size=199)
        self.ALARM = one(3000, typ="Int")
        self.T_MS = one(3001, typ="Time")
        self.T_HR = one(3002, typ="Time")
        self.SINGLE_BLOCK_OFF = ione(3003)
        self.FEED_HOLD_OFF = ione(3004)
        self.GAP08 = Gap(3005, size=1)
        self.MESSAGE = ione(3006)
        self.GAP09 = Gap(3007, size=4)
        self.YEAR_MONTH_DAY = one(3011, typ="Time")
        self.HOUR_MINUTE_SECOND = one(3012, typ="Time")
        self.GAP10 = Gap(3013, size=7)
        self.POWER_ON_TIME = one(3020, typ="Time")
        self.CYCLE_START_TIME = one(3021, typ="Time")
        self.FEED_TIMER = one(3022, typ="Time")
        self.CUR_PART_TIMER = one(3023, typ="Time")
        self.LAST_COMPLETE_PART_TIMER = one(3024, typ="Time")
        self.LAST_PART_TIMER = one(3025, typ="Time")
        self.TOOL_IN_SPIDLE = ione(3026)
        self.SPINDLE_RPM = ione(3027)
        self.PALLET_LOADED = ione(3028)
        self.GAP11 = Gap(3029, size=1)
        self.SINGLE_BLOCK = ione(3030)
        self.AGAP = one(3031)
        self.BLOCK_DELETE = ione(3032)
        self.OPT_STOP = ione(3033)
        self.GAP12 = Gap(3034, size=162)
        self.TIMER_CELL_SAFE = one(3196, typ="Time")
        self.GAP13 = Gap(3197, size=4)
        self.TOOL_TBL_DIAMETER = tooltable(3201, size=200)
        self.TOOL_TBL_COOLANT_POSITION = tooltable(3401, size=200)
        self.GAP14 = Gap(3601, size=300)
        self.M30_COUNT1 = ione(3901)
        self.M30_COUNT2 = ione(3902)
        self.GAP15 = Gap(3903, size=98)
        self.LAST_BLOCK_G = fixed(4001, size=13)
        self.LAST_WCS = fixed(4014, size=1)

        self.GAP16 = Gap(4022, size=79)
        self.LAST_BLOCK_ADDRESS = fixed(4101, size=26)
        self.GAP17 = Gap(4127, size=874)
        self.LAST_TARGET_POS = cwcpos(5001)
        self.MACHINE_POS = machinepos(5021)
        self.WORK_POS = cwcpos(5041)
        self.SKIP_POS = cwcpos(5061)
        self.TOOL_OFFSET = fixed(5081, size=20)
        self.GAP18 = Gap(5101, size=100)
        self.G52 = workoffsettable(5201)
        self.G54 = workoffsettable(5221)
        self.G55 = workoffsettable(5241)
        self.G56 = workoffsettable(5261)
        self.G57 = workoffsettable(5281)
        self.G58 = workoffsettable(5301)
        self.G59 = workoffsettable(5321)
        self.GAP19 = Gap(5341, size=60)
        self.TOOL_TBL_FEED_TIMERS = tooltable(5401, size=100, typ="Secs")
        self.TOOL_TBL_TOTAL_TIMERS = tooltable(5501, size=100, typ="Secs")
        self.TOOL_TBL_LIFE_LIMITS = tooltable(5601, size=100, typ="Int")
        self.TOOL_TBL_LIFE_COUNTERS = tooltable(5701, size=100, typ="Int")
        self.TOOL_TBL_LIFE_MAX_LOADS = tooltable(5801, size=100)
        self.TOOL_TBL_LIFE_LOAD_LIMITS = tooltable(5901, size=100)
        self.GAP20 = Gap(6001, size=197)
        self.NGC_CF = ione(6198)
        self.GAP21 = Gap(6199, size=802)
        self.G154_P1 = workoffsettable(7001)
        self.G154_P2 = workoffsettable(7021)
        self.G154_P3 = workoffsettable(7041)
        self.G154_P4 = workoffsettable(7061)
        self.G154_P5 = workoffsettable(7081)
        self.G154_P6 = workoffsettable(7101)
        self.G154_P7 = workoffsettable(7121)
        self.G154_P8 = workoffsettable(7141)
        self.G154_P9 = workoffsettable(7161)
        self.G154_P10 = workoffsettable(7181)
        self.G154_P11 = workoffsettable(7201)
        self.G154_P12 = workoffsettable(7221)
        self.G154_P13 = workoffsettable(7241)
        self.G154_P14 = workoffsettable(7261)
        self.G154_P15 = workoffsettable(7281)
        self.G154_P16 = workoffsettable(7301)
        self.G154_P17 = workoffsettable(7321)
        self.G154_P18 = workoffsettable(7341)
        self.G154_P19 = workoffsettable(7361)
        self.G154_P20 = workoffsettable(7381)
        self.GAP22 = Gap(7401, size=100)
        self.PALLET_PRIORITY = PalletTable(7501, size=100)
        self.PALLET_STATUS = PalletTable(7601, size=100)
        self.PALLET_PROGRAM = PalletTable(7701, size=100)
        self.PALLET_USAGE = PalletTable(7801, size=100)
        self.GAP23 = Gap(7901, size=599)
        self.ATM_ID = ione(8500)
        self.ATM_PERCENT = one(8501, typ="Percent")
        self.ATM_TOTAL_AVL_USAGE = ione(8502)
        self.ATM_TOTAL_AVL_HOLE_COUNT = ione(8503)
        self.ATM_TOTAL_AVL_FEED_TIME = one(8504, typ="Secs")
        self.ATM_TOTAL_AVL_TOTAL_TIME = one(8505, typ="Secs")
        self.GAP24 = Gap(8506, size=4)
        self.ATM_NEXT_TOOL_NUMBER = ione(8510)
        self.ATM_NEXT_TOOL_LIFE = one(8511, typ="Percent")
        self.ATM_NEXT_TOOL_AVL_USAGE = ione(8512)
        self.ATM_NEXT_TOOL_HOLE_COUNT = ione(8513)
        self.ATM_NEXT_TOOL_FEED_TIME = one(8514, typ="Secs")
        self.ATM_NEXT_TOOL_TOTAL_TIME = one(8515, typ="Secs")
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
        self.TOOL_FEED_TIMER = one(8559, typ="Secs")
        self.TOOL_TOTAL_TIMER = one(8560, typ="Secs")
        self.TOOL_LIFE_LIMIT = one(8561)
        self.TOOL_LIFE_COUNTER = one(8562)
        self.TOOL_LIFE_MAX_LOAD = one(8563)
        self.TOOL_LIFE_LOAD_LIMIT = one(8564)
        self.GAP26 = Gap(8565, size=435)
        self.THERMAL_COMP_ACC = one(9000)
        self.GAP27 = Gap(9001, size=15)
        self.THERMAL_SPINDLE_COMP_ACC = one(9016)
        self.GAP28 = Gap(9017, size=983)
        self.GVARIABLES3 = fixed(10000, size=1000)
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
        self.GAP32 = Gap(50401, 50600)
        self.GAP32 = Gap(51001, 51300)
        self.CURRENT_OFFSET = fixed(50601, size=200)
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


def openw(outname):
    return sys.stdout if outname == "-" else open(outname, "w", encoding="utf-8")


def txt_out(outname, names):
    guts = Table(
        title=f"{names.title} Macro Variables",
        caption=f"Generated by {__file__}",
    )

    guts.add_column("Range", justify="right")
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
        console.print(guts, style=None)
        print("Generated ", outname)


def regen_out(outname, defs):
    with openw(outname) as out:
        for el in sorted(defs.interesting):
            out.write("        " + el.for_regen())


def org_out(outname, defs):
    with openw(outname) as out:
        out.write(
            "| <code>Name</code>          "
            "|<code>Size</code>"
            "| <code>Address</code>         |\n"
        )
        out.write("| --- | --- | --- |\n")
        for el in sorted(defs.interesting):
            if el.name != "-":
                out.write(el.for_org())


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


def main(argv=None):
    opts = docopt.docopt(argv=argv, doc=DOC)

    try:
        for names in [HaasNames()]:
            if out := opts["--txt"]:
                txt_out(out, names)
            if out := opts["--dev"]:
                regen_out(out, names)
            if out := opts["--org"]:
                org_out(out, names)
            if out := opts["--py"]:
                py_out(out, names)

    except FileNotFoundError as exc:  # no cover
        print(f"FAIL {exc.args[1]} '{exc.filename}'")
        return 1
    return 0


if __name__ == "__main__":
    main()  # no cover
