import p2g
from p2g import axis

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
PROBE_H = p2g.Fixed[3](addr=2001)
OTS_ON = ["M59 P2", "G04 P1.0", "M59 P3"]
OTS_OFF = ["M69 P2", "M68 P3"]
SPINDLE_PROBE_ON = "P9832"
SPINDLE_PROBE_OFF = "P9833"
NO_LOOKAHEAD = ["G103 P1", "G04 P1", "G04 P1", "G04 P1"]

# MACHINE GEN BELOW
NULL = p2g.Fixed(addr=0)
MACRO_ARGUMENTS = p2g.Fixed[33](addr=1)
# 34 .. 99 - ..
GP_SAVED1 = p2g.Fixed[100](addr=100)
# 200 .. 499 - ..
GP_SAVED2 = p2g.Fixed[50](addr=500)
PROBE_CALIBRATION1 = p2g.Fixed[6](addr=550)
PROBE_R = p2g.Fixed[3](addr=556)
PROBE_CALIBRATION2 = p2g.Fixed[22](addr=559)
GP_SAVED3 = p2g.Fixed[119](addr=581)
# 700 .. 799 - ..
GP_SAVED4 = p2g.Fixed[200](addr=800)
INPUTS = p2g.Fixed[64](addr=1000)
MAX_LOADS_XYZAB = p2g.Fixed[5](addr=1064)
# 1069 .. 1079 - ..
RAW_ANALOG = p2g.Fixed[10](addr=1080)
FILTERED_ANALOG = p2g.Fixed[8](addr=1090)
SPINDLE_LOAD = p2g.Fixed(addr=1098)
# 1099 .. 1263 - ..
MAX_LOADS_CTUVW = p2g.Fixed[5](addr=1264)
# 1269 .. 1600 - ..
TOOL_TBL_FLUTES = p2g.Fixed[200](addr=1601)
TOOL_TBL_VIBRATION = p2g.Fixed[200](addr=1801)
TOOL_TBL_OFFSETS = p2g.Fixed[200](addr=2001)
TOOL_TBL_WEAR = p2g.Fixed[200](addr=2201)
TOOL_TBL_DROFFSET = p2g.Fixed[200](addr=2401)
TOOL_TBL_DRWEAR = p2g.Fixed[200](addr=2601)
# 2801 .. 2999 - ..
ALARM = p2g.Fixed(addr=3000)
T_MS = p2g.Fixed(addr=3001)
T_HR = p2g.Fixed(addr=3002)
SINGLE_BLOCK_OFF = p2g.Fixed(addr=3003)
FEED_HOLD_OFF = p2g.Fixed(addr=3004)
# 3005 .. 3005 - ..
MESSAGE = p2g.Fixed(addr=3006)
# 3007 .. 3010 - ..
YEAR_MONTH_DAY = p2g.Fixed(addr=3011)
HOUR_MINUTE_SECOND = p2g.Fixed(addr=3012)
# 3013 .. 3019 - ..
POWER_ON_TIME = p2g.Fixed(addr=3020)
CYCLE_START_TIME = p2g.Fixed(addr=3021)
FEED_TIMER = p2g.Fixed(addr=3022)
CUR_PART_TIMER = p2g.Fixed(addr=3023)
LAST_COMPLETE_PART_TIMER = p2g.Fixed(addr=3024)
LAST_PART_TIMER = p2g.Fixed(addr=3025)
TOOL_IN_SPIDLE = p2g.Fixed(addr=3026)
SPINDLE_RPM = p2g.Fixed(addr=3027)
PALLET_LOADED = p2g.Fixed(addr=3028)
# 3029 .. 3029 - ..
SINGLE_BLOCK = p2g.Fixed(addr=3030)
AGAP = p2g.Fixed(addr=3031)
BLOCK_DELETE = p2g.Fixed(addr=3032)
OPT_STOP = p2g.Fixed(addr=3033)
# 3034 .. 3195 - ..
TIMER_CELL_SAFE = p2g.Fixed(addr=3196)
# 3197 .. 3200 - ..
TOOL_TBL_DIAMETER = p2g.Fixed[200](addr=3201)
TOOL_TBL_COOLANT_POSITION = p2g.Fixed[200](addr=3401)
# 3601 .. 3900 - ..
M30_COUNT1 = p2g.Fixed(addr=3901)
M30_COUNT2 = p2g.Fixed(addr=3902)
# 3903 .. 4000 - ..
LAST_BLOCK_G = p2g.Fixed[21](addr=4001)
# 4022 .. 4100 - ..
LAST_BLOCK_ADDRESS = p2g.Fixed[26](addr=4101)
# 4127 .. 5000 - ..
LAST_TARGET_POS = p2g.Fixed[NAXES](addr=5001)
MACHINE_POS = p2g.Fixed[NAXES](addr=5021)
WORK_POS = p2g.Fixed[NAXES](addr=5041)
SKIP_POS = p2g.Fixed[NAXES](addr=5061)
TOOL_OFFSET = p2g.Fixed[20](addr=5081)
# 5101 .. 5200 - ..
G52 = p2g.Fixed[NAXES](addr=5201)
G54 = p2g.Fixed[NAXES](addr=5221)
G55 = p2g.Fixed[NAXES](addr=5241)
G56 = p2g.Fixed[NAXES](addr=5261)
G57 = p2g.Fixed[NAXES](addr=5281)
G58 = p2g.Fixed[NAXES](addr=5301)
G59 = p2g.Fixed[NAXES](addr=5321)
# 5341 .. 5400 - ..
TOOL_TBL_FEED_TIMERS = p2g.Fixed[100](addr=5401)
TOOL_TBL_TOTAL_TIMERS = p2g.Fixed[100](addr=5501)
TOOL_TBL_LIFE_LIMITS = p2g.Fixed[100](addr=5601)
TOOL_TBL_LIFE_COUNTERS = p2g.Fixed[100](addr=5701)
TOOL_TBL_LIFE_MAX_LOADS = p2g.Fixed[100](addr=5801)
TOOL_TBL_LIFE_LOAD_LIMITS = p2g.Fixed[100](addr=5901)
# 6001 .. 6197 - ..
NGC_CF = p2g.Fixed(addr=6198)
# 6199 .. 7000 - ..
G154_P1 = p2g.Fixed[NAXES](addr=7001)
G154_P2 = p2g.Fixed[NAXES](addr=7021)
G154_P3 = p2g.Fixed[NAXES](addr=7041)
G154_P4 = p2g.Fixed[NAXES](addr=7061)
G154_P5 = p2g.Fixed[NAXES](addr=7081)
G154_P6 = p2g.Fixed[NAXES](addr=7101)
G154_P7 = p2g.Fixed[NAXES](addr=7121)
G154_P8 = p2g.Fixed[NAXES](addr=7141)
G154_P9 = p2g.Fixed[NAXES](addr=7161)
G154_P10 = p2g.Fixed[NAXES](addr=7181)
G154_P11 = p2g.Fixed[NAXES](addr=7201)
G154_P12 = p2g.Fixed[NAXES](addr=7221)
G154_P13 = p2g.Fixed[NAXES](addr=7241)
G154_P14 = p2g.Fixed[NAXES](addr=7261)
G154_P15 = p2g.Fixed[NAXES](addr=7281)
G154_P16 = p2g.Fixed[NAXES](addr=7301)
G154_P17 = p2g.Fixed[NAXES](addr=7321)
G154_P18 = p2g.Fixed[NAXES](addr=7341)
G154_P19 = p2g.Fixed[NAXES](addr=7361)
G154_P20 = p2g.Fixed[NAXES](addr=7381)
# 7401 .. 7500 - ..
# 7501 .. 7600 PALLET_PRIORITY ..
# 7601 .. 7700 PALLET_STATUS ..
# 7701 .. 7800 PALLET_PROGRAM ..
# 7801 .. 7900 PALLET_USAGE ..
# 7901 .. 8499 - ..
ATM_ID = p2g.Fixed(addr=8500)
ATM_PERCENT = p2g.Fixed(addr=8501)
ATM_TOTAL_AVL_USAGE = p2g.Fixed(addr=8502)
ATM_TOTAL_AVL_HOLE_COUNT = p2g.Fixed(addr=8503)
ATM_TOTAL_AVL_FEED_TIME = p2g.Fixed(addr=8504)
ATM_TOTAL_AVL_TOTAL_TIME = p2g.Fixed(addr=8505)
# 8506 .. 8509 - ..
ATM_NEXT_TOOL_NUMBER = p2g.Fixed(addr=8510)
ATM_NEXT_TOOL_LIFE = p2g.Fixed(addr=8511)
ATM_NEXT_TOOL_AVL_USAGE = p2g.Fixed(addr=8512)
ATM_NEXT_TOOL_HOLE_COUNT = p2g.Fixed(addr=8513)
ATM_NEXT_TOOL_FEED_TIME = p2g.Fixed(addr=8514)
ATM_NEXT_TOOL_TOTAL_TIME = p2g.Fixed(addr=8515)
# 8516 .. 8549 - ..
TOOL_ID = p2g.Fixed(addr=8550)
TOOL_FLUTES = p2g.Fixed(addr=8551)
TOOL_MAX_VIBRATION = p2g.Fixed(addr=8552)
TOOL_LENGTH_OFFSETS = p2g.Fixed(addr=8553)
TOOL_LENGTH_WEAR = p2g.Fixed(addr=8554)
TOOL_DIAMETER_OFFSETS = p2g.Fixed(addr=8555)
TOOL_DIAMETER_WEAR = p2g.Fixed(addr=8556)
TOOL_ACTUAL_DIAMETER = p2g.Fixed(addr=8557)
TOOL_COOLANT_POSITION = p2g.Fixed(addr=8558)
TOOL_FEED_TIMER = p2g.Fixed(addr=8559)
TOOL_TOTAL_TIMER = p2g.Fixed(addr=8560)
TOOL_LIFE_LIMIT = p2g.Fixed(addr=8561)
TOOL_LIFE_COUNTER = p2g.Fixed(addr=8562)
TOOL_LIFE_MAX_LOAD = p2g.Fixed(addr=8563)
TOOL_LIFE_LOAD_LIMIT = p2g.Fixed(addr=8564)
# 8565 .. 8999 - ..
THERMAL_COMP_ACC = p2g.Fixed(addr=9000)
# 9001 .. 9015 - ..
THERMAL_SPINDLE_COMP_ACC = p2g.Fixed(addr=9016)
# 9017 .. 9999 - ..
GVARIABLES3 = p2g.Fixed[1000](addr=10000)
INPUTS1 = p2g.Fixed[256](addr=11000)
# 11256 .. 11999 - ..
OUTPUT1 = p2g.Fixed[256](addr=12000)
# 12256 .. 12999 - ..
FILTERED_ANALOG1 = p2g.Fixed[13](addr=13000)
COOLANT_LEVEL = p2g.Fixed(addr=13013)
FILTERED_ANALOG2 = p2g.Fixed[50](addr=13014)
# 13064 .. 13999 - ..
SETTING = p2g.Fixed[10000](addr=20000)
PARAMETER = p2g.Fixed[10000](addr=30000)
TOOL_TYP = p2g.Fixed[200](addr=50001)
TOOL_MATERIAL = p2g.Fixed[200](addr=50201)
# 50401 .. 101000 - ..
# 51001 .. 102300 - ..
CURRENT_OFFSET = p2g.Fixed[200](addr=50601)
CURRENT_OFFSET2 = p2g.Fixed[200](addr=50801)
VPS_TEMPLATE_OFFSET = p2g.Fixed[100](addr=51301)
WORK_MATERIAL = p2g.Fixed[200](addr=51401)
VPS_FEEDRATE = p2g.Fixed[200](addr=51601)
APPROX_LENGTH = p2g.Fixed[200](addr=51801)
APPROX_DIAMETER = p2g.Fixed[200](addr=52001)
EDGE_MEASURE_HEIGHT = p2g.Fixed[200](addr=52201)
TOOL_TOLERANCE = p2g.Fixed[200](addr=52401)
PROBE_TYPE = p2g.Fixed[200](addr=52601)
PROBE = p2g.alias(SKIP_POS)
WORK = p2g.alias(WORK_POS)
MACHINE = p2g.alias(MACHINE_POS)
G53 = p2g.alias(MACHINE_POS)
# MACHINE GEN ABOVE
