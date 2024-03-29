from p2g import axis
from p2g.coords import Fixed


# flake8: noqa

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
NULL                      = Fixed[    1](addr=   0)
MACRO_ARGUMENTS           = Fixed[   33](addr=   1)
GP_SAVED1                 = Fixed[   50](addr= 100)
PROBE_VALUES              = Fixed[   50](addr= 150)
GP_SAVED2                 = Fixed[   50](addr= 500)
PROBE_CALIB1              = Fixed[    6](addr= 550)
PROBE_R                   = Fixed[    3](addr= 556)
PROBE_CALIB2              = Fixed[   22](addr= 559)
GP_SAVED3                 = Fixed[  119](addr= 581)
GP_SAVED4                 = Fixed[  200](addr= 800)
INPUTS                    = Fixed[   64](addr=1000)
MAX_LOADS_XYZAB           = Fixed[    5](addr=1064)
RAW_ANALOG                = Fixed[   10](addr=1080)
FILTERED_ANALOG           = Fixed[    8](addr=1090)
SPINDLE_LOAD              = Fixed[    1](addr=1098)
MAX_LOADS_CTUVW           = Fixed[    5](addr=1264)
TOOL_TBL_FLUTES           = Fixed[  200](addr=1601)
TOOL_TBL_VIBRATION        = Fixed[  200](addr=1801)
TOOL_TBL_OFFSETS          = Fixed[  200](addr=2001)
TOOL_TBL_WEAR             = Fixed[  200](addr=2201)
TOOL_TBL_DROFFSET         = Fixed[  200](addr=2401)
TOOL_TBL_DRWEAR           = Fixed[  200](addr=2601)
ALARM                     = Fixed[    1](addr=3000)
T_MS                      = Fixed[    1](addr=3001)
T_HR                      = Fixed[    1](addr=3002)
SINGLE_BLOCK_OFF          = Fixed[    1](addr=3003)
FEED_HOLD_OFF             = Fixed[    1](addr=3004)
MESSAGE                   = Fixed[    1](addr=3006)
YEAR_MONTH_DAY            = Fixed[    1](addr=3011)
HOUR_MINUTE_SECOND        = Fixed[    1](addr=3012)
POWER_ON_TIME             = Fixed[    1](addr=3020)
CYCLE_START_TIME          = Fixed[    1](addr=3021)
FEED_TIMER                = Fixed[    1](addr=3022)
CUR_PART_TIMER            = Fixed[    1](addr=3023)
LAST_COMPLETE_PART_TIMER  = Fixed[    1](addr=3024)
LAST_PART_TIMER           = Fixed[    1](addr=3025)
TOOL_IN_SPIDLE            = Fixed[    1](addr=3026)
SPINDLE_RPM               = Fixed[    1](addr=3027)
PALLET_LOADED             = Fixed[    1](addr=3028)
SINGLE_BLOCK              = Fixed[    1](addr=3030)
AGAP                      = Fixed[    1](addr=3031)
BLOCK_DELETE              = Fixed[    1](addr=3032)
OPT_STOP                  = Fixed[    1](addr=3033)
TIMER_CELL_SAFE           = Fixed[    1](addr=3196)
TOOL_TBL_DIAMETER         = Fixed[  200](addr=3201)
TOOL_TBL_COOLANT_POSITION = Fixed[  200](addr=3401)
M30_COUNT1                = Fixed[    1](addr=3901)
M30_COUNT2                = Fixed[    1](addr=3902)
PREV_BLOCK                = Fixed[   13](addr=4001)
PREV_WCS                  = Fixed[    1](addr=4014)
PREV_BLOCK_ADDRESS        = Fixed[   26](addr=4101)
LAST_TARGET_POS           = Fixed[NAXES](addr=5001)
MACHINE_POS               = Fixed[NAXES](addr=5021)
WORK_POS                  = Fixed[NAXES](addr=5041)
SKIP_POS                  = Fixed[NAXES](addr=5061)
TOOL_OFFSET               = Fixed[NAXES](addr=5081)
G52                       = Fixed[NAXES](addr=5201)
G54                       = Fixed[NAXES](addr=5221)
G55                       = Fixed[NAXES](addr=5241)
G56                       = Fixed[NAXES](addr=5261)
G57                       = Fixed[NAXES](addr=5281)
G58                       = Fixed[NAXES](addr=5301)
G59                       = Fixed[NAXES](addr=5321)
TOOL_TBL_FEED_TIMERS      = Fixed[  100](addr=5401)
TOOL_TBL_TOTAL_TIMERS     = Fixed[  100](addr=5501)
TOOL_TBL_LIFE_LIMITS      = Fixed[  100](addr=5601)
TOOL_TBL_LIFE_COUNTERS    = Fixed[  100](addr=5701)
TOOL_TBL_LIFE_MAX_LOADS   = Fixed[  100](addr=5801)
TOOL_TBL_LIFE_LOAD_LIMITS = Fixed[  100](addr=5901)
NGC_CF                    = Fixed[    1](addr=6198)
G154_P1                   = Fixed[NAXES](addr=7001)
G154_P2                   = Fixed[NAXES](addr=7021)
G154_P3                   = Fixed[NAXES](addr=7041)
G154_P4                   = Fixed[NAXES](addr=7061)
G154_P5                   = Fixed[NAXES](addr=7081)
G154_P6                   = Fixed[NAXES](addr=7101)
G154_P7                   = Fixed[NAXES](addr=7121)
G154_P8                   = Fixed[NAXES](addr=7141)
G154_P9                   = Fixed[NAXES](addr=7161)
G154_P10                  = Fixed[NAXES](addr=7181)
G154_P11                  = Fixed[NAXES](addr=7201)
G154_P12                  = Fixed[NAXES](addr=7221)
G154_P13                  = Fixed[NAXES](addr=7241)
G154_P14                  = Fixed[NAXES](addr=7261)
G154_P15                  = Fixed[NAXES](addr=7281)
G154_P16                  = Fixed[NAXES](addr=7301)
G154_P17                  = Fixed[NAXES](addr=7321)
G154_P18                  = Fixed[NAXES](addr=7341)
G154_P19                  = Fixed[NAXES](addr=7361)
G154_P20                  = Fixed[NAXES](addr=7381)
ATM_ID                    = Fixed[    1](addr=8500)
ATM_PERCENT               = Fixed[    1](addr=8501)
ATM_TOTAL_AVL_USAGE       = Fixed[    1](addr=8502)
ATM_TOTAL_AVL_HOLE_COUNT  = Fixed[    1](addr=8503)
ATM_TOTAL_AVL_FEED_TIME   = Fixed[    1](addr=8504)
ATM_TOTAL_AVL_TOTAL_TIME  = Fixed[    1](addr=8505)
ATM_NEXT_TOOL_NUMBER      = Fixed[    1](addr=8510)
ATM_NEXT_TOOL_LIFE        = Fixed[    1](addr=8511)
ATM_NEXT_TOOL_AVL_USAGE   = Fixed[    1](addr=8512)
ATM_NEXT_TOOL_HOLE_COUNT  = Fixed[    1](addr=8513)
ATM_NEXT_TOOL_FEED_TIME   = Fixed[    1](addr=8514)
ATM_NEXT_TOOL_TOTAL_TIME  = Fixed[    1](addr=8515)
TOOL_ID                   = Fixed[    1](addr=8550)
TOOL_FLUTES               = Fixed[    1](addr=8551)
TOOL_MAX_VIBRATION        = Fixed[    1](addr=8552)
TOOL_LENGTH_OFFSETS       = Fixed[    1](addr=8553)
TOOL_LENGTH_WEAR          = Fixed[    1](addr=8554)
TOOL_DIAMETER_OFFSETS     = Fixed[    1](addr=8555)
TOOL_DIAMETER_WEAR        = Fixed[    1](addr=8556)
TOOL_ACTUAL_DIAMETER      = Fixed[    1](addr=8557)
TOOL_COOLANT_POSITION     = Fixed[    1](addr=8558)
TOOL_FEED_TIMER           = Fixed[    1](addr=8559)
TOOL_TOTAL_TIMER          = Fixed[    1](addr=8560)
TOOL_LIFE_LIMIT           = Fixed[    1](addr=8561)
TOOL_LIFE_COUNTER         = Fixed[    1](addr=8562)
TOOL_LIFE_MAX_LOAD        = Fixed[    1](addr=8563)
TOOL_LIFE_LOAD_LIMIT      = Fixed[    1](addr=8564)
THERMAL_COMP_ACC          = Fixed[    1](addr=9000)
THERMAL_SPINDLE_COMP_ACC  = Fixed[    1](addr=9016)
GVARIABLES3               = Fixed[ 1000](addr=10000)
PROBE_VALUES_             = Fixed[   50](addr=10150)
GPS1                      = Fixed[  200](addr=10200)
GPNS1                     = Fixed[  100](addr=10400)
GPS2                      = Fixed[   50](addr=10500)
PROBE_CALIB_              = Fixed[   50](addr=10550)
GPS3                      = Fixed[  100](addr=10600)
GPNS3                     = Fixed[  100](addr=10700)
GPS4                      = Fixed[  200](addr=10800)
INPUTS1                   = Fixed[  256](addr=11000)
OUTPUT1                   = Fixed[  256](addr=12000)
FILTERED_ANALOG1          = Fixed[   13](addr=13000)
COOLANT_LEVEL             = Fixed[    1](addr=13013)
FILTERED_ANALOG2          = Fixed[   50](addr=13014)
SETTING                   = Fixed[10000](addr=20000)
PARAMETER                 = Fixed[10000](addr=30000)
TOOL_TYP                  = Fixed[  200](addr=50001)
TOOL_MATERIAL             = Fixed[  200](addr=50201)
CURRENT_OFFSET            = Fixed[  200](addr=50601)
CURRENT_OFFSET2           = Fixed[  200](addr=50801)
VPS_TEMPLATE_OFFSET       = Fixed[  100](addr=51301)
WORK_MATERIAL             = Fixed[  200](addr=51401)
VPS_FEEDRATE              = Fixed[  200](addr=51601)
APPROX_LENGTH             = Fixed[  200](addr=51801)
APPROX_DIAMETER           = Fixed[  200](addr=52001)
EDGE_MEASURE_HEIGHT       = Fixed[  200](addr=52201)
TOOL_TOLERANCE            = Fixed[  200](addr=52401)
PROBE_TYPE                = Fixed[  200](addr=52601)
PROBE = SKIP_POS
WORK = WORK_POS
MACHINE = MACHINE_POS
G53 = MACHINE_POS
# MACHINE GEN ABOVE
