from p2g import axis
from p2g import coords

from p2g.coords import Fixed

# j = coords.Fixed[3](addr=2001)
NAME = "HAAS NGC"
ORIGIN = [0, 0, 0]
NAXES = axis.Axes()
NO_SKIP = "M78"
MUST_SKIP = "M79"
FEED_FAST = 650.0
FEED_SLOW = 50.0
PROBE_FAST = 50.0
PROBE_SLOW = 10.0
PROBE_ON = ["G65 P9832"]
PROBE_H = Fixed[3](addr=2001)
OTS_ON = ["M59 P2", "G04 P1.0", "M59 P3"]
OTS_OFF = ["M69 P2", "M68 P3"]
SPINDLE_PROBE_ON = "G65 P9832"
SPINDLE_PROBE_OFF = "G65 P9833"
NO_LOOKAHEAD = ["G103 P1", "G04 P1", "G04 P1", "G04 P1"]
# MACHINE GEN BELOW
NULL = coords.Fixed(addr=0)
MACRO_ARGUMENTS = coords.Fixed[33](addr=1)
# 34 .. 99 GAP01 ..
GP_SAVED1 = coords.Fixed[100](addr=100)
# 200 .. 499 GAP02 ..
GP_SAVED2 = coords.Fixed[50](addr=500)
PROBE_CALIBRATION1 = coords.Fixed[6](addr=550)
PROBE_R = coords.Fixed[3](addr=556)
PROBE_CALIBRATION2 = coords.Fixed[22](addr=559)
GP_SAVED3 = coords.Fixed[119](addr=581)
# 700 .. 799 GAP03 ..
GP_SAVED4 = coords.Fixed[200](addr=800)
INPUTS = coords.Fixed[64](addr=1000)
MAX_LOADS_XYZAB = coords.Fixed[5](addr=1064)
# 1069 .. 1079 GAP04 ..
RAW_ANALOG = coords.Fixed[10](addr=1080)
FILTERED_ANALOG = coords.Fixed[8](addr=1090)
SPINDLE_LOAD = coords.Fixed(addr=1098)
# 1099 .. 1263 GAP05 ..
MAX_LOADS_CTUVW = coords.Fixed[5](addr=1264)
# 1269 .. 1600 GAP06 ..
TOOL_TBL_FLUTES = coords.Fixed[200](addr=1601)
TOOL_TBL_VIBRATION = coords.Fixed[200](addr=1801)
TOOL_TBL_OFFSETS = coords.Fixed[200](addr=2001)
TOOL_TBL_WEAR = coords.Fixed[200](addr=2201)
TOOL_TBL_DROFFSET = coords.Fixed[200](addr=2401)
TOOL_TBL_DRWEAR = coords.Fixed[200](addr=2601)
# 2801 .. 2999 GAP07 ..
ALARM = coords.Fixed(addr=3000)
T_MS = coords.Fixed(addr=3001)
T_HR = coords.Fixed(addr=3002)
SINGLE_BLOCK_OFF = coords.Fixed(addr=3003)
FEED_HOLD_OFF = coords.Fixed(addr=3004)
# 3005 .. 3005 GAP08 ..
MESSAGE = coords.Fixed(addr=3006)
# 3007 .. 3010 GAP09 ..
YEAR_MONTH_DAY = coords.Fixed(addr=3011)
HOUR_MINUTE_SECOND = coords.Fixed(addr=3012)
# 3013 .. 3019 GAP10 ..
POWER_ON_TIME = coords.Fixed(addr=3020)
CYCLE_START_TIME = coords.Fixed(addr=3021)
FEED_TIMER = coords.Fixed(addr=3022)
CUR_PART_TIMER = coords.Fixed(addr=3023)
LAST_COMPLETE_PART_TIMER = coords.Fixed(addr=3024)
LAST_PART_TIMER = coords.Fixed(addr=3025)
TOOL_IN_SPIDLE = coords.Fixed(addr=3026)
SPINDLE_RPM = coords.Fixed(addr=3027)
PALLET_LOADED = coords.Fixed(addr=3028)
# 3029 .. 3029 GAP11 ..
SINGLE_BLOCK = coords.Fixed(addr=3030)
AGAP = coords.Fixed(addr=3031)
BLOCK_DELETE = coords.Fixed(addr=3032)
OPT_STOP = coords.Fixed(addr=3033)
# 3034 .. 3195 GAP12 ..
TIMER_CELL_SAFE = coords.Fixed(addr=3196)
# 3197 .. 3200 GAP13 ..
TOOL_TBL_DIAMETER = coords.Fixed[200](addr=3201)
TOOL_TBL_COOLANT_POSITION = coords.Fixed[200](addr=3401)
# 3601 .. 3900 GAP14 ..
M30_COUNT1 = coords.Fixed(addr=3901)
M30_COUNT2 = coords.Fixed(addr=3902)
# 3903 .. 4000 GAP15 ..
LAST_BLOCK_G = coords.Fixed[13](addr=4001)
LAST_WCS = coords.Fixed(addr=4014)
# 4022 .. 4100 GAP16 ..
LAST_BLOCK_ADDRESS = coords.Fixed[26](addr=4101)
# 4127 .. 5000 GAP17 ..
LAST_TARGET_POS = coords.Fixed[NAXES](addr=5001)
MACHINE_POS = coords.Fixed[NAXES](addr=5021)
WORK_POS = coords.Fixed[NAXES](addr=5041)
SKIP_POS = coords.Fixed[NAXES](addr=5061)
TOOL_OFFSET = coords.Fixed[20](addr=5081)
# 5101 .. 5200 GAP18 ..
G52 = coords.Fixed[NAXES](addr=5201)
G54 = coords.Fixed[NAXES](addr=5221)
G55 = coords.Fixed[NAXES](addr=5241)
G56 = coords.Fixed[NAXES](addr=5261)
G57 = coords.Fixed[NAXES](addr=5281)
G58 = coords.Fixed[NAXES](addr=5301)
G59 = coords.Fixed[NAXES](addr=5321)
# 5341 .. 5400 GAP19 ..
TOOL_TBL_FEED_TIMERS = coords.Fixed[100](addr=5401)
TOOL_TBL_TOTAL_TIMERS = coords.Fixed[100](addr=5501)
TOOL_TBL_LIFE_LIMITS = coords.Fixed[100](addr=5601)
TOOL_TBL_LIFE_COUNTERS = coords.Fixed[100](addr=5701)
TOOL_TBL_LIFE_MAX_LOADS = coords.Fixed[100](addr=5801)
TOOL_TBL_LIFE_LOAD_LIMITS = coords.Fixed[100](addr=5901)
# 6001 .. 6197 GAP20 ..
NGC_CF = coords.Fixed(addr=6198)
# 6199 .. 7000 GAP21 ..
G154_P1 = coords.Fixed[NAXES](addr=7001)
G154_P2 = coords.Fixed[NAXES](addr=7021)
G154_P3 = coords.Fixed[NAXES](addr=7041)
G154_P4 = coords.Fixed[NAXES](addr=7061)
G154_P5 = coords.Fixed[NAXES](addr=7081)
G154_P6 = coords.Fixed[NAXES](addr=7101)
G154_P7 = coords.Fixed[NAXES](addr=7121)
G154_P8 = coords.Fixed[NAXES](addr=7141)
G154_P9 = coords.Fixed[NAXES](addr=7161)
G154_P10 = coords.Fixed[NAXES](addr=7181)
G154_P11 = coords.Fixed[NAXES](addr=7201)
G154_P12 = coords.Fixed[NAXES](addr=7221)
G154_P13 = coords.Fixed[NAXES](addr=7241)
G154_P14 = coords.Fixed[NAXES](addr=7261)
G154_P15 = coords.Fixed[NAXES](addr=7281)
G154_P16 = coords.Fixed[NAXES](addr=7301)
G154_P17 = coords.Fixed[NAXES](addr=7321)
G154_P18 = coords.Fixed[NAXES](addr=7341)
G154_P19 = coords.Fixed[NAXES](addr=7361)
G154_P20 = coords.Fixed[NAXES](addr=7381)
# 7401 .. 7500 GAP22 ..
# 7501 .. 7600 PALLET_PRIORITY ..
# 7601 .. 7700 PALLET_STATUS ..
# 7701 .. 7800 PALLET_PROGRAM ..
# 7801 .. 7900 PALLET_USAGE ..
# 7901 .. 8499 GAP23 ..
ATM_ID = coords.Fixed(addr=8500)
ATM_PERCENT = coords.Fixed(addr=8501)
ATM_TOTAL_AVL_USAGE = coords.Fixed(addr=8502)
ATM_TOTAL_AVL_HOLE_COUNT = coords.Fixed(addr=8503)
ATM_TOTAL_AVL_FEED_TIME = coords.Fixed(addr=8504)
ATM_TOTAL_AVL_TOTAL_TIME = coords.Fixed(addr=8505)
# 8506 .. 8509 GAP24 ..
ATM_NEXT_TOOL_NUMBER = coords.Fixed(addr=8510)
ATM_NEXT_TOOL_LIFE = coords.Fixed(addr=8511)
ATM_NEXT_TOOL_AVL_USAGE = coords.Fixed(addr=8512)
ATM_NEXT_TOOL_HOLE_COUNT = coords.Fixed(addr=8513)
ATM_NEXT_TOOL_FEED_TIME = coords.Fixed(addr=8514)
ATM_NEXT_TOOL_TOTAL_TIME = coords.Fixed(addr=8515)
# 8516 .. 8549 GAP25 ..
TOOL_ID = coords.Fixed(addr=8550)
TOOL_FLUTES = coords.Fixed(addr=8551)
TOOL_MAX_VIBRATION = coords.Fixed(addr=8552)
TOOL_LENGTH_OFFSETS = coords.Fixed(addr=8553)
TOOL_LENGTH_WEAR = coords.Fixed(addr=8554)
TOOL_DIAMETER_OFFSETS = coords.Fixed(addr=8555)
TOOL_DIAMETER_WEAR = coords.Fixed(addr=8556)
TOOL_ACTUAL_DIAMETER = coords.Fixed(addr=8557)
TOOL_COOLANT_POSITION = coords.Fixed(addr=8558)
TOOL_FEED_TIMER = coords.Fixed(addr=8559)
TOOL_TOTAL_TIMER = coords.Fixed(addr=8560)
TOOL_LIFE_LIMIT = coords.Fixed(addr=8561)
TOOL_LIFE_COUNTER = coords.Fixed(addr=8562)
TOOL_LIFE_MAX_LOAD = coords.Fixed(addr=8563)
TOOL_LIFE_LOAD_LIMIT = coords.Fixed(addr=8564)
# 8565 .. 8999 GAP26 ..
THERMAL_COMP_ACC = coords.Fixed(addr=9000)
# 9001 .. 9015 GAP27 ..
THERMAL_SPINDLE_COMP_ACC = coords.Fixed(addr=9016)
# 9017 .. 9999 GAP28 ..
GVARIABLES3 = coords.Fixed[1000](addr=10000)
INPUTS1 = coords.Fixed[256](addr=11000)
# 11256 .. 11999 GAP29 ..
OUTPUT1 = coords.Fixed[256](addr=12000)
# 12256 .. 12999 GAP30 ..
FILTERED_ANALOG1 = coords.Fixed[13](addr=13000)
COOLANT_LEVEL = coords.Fixed(addr=13013)
FILTERED_ANALOG2 = coords.Fixed[50](addr=13014)
# 13064 .. 13999 GAP31 ..
SETTING = coords.Fixed[10000](addr=20000)
PARAMETER = coords.Fixed[10000](addr=30000)
TOOL_TYP = coords.Fixed[200](addr=50001)
TOOL_MATERIAL = coords.Fixed[200](addr=50201)
# 50401 .. 101000 GAP32 ..
# 51001 .. 102300 GAP32 ..
CURRENT_OFFSET = coords.Fixed[200](addr=50601)
CURRENT_OFFSET2 = coords.Fixed[200](addr=50801)
VPS_TEMPLATE_OFFSET = coords.Fixed[100](addr=51301)
WORK_MATERIAL = coords.Fixed[200](addr=51401)
VPS_FEEDRATE = coords.Fixed[200](addr=51601)
APPROX_LENGTH = coords.Fixed[200](addr=51801)
APPROX_DIAMETER = coords.Fixed[200](addr=52001)
EDGE_MEASURE_HEIGHT = coords.Fixed[200](addr=52201)
TOOL_TOLERANCE = coords.Fixed[200](addr=52401)
PROBE_TYPE = coords.Fixed[200](addr=52601)
PROBE = SKIP_POS
WORK = WORK_POS
MACHINE = MACHINE_POS
G53 = MACHINE_POS
# MACHINE GEN ABOVE
