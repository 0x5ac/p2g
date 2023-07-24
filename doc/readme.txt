			_______________________

			 P2G - PYTHON 2 G-CODE

			     sac@0x5ac.com
			_______________________


Table of Contents
_________________

1. Version  0.2.222+2
2. Introduction
3. Usage
4. Install
5. Examples
.. 1. Simple demo
.. 2. Non trivial demo
6. Variables
7. Coordinates
8. Expressions
9. Axes
10. When
11. Goto
12. Printing
13. Symbol Tables
14. Notes
15. HAAS macro var definitions
16. Why


------------------------------------------------------------------------

(<file:https://codecov.io/gh/0x5ac/p2g/branch/master/graph/badge.svg?token=FKR0R7P8U1>)
(<file:https://img.shields.io/badge/License-MIT%20v3-blue.svg>)


1 Version  0.2.222+2
====================

  ----------------------------------------------------------------------


2 Introduction
==============

  Many styli died to bring us this information.

  This project makes it simpl(er) to ensure that parts are in fixtures
  correctly, coordinate systems are adjusted to deal with stock
  placement and cope with movement and rotation of workpieces through
  multiple operations.


  P2G is a compiler; it takes Python code, some definitions of machine
  specific variables, a little glue and makes G-code, so far, Haas
  ideomatic.

  Thanks to magic it can do surprising things with python data
  structures, anything reasonably calculated statically during
  compilation can be used in the source, classes, dicts, and so on.

  It comes with a set of macro variable definitions for a Haas mill with
  NCD.  And a few example settings for my own VF-3SSYT.

  ----------------------------------------------------------------------
  Table of Contents
  _________________

  1. Version  0.2.222+2
  2. Introduction
  3. Usage
  4. Install
  5. Examples
  .. 1. Simple demo
  .. 2. Non trivial demo
  6. Variables
  7. Coordinates
  8. Expressions
  9. Axes
  10. When
  11. Goto
  12. Printing
  13. Symbol Tables
  14. Notes
  15. HAAS macro var definitions
  16. Why

  ----------------------------------------------------------------------


3 Usage
=======

  ,----

  `----
  ,----
  | Example of program with many options using docopt.
  | 
  | Usage:
  |   p2g.py [options]  <srcfile> [<dstfile>] 
  |   p2g.py --help [<topic>]
  | 
  |     Example:
  |         p2g foo.py ~/_nc_/O{countdown}vc1-foo.nc
  |          Makes an output of the form ~/_nc_/O1234vc1-foo.nc
  |  
  |         p2g --func=thisone -
  |          Read from stdin, look for the 'thisone' function and write to
  |          to stdout.
  |  
  | 
  | Arguments:
  |   <srcfile>   Source python file. [default: stdin]
  |   <dstfile>   Destination G-Code file. [default: stdout]
  |                {countdown} in file name creates a decrementing prefix
  |                for the output file which makes looking for the .nc in
  |                a crowded directory less painful - it's at the top.
  |                (It's the number of minutes until midnight, so clear
  |                the directory once a day.)
  |   
  |   <topic>     [ topics | all | <topic>]
  |           <topic>  Print from readme starting at topic.                 
  |           topics:  List all topics.
  |           all      Print all readme.
  | 
  | Options:
  |      --job=<jobname>      Olabel for output code.
  |      --function=<fname>   Function to be compiled,
  |                            default is last one in source file.
  |      --break              pdb.set_trace() on error.
  |      --no-version         Don't put version number in outputs.
  |      --narrow             Emit comments on their own line,
  |                            makes text fit more easily into
  |                            a narrow program window.
  |      --verbose=<level>    Set verbosity level [default: 0]
  |      --version            Print version.
  |      --location           Print path of running executable.
  |      --examples=<dstdir>  Create <dstdir>, populate with
  |                               examples and compile.
  |  
  |           Examples:
  |             p2g examples showme
  |               Copies the examples into ./showme and then runs
  |                p2g showme/vicecenter.py showme/vicecenter.nc
  |                p2g showme/checkprobe.py showme/checkprobe.nc
  |  
  `----

  ----------------------------------------------------------------------


4 Install
=========

  ,----
  | $ pip install p2g
  `----

  ----------------------------------------------------------------------

  ----------------------------------------------------------------------


5 Examples
==========

  for a show:
  ,----
  | $ p2g examples dstdir
  `----

  ----------------------------------------------------------------------


5.1 Simple demo
~~~~~~~~~~~~~~~

  ,----
  | $ echo "
  `----
  ,----
  | import p2g
  | def t():
  |   x = p2g.Var(99)
  |   for y in range(10):
  |     x += y
  | 
  `----
  " | p2g -
  ,----
  | ⇨ directly ⇨
  `----
  ,----
  | O0001 (t: 0.2.351)
  |   #100= 99.                       (   x = Var[99]                 )
  |   #102= 0.                        (   for y in range[10]:         )
  | N1000
  |   IF [#102 GE 10.] GOTO 1002      (   for y in range[10]:         )
  |   #100= #100 + #102               ( x += y                        )
  |   #102= #102 + 1.
  |   GOTO 1000
  | N1002
  |   M30
  | %
  `----
  ----------------------------------------------------------------------


5.2 Non trivial demo
~~~~~~~~~~~~~~~~~~~~

  ,----
  | from p2g import *
  | from p2g.haas import *
  | class SearchParams:
  |     def __init__(self, name, search_depth, iota, delta):
  |         self.name = name
  |         self.its = 10
  |         self.search_depth = search_depth
  |         self.iota = iota
  |         self.delta = delta
  |         self.probe = goto.probe.work.feed(30).all
  |         self.go = goto.feed(640).work.all
  | 
  | 
  | def search(cursor, sch):
  |     # stick from class SearchParams  iterations into macro var
  |     its = Var(sch.its)
  |     while its > 0:
  |         # goto start point
  |         sch.go(cursor)
  |         # down until hit - or not.
  |         sch.probe(z=sch.search_depth)
  |         # if probe is below (+some slack) hit
  |         # point, then done.
  |         if SKIP_POS.z < sch.search_depth + sch.iota:
  |             break
  |         # otherwise move to next point
  |         cursor.xy += sch.delta
  |         its -= 1
  |     else:
  |         message(ALARM[0], f"too far {sch.name}.")
  | 
  | 
  | def demo1():
  |     cursor = Var[3](2, 3, 4)
  |     # searching right, look down 0.4", move
  |     # 1.5" right if nothing hit.
  |     sch1 = SearchParams(name="right", search_depth=-0.4, iota=-0.1, delta=(1.5, 0))
  |     search(cursor, sch1)
  | 

  `----
  ⇨ `p2g demo1.py' ⇨
  ,----
  | O0001 (demo1: 0.2.350)
  |   #100= 2.                        (   cursor = Var[3][2, 3, 4]    )
  |   #101= 3.
  |   #102= 4.
  |   #103= 10.                       (   its = Var[sch.its]          )
  | N1000
  |   IF [#103 LE 0.] GOTO 1002       (   while its > 0:              )
  |   G90 G01 F640. x#100 y#101 z#102 (       sch.go[cursor]          )
  |   G90 G31 F30. z-0.4              (       sch.probe[z=sch.search_depth])
  |   IF [#5063 LT -0.5] GOTO 1001    (       if SKIP_POS.z < sch.search_depth + sch.iota:)
  |   #100= #100 + 1.5                (       cursor.xy += sch.delta  )
  |   #103= #103 - 1.                 (       its -= 1                )
  |   GOTO 1000
  | N1002
  |   #3000 = 101 (too far right.)
  | N1001
  |   M30
  | %
  `----

  ----------------------------------------------------------------------


6 Variables
===========

  + Give names to macro variables at a known address:

    `Fixed' ❰ `[' /size/ `]' ❱_{opt} (`addr=' /addr/ ❰ `,' /init/
    ... ❱_{opt} `)'

  + Give names to macro variables automatically per function.

    `Var' ❰ `[' /size/ `]' ❱_{opt} (❰ `,' /init/ ... ❱_{opt} `)'

  + Not actually a variable, but same syntax.

    `Const' ❰ `[' /size/ `]' ❱_{opt} (❰ `,' /init/ ... ❱_{opt} `)'

  Example:
  ,----
  | 
  | from p2g import *  # this is the common header
  | from p2g.haas import *
  | 
  | 
  | def ex2():
  |     # On my machine, Renishaw skip positions are
  |     # in 5061, 5062, 5063.  Look in p2g.haas.py
  |     # for : SKIP_POS = p2g.Fixed[20](addr=5061)
  |     skip0 = SKIP_POS
  | 
  |     # can be done manualy too.
  |     skip1 = Fixed[3](addr=5061)
  | 
  |     # grab 5041.. from globals oto.
  |     workpos = WORK_POS
  |     tmp0 = Var(skip0.xyz * 2.0 + workpos + skip1)
  | 
  |     com("Define a constant ")
  |     above_tdc = Const(111, 222, 1333)
  | 
  |     com("Use it ")
  |     tmp0 += above_tdc
  | 
  `----

  ⇨ `p2g var1.py' ⇨

  ,----
  | O0001 (ex2)
  |   #100= #5061 * 2. + #5041 + #5061( tmp0 = Var[ skip0.xyz * 2.0 + workpos + skip1])
  |   #101= #5062 * 2. + #5042 + #5062
  |   #102= #5063 * 2. + #5043 + #5063
  | ( Define a constant  )
  | ( Use it  )
  |   #100= #100 + 111.               ( tmp0 += above_tdc             )
  |   #101= #101 + 222.
  |   #102= #102 + 1333.
  |   M30
  | %                                 ( 0.2.301                       )
  `----
  ----------------------------------------------------------------------


7 Coordinates
=============

  Describe position, with axis by location, in sequence or by name.
  ,----
  | from p2g import *  # this is the common header
  | from p2g.haas import *  # to all the examples
  | 
  | 
  | def co1():
  |     com("Describe 3 variables at 3000")
  |     dst = Fixed[3](addr=3000)
  |     com("Fill with 1,2,3")
  |     dst.var = (1, 2, 3)
  | 
  |     com("Set by parts")
  |     dst.y = 7
  |     dst.z = 71
  |     dst.x = 19
  | 
  |     offset = Const(0.101, 0.102, 0.103)
  |     com("Arithmetic")
  |     dst.var += (1, 2, 3)
  |     dst.var -= offset
  |     dst.var %= sin(asin(offset) + 7)
  | 
  |     com("When describing a location:")
  |     com("Coords by order.")
  |     p1 = Fixed[3](1, 2, 3, addr=100)
  | 
  |     com("Coords by axis name.")
  |     p2 = Fixed[3](z=333, y=222, x=111, addr=200)
  |     p2.x = 17
  | 
  |     com("Coords by index.")
  |     p1.xyz = p2[2]
  |     p2[1:3] = 7
  | 
  |     com("Mix them up.")
  |     p1.yz = p2.yz[1]
  | 

  `----

  ⇨ `p2g co1.py' ⇨
  ,----
  | O0001 (co1)
  | ( Describe 3 variables at 3000 )
  | ( Fill with 1,2,3 )
  |   #3000= 1.                       ( dst.var = [1,2,3]             )
  |   #3001= 2.
  |   #3002= 3.
  | ( Set by parts )
  |   #3001= 7.                       ( dst.y = 7                     )
  |   #3002= 71.                      ( dst.z = 71                    )
  |   #3000= 19.                      ( dst.x = 19                    )
  | ( Arithmetic )
  |   #3000= #3000 + 1.               ( dst.var += [1,2,3]            )
  |   #3001= #3001 + 2.
  |   #3002= #3002 + 3.
  |   #3000= #3000 - 0.101            ( dst.var -= offset             )
  |   #3001= #3001 - 0.102
  |   #3002= #3002 - 0.103
  |   #3000= #3000 MOD 0.2215         ( dst.var %= sin[asin[offset] + 7])
  |   #3001= #3001 MOD 0.2225
  |   #3002= #3002 MOD 0.2235
  | ( When describing a location: )
  | ( Coords by order. )
  |   #100= 1.                        ( p1 = Fixed[3][1, 2, 3, addr=100])
  |   #101= 2.
  |   #102= 3.
  | ( Coords by axis name. )
  |   #200= 111.                      ( p2 = Fixed[3][z=333, y=222, x=111, addr=200])
  |   #201= 222.
  |   #202= 333.
  |   #200= 17.                       ( p2.x = 17                     )
  | ( Coords by index. )
  |   #100= #202                      ( p1.xyz = p2[2]                )
  |   #101= #202
  |   #102= #202
  |   #201= 7.                        ( p2[1:3] = 7                   )
  |   #202= 7.
  | ( Mix them up. )
  |   #101= #202                      ( p1.yz = p2.yz[1]              )
  |   #102= #202
  |   M30
  | %                                 ( 0.2.301                       )
  `----

  ----------------------------------------------------------------------


8 Expressions
=============

  Python expressions turn into G-Code as you may expect, save that
  native Python uses radians for trig, and G-Code uses degrees, so
  folding is done in degrees.


  ,----
  | from p2g import *  # this is the common header
  | from p2g.haas import *  # to all the examples
  | 
  | 
  | def exp11():
  |     com("Variables go into macro variables.")
  |     theta = Var(0.3)
  |     angle = Var(sin(theta))
  | 
  |     com("Constants are elided in G-code.")
  |     thetak = Const(0.3)
  |     anglek = Var(sin(thetak))
  | 
  |     com("Lots of things are folded.")
  |     t1 = Var(2 * thetak + 7)
  | 
  |     com("Simple array math:")
  | 
  |     box_size = Const([4, 4, 2])
  |     tlhc = Var(-box_size / 2)
  |     brhc = Var(box_size / 2)
  |     diff = Var(tlhc - brhc)
  | 
  |     a, b, x = Var(), Var(), Var()
  |     a = tlhc[0] / tlhc[1]
  |     b = tlhc[0] % tlhc[1]
  |     x = tlhc[0] & tlhc[1]
  |     tlhc.xy = ((a - b + 3) / sin(x), (a + b + 3) / cos(x))
  | 
  | 
  | 

  `----
  ⇨ `p2g exp1.py' ⇨
  ,----
  | O0001 (exp11)
  | ( Variables go into macro variables. )
  |   #100= 0.3                       ( theta = Var[0.3]              )
  |   #101= SIN[#100]                 ( angle = Var[sin[theta]]       )
  | ( Constants don't exist in G-code. )
  |   #102= 0.0052                    ( anglek = Var[sin[thetak]]     )
  | ( Lots of things are folded. )
  |   #103= 7.6                       ( t1 = Var[2 * thetak  + 7]     )
  | ( Simple array math: )
  |   #104= -2.                       ( tlhc = Var[ - box_size / 2]   )
  |   #105= -2.
  |   #106= -1.
  |   #107= 2.                        ( brhc = Var[box_size / 2]      )
  |   #108= 2.
  |   #109= 1.
  |   #110= #104 - #107               ( diff = Var[tlhc - brhc]       )
  |   #111= #105 - #108
  |   #112= #106 - #109
  |   #113= #104 / #105               ( a = tlhc[0] / tlhc[1]         )
  |   #114= #104 MOD #105             ( b = tlhc[0] % tlhc[1]         )
  |   #115= #104 AND #105             ( x = tlhc[0] & tlhc[1]         )
  | ( tlhc.xy = [[a - b + 3] / sin[x],)
  |   #104= [#113 - #114 + 3.] / SIN[#115]
  |   #105= [#113 + #114 + 3.] / COS[#115]
  |   M30
  | %                                 ( 0.2.301                       )
  `----

  ----------------------------------------------------------------------


9 Axes
======

  Any number of axes are supported, default just being xy and z.

  A rotary on ac can be set with p2g.axis.NAMES="xyza*c".  The axis
  letters should be the same order as your machine expects coordinates
  to turn up in work offset registers.



  ,----
  | import p2g
  | from p2g.haas import *
  | 
  | 
  | def a5():
  |     p2g.axis.NAMES = "xyza*c"
  |     p2g.com("rhs of vector ops get expanded as needed")
  |     G55.var = [0, 1]
  |     p2g.com("fill yz and c with some stuff")
  |     tmp1 = p2g.Const(y=3, z=9, c=p2g.asin(0.5))
  |     p2g.com(
  |         "Unmentioned axes values are assumed", "to be 0, so adding them makes no code."
  |     )
  |     G55.var += tmp1
  |     p2g.com("")
  |     G55.ac *= 2.0
  | 
  |     p2g.com("Rotaries.")
  |     p4 = p2g.Fixed[6](addr=200)
  |     p4.a = 180
  |     p4.c = p2g.asin(0.5)
  | 
  | 
  | def a3():
  |     # xyz is the default.
  |     # but overridden because a5 called first, so
  |     p2g.axis.NAMES = "xyz"
  |     p2g.com("Filling to number of axes.")
  |     G55.var = [0]
  |     tmp = p2g.Var(G55 * 34)
  | 
  | 
  | def axes():
  |     a5()
  |     a3()
  `----
  ⇨ `p2g axes.py' ⇨
  ,----
  | O0001 (axes)
  | ( rhs of vector ops get expanded as needed )
  |   #5241= 0.                       (    G55.var = [0,1]            )
  |   #5242= 1.
  |   #5243= 0.
  |   #5244= 1.
  |   #5245= 0.
  |   #5246= 1.
  | ( fill yz and c with some stuff )
  | ( Unmentioned axes values are assumed    )
  | ( to be 0, so adding them makes no code. )
  |   #5242= #5242 + 3.               (    G55.var += tmp1            )
  |   #5243= #5243 + 9.
  |   #5246= #5246 + 30.
  | 
  |   #5244= #5244 * 2.               (    G55.ac *= 2.0              )
  |   #5246= #5246 * 2.
  | ( Rotaries. )
  |   #203= 180.                      (    p4.a = 180                 )
  |   #205= 30.                       (    p4.c = asin [0.5]          )
  | ( Filling to number of axes. )
  |   #5241= 0.                       (    G55.var = [0]              )
  |   #5242= 0.
  |   #5243= 0.
  |   #100= #5241 * 34.               (    tmp = Var[G55 * 34]        )
  |   #101= #5242 * 34.
  |   #102= #5243 * 34.
  |   M30
  | %                                 ( 0.2.301                       )
  `----


  ----------------------------------------------------------------------


10 When
=======

  'when' works as in python, save there are no exceptions; useful for
  turning on probing and magically getting it turned off,.  Or setting
  and restoring the wcs etc etc (look in p2g/lib.py)

  ,----
  | import p2g
  | from p2g import haas
  | 
  | PROBE = 1
  | 
  | 
  | class Optional:
  |     prev: str
  | 
  |     def __init__(self):
  |         self.prev = p2g.stat.OPT_PREFIX
  |         p2g.stat.OPT_PREFIX = "/ "
  | 
  |     def __enter__(self):
  |         pass
  | 
  |     def __exit__(self, *_):
  |         p2g.stat.OPT_PREFIX = self.prev
  | 
  | 
  | class Probe:
  |     def __enter__(self):
  |         p2g.load_tool(PROBE)
  |         p2g.codenl(haas.SPINDLE_PROBE_ON, comment_txt="Probe on.")
  | 
  |     def __exit__(self, *_):
  |         p2g.codenl(haas.SPINDLE_PROBE_OFF, comment_txt="Probe off.")
  | 
  | 
  | def when_demo():
  |     with Probe():
  |         tmp = p2g.Var(9)
  |         with Optional():
  |             tmp.var += 98
  |         p2g.dprint(f"tmp is {tmp}")
  | 

  `----
  ⇨ `p2g whendemo.py' ⇨
  ,----
  | O0001 (when_demo : 0.2.333)
  |   T01 M06                         (     load_tool[PROBE]          )
  |   G65 P9832                       ( Probe on.                     )
  |   #100= 9.                        (  tmp = Var[9]                 )
  | /   #100= #100 + 98.                (     tmp.var += 98             )
  | DPRNT[tmp*is*[#100]]
  |   G65 P9833                       ( Probe off.                    )
  |   M30
  | %
  `----




  ----------------------------------------------------------------------


11 Goto
=======

  Goto functions are constructed from parts, and make building blocks
  when partially applied.

  `goto' ❰ `.'  /modifier/ ❱* `(' /coordinates/ `)'

  /modifier/ :
  - `r9810' Use Renishaw macro 9810 to do a protected positioning cycle.
  - `work' Use current work coordinate system. - whatever set with
    set_wcs
  - `machine' Use the machine coordinate system - G53
  - `relative' Use relative coordinate system - G91
  - `absolute' Use absolute coordinate system - G90
  - `z_first' move Z axis first.
  - `z_last' move the other axes before the Z.
  - `probe' Emit probe code using G31.
  - `xyz' Move all axes at once.
  - `feed(' /expr/ `)' Set feed rate.
  - `mcode(' /string/ `)' Apply an mcode.


  ,----
  | from p2g import *
  | 
  | 
  | def goto1():
  |     symbol.Table.print = True
  |     g1 = goto.work.feed(20).all
  | 
  |     comment("in work cosys, goto x=1, y=2, z=3 at 20ips")
  |     g1(1, 2, 3)
  | 
  |     comment("make a variable, 2,3,4")
  |     v1 = Var(x=2, y=3, z=4)
  | 
  |     absslow = goto.machine.feed(10)
  | 
  |     comment("In the machine cosys, move to v1.z then v1.xy, slowly")
  | 
  |     absslow.z_first(v1)
  | 
  |     comment("p1 is whatever absslow was, with feed adjusted to 100.")
  |     p1 = absslow.feed(100)
  |     p1.z_last(v1)
  | 
  |     comment("p2 is whatever p1 was, with changed to a probe.")
  |     p2 = p1.probe
  |     p2.z_last(v1)
  | 
  |     comment("move a and c axes ")
  |     axis.NAMES = "xyza*c"
  |     goto.feed(20).all.relative(a=9, c=90)
  | 
  |     comment("probe with a hass MUST_SKIP mcode.")
  |     goto.probe.feed(10).mcode("M79").relative.all(3, 4, 5)
  | 
  |     comment("Define shortcut for safe_goto and use.")
  |     safe_goto = goto.feed(20).r9810
  | 
  |     safe_goto.z_first(1, 2, 3)
  `----
  ⇨ `p2g goto1.py` ⇨
  ,----
  | O0001 (goto1)
  | ( Symbol Table )
  | 
  |  ( v1 :  #100.x  #101.y  #102.z )
  | 
  | 
  | ( in work cosys, goto x=1, y=2, z=3 at 20ips )
  |   G90 G01 F20. x1. y2. z3.        ( g1 [1,2,3]                    )
  | 
  | ( make a variable, 2,3,4 )
  |   #100= 2.                        ( v1 = Var[x=2,y=3,z=4]         )
  |   #101= 3.
  |   #102= 4.
  | 
  | ( In the machine cosys, move to v1.z then v1.xy, slowly )
  |   G90 G53 G01 F10. z#102          ( absslow.z_first[v1]           )
  |   G90 G53 G01 F10. x#100 y#101
  | 
  | ( p1 is whatever absslow was, with feed adjusted to 100. )
  |   G90 G53 G01 F100. x#100 y#101   ( p1.z_last[v1]                 )
  |   G90 G53 G01 F100. z#102
  | 
  | ( p2 is whatever p1 was, with changed to a probe. )
  |   G90 G53 G31 F100. x#100 y#101   ( p2.z_last[v1]                 )
  |   G90 G53 G31 F100. z#102
  | 
  | ( move a and c axes  )
  |   G91 G01 F20. a9. c90.           ( goto.feed[20].all.relative [a=9, c= 90])
  | 
  | ( probe with a hass MUST_SKIP mcode. )
  |   G91 G31 M79 F10. x3. y4. z5.    ( goto.probe.feed[10].mcode["M79"].relative.all[3,4,5])
  | 
  | ( Define shortcut for safe_goto and use. )
  |   G65 R9810 F20. z3.              ( safe_goto.z_first[1,2,3]      )
  |   G65 R9810 F20. x1. y2.
  |   M30
  | %                                 ( 0.2.301                       )
  `----

  ----------------------------------------------------------------------


12 Printing
===========

  Turns Python f string prints into G-code DPRNT.  Make sure that your
  print string does not have any characters in it that your machine
  considers to be illegal in a DPRNT string.


  ,----
  | from p2g import *
  | from p2g.haas import *
  | 
  | 
  | def exprnt():
  |     x = Var(2)
  |     y = Var(27)
  | 
  |     for q in range(10):
  |         dprint(f"X is {x:3.1f}, Y+Q is {y+q:5.2f}")
  | 

  `----
  ⇨ `p2g exprnt.py' ⇨
  ,----
  | O0001 (exprnt : 0.2.333)
  |   #100= 2.                        (   x = Var[2]                  )
  |   #101= 27.                       (   y = Var[27]                 )
  |   #103= 0.                        (   for q in range[10]:         )
  | N1000
  |   IF [#103 GE 10.] GOTO 1002      (   for q in range[10]:         )
  | DPRNT[X*is*[#100][31],*Y+Q*is*[#101+#103][52]]
  |   #103= #103 + 1.                 ( dprint[f"X is {x:3.1f}, Y+Q is {y+q:5.2f}"])
  |   GOTO 1000
  | N1002
  |   M30
  | %
  `----

  ----------------------------------------------------------------------


13 Symbol Tables
================

  Set the global `p2g.symbol.Table.print' to get a symbol table in the
  output file.

  ,----
  | import p2g
  | x1 = -7
  | MACHINE_ABS_ABOVE_OTS = p2g.Const(x=x1, y=8, z=9)
  | MACHINE_ABS_ABOVE_SEARCH_ROTARY_LHS_5X8 = p2g.Const(100, 101, 102)
  | MACHINE_ABS_ABOVE_VICE = p2g.Const(x=17, y=18, z=19)
  |  RAW_ANALOG = p2g.Fixed[10](addr=1080)
  | fish = 10
  | not_used = 12
  | 
  | def stest():
  |       p2g.symbol.Table.print = True    
  |       p2g.comment("Only used symbols are in output table.")
  |       p2g.Var(MACHINE_ABS_ABOVE_OTS)
  |       p2g.Var(MACHINE_ABS_ABOVE_VICE * fish)
  |       v1 = p2g.Var()
  |       v1 += RAW_ANALOG[7]
  `----
  ⇨ `p2g stest.py` ⇨
  ,----
  | O0001 (stest)
  | ( Symbol Table )
  | 
  |  ( MACHINE_ABS_ABOVE_OTS                   :  -7.000,  8.000,  9.000 )
  |  ( MACHINE_ABS_ABOVE_SEARCH_ROTARY_LHS_5X8 : 100.000,101.000,102.000 )
  |  ( MACHINE_ABS_ABOVE_VICE                  :  17.000, 18.000, 19.000 )
  | 
  |  ( RAW_ANALOG                              : #1080[10]               )
  |  ( v1                                      :  #106.x                 )
  | 
  | 
  | ( Only used symbols are in output table. )
  |   #100= -7.                       ( Var[MACHINE_ABS_ABOVE_OTS]    )
  |   #101= 8.
  |   #102= 9.
  |   #103= 170.                      ( Var[MACHINE_ABS_ABOVE_VICE * fish])
  |   #104= 180.
  |   #105= 190.
  |   #106= #106 + #1087              ( v1 += RAW_ANALOG[7]           )
  |   M30
  | %                                 ( 0.2.301                       )
  `----

  ----------------------------------------------------------------------


14 Notes
========

  The entire thing is brittle; I've only used it to make code for my own
  limited purposes.

  Nice things:

  ,----
  | 
  | from p2g import *
  | from p2g.haas import *
  | 
  | 
  | class X:
  |     def __init__(self, a, b):
  |         self.thisone = a
  |         self.b = b
  | 
  |     def adjust(self, tof):
  |         self.thisone += tof.x
  |         self.b += tof.y
  | 
  | 
  | class Y:
  |     def __init__(self, a):
  |         self.val = a
  | 
  |     def adjust(self, tof):
  |         self.val += tof
  | 
  |     # an example of overloading.
  |     # I'm not recommending replacing
  |     # add with multiply, but it would work.
  |     def __add__(self, other):
  |         return self.val * other + 3
  | 
  | 
  | def cool():
  |     com("You can do surprising things.")
  | 
  |     avariable = Var(100)
  |     objp = X(avariable, 34)
  |     another = Var(7, 8)
  | 
  |     objp.adjust(TOOL_OFFSET)
  | 
  |     q = Y(another) + (objp.thisone, objp.b)
  |     dprint(f"{q[0]}{q[1]}")
  | 
  `----
  ⇨ `p2g notes.py' ⇨
  ,----
  | O0001 (cool)
  | ( You can do surprising things. )
  |   #100= 100.                      (   avariable = Var[100]        )
  |   #101= 7.                        (   another = Var[7,8]          )
  |   #102= 8.
  | DPRNT[[#101*[#100+#5081]+3.][#102*[#5082+34.]+3.]]
  |   M30
  | %                                 ( 0.2.301                       )
  `----






  ,----
  | import p2g
  | from p2g.haas import *
  | 
  | G55 = p2g.Fixed[3](addr=5241)
  | 
  | def beware():
  |         p2g.com(
  |             "Names on the left hand side of an assignment need to be",
  |             "treated with care.  A simple.",
  |         )
  |         G55 = [0, 0, 0]
  |         p2g.com(
  |             "Will not do what you want - this will overwrite the definition",
  |             "of G55 above - so no code will be generated.",
  |         )
  | 
  |         p2g.com(
  |             "You need to use .var (for everything), explicitly name the axes,"
  |             "or use magic slicing."
  |         )
  | 
  |         G56.var = [1, 1, 1]
  |         G56.xyz = [2, 2, 2]
  |         G56[:] = [3, 3, 3]
  | 
  `----
  ⇨ `p2g beware.py' ⇨
  ,----
  | O0001 (beware)
  | ( Names on the left hand side of an assignment need to be )
  | ( treated with care.  A simple.                           )
  | ( Will not do what you want - this will overwrite the definition )
  | ( of G55 above - so no code will be generated.                   )
  | ( You need to use .var [for everything], explicitly name the axes,or use magic slicing. )
  |   #5261= 1.                       ( G56.var = [1, 1, 1]           )
  |   #5262= 1.
  |   #5263= 1.
  |   #5261= 2.                       ( G56.xyz = [2, 2, 2]           )
  |   #5262= 2.
  |   #5263= 2.
  |   #5261= 3.                       ( G56[:] = [3, 3, 3]            )
  |   #5262= 3.
  |   #5263= 3.
  |   M30
  | %                                 ( 0.2.301                       )
  `----

  ,----
  | from p2g import *
  | from p2g.haas import *
  | 
  | 
  | def beware1():
  |     com(
  |         "It's easy to forget that only macro variables will get into",
  |         "the output code. Other code will go away.",
  |     )
  |     x = 123  # not a var
  |     y = Var(7)
  |     if x == 23:  # look here
  |         y = 9
  | 
  |     com("Should look like:")
  |     x = Var(123)  # is a var
  |     y = Var(7)
  |     if x == 23:  # look here
  |         y = 9
  |     else:
  |         y = 99
  | 
  `----

  ,----
  | O0001 (beware1)
  | ( It's easy to forget that only macro variables will get into )
  | ( the output code. Other code will go away.                   )
  |   #100= 7.                        ( y = Var[7]                    )
  | ( Should look like: )
  |   #101= 123.                      ( x = Var[123]  # is a var      )
  |   #102= 7.                        ( y = Var[7]                    )
  |   #100= #102
  |   IF [#101 NE 23.] GOTO 1002      ( if x == 23:  # look here      )
  |   #100= 9.                        (     y = 9                     )
  |   GOTO 1003
  | N1002
  |   #100= 99.                       (     y = 99                    )
  | N1003
  |   M30
  | %
  `----

  ----------------------------------------------------------------------


15 HAAS macro var definitions
=============================

  Names predefined in p2g.haas:


   <code>Name</code>                       <code>Size</code>   <code>Address</code>          
   ---                                     ---                 ---                           
   <code>NULL</code>                       <code>    1</code>  <code>     #    0    </code>  
   <code>MACRO_ARGUMENTS</code>            <code>   33</code>  <code>#    1 … #   33</code>  
   <code>GAP01</code>                      <code>   66</code>  <code>#   34 … #   99</code>  
   <code>GP_SAVED1</code>                  <code>  100</code>  <code>#  100 … #  199</code>  
   <code>GAP02</code>                      <code>  300</code>  <code>#  200 … #  499</code>  
   <code>GP_SAVED2</code>                  <code>   50</code>  <code>#  500 … #  549</code>  
   <code>PROBE_CALIBRATION1</code>         <code>    6</code>  <code>#  550 … #  555</code>  
   <code>PROBE_R</code>                    <code>    3</code>  <code>#  556 … #  558</code>  
   <code>PROBE_CALIBRATION2</code>         <code>   22</code>  <code>#  559 … #  580</code>  
   <code>GP_SAVED3</code>                  <code>  119</code>  <code>#  581 … #  699</code>  
   <code>GAP03</code>                      <code>  100</code>  <code>#  700 … #  799</code>  
   <code>GP_SAVED4</code>                  <code>  200</code>  <code>#  800 … #  999</code>  
   <code>INPUTS</code>                     <code>   64</code>  <code># 1000 … # 1063</code>  
   <code>MAX_LOADS_XYZAB</code>            <code>    5</code>  <code># 1064 … # 1068</code>  
   <code>GAP04</code>                      <code>   11</code>  <code># 1069 … # 1079</code>  
   <code>RAW_ANALOG</code>                 <code>   10</code>  <code># 1080 … # 1089</code>  
   <code>FILTERED_ANALOG</code>            <code>    8</code>  <code># 1090 … # 1097</code>  
   <code>SPINDLE_LOAD</code>               <code>    1</code>  <code>     # 1098    </code>  
   <code>GAP05</code>                      <code>  165</code>  <code># 1099 … # 1263</code>  
   <code>MAX_LOADS_CTUVW</code>            <code>    5</code>  <code># 1264 … # 1268</code>  
   <code>GAP06</code>                      <code>  332</code>  <code># 1269 … # 1600</code>  
   <code>TOOL_TBL_FLUTES</code>            <code>  200</code>  <code># 1601 … # 1800</code>  
   <code>TOOL_TBL_VIBRATION</code>         <code>  200</code>  <code># 1801 … # 2000</code>  
   <code>TOOL_TBL_OFFSETS</code>           <code>  200</code>  <code># 2001 … # 2200</code>  
   <code>TOOL_TBL_WEAR</code>              <code>  200</code>  <code># 2201 … # 2400</code>  
   <code>TOOL_TBL_DROFFSET</code>          <code>  200</code>  <code># 2401 … # 2600</code>  
   <code>TOOL_TBL_DRWEAR</code>            <code>  200</code>  <code># 2601 … # 2800</code>  
   <code>GAP07</code>                      <code>  199</code>  <code># 2801 … # 2999</code>  
   <code>ALARM</code>                      <code>    1</code>  <code>     # 3000    </code>  
   <code>T_MS</code>                       <code>    1</code>  <code>     # 3001    </code>  
   <code>T_HR</code>                       <code>    1</code>  <code>     # 3002    </code>  
   <code>SINGLE_BLOCK_OFF</code>           <code>    1</code>  <code>     # 3003    </code>  
   <code>FEED_HOLD_OFF</code>              <code>    1</code>  <code>     # 3004    </code>  
   <code>GAP08</code>                      <code>    1</code>  <code>     # 3005    </code>  
   <code>MESSAGE</code>                    <code>    1</code>  <code>     # 3006    </code>  
   <code>GAP09</code>                      <code>    4</code>  <code># 3007 … # 3010</code>  
   <code>YEAR_MONTH_DAY</code>             <code>    1</code>  <code>     # 3011    </code>  
   <code>HOUR_MINUTE_SECOND</code>         <code>    1</code>  <code>     # 3012    </code>  
   <code>GAP10</code>                      <code>    7</code>  <code># 3013 … # 3019</code>  
   <code>POWER_ON_TIME</code>              <code>    1</code>  <code>     # 3020    </code>  
   <code>CYCLE_START_TIME</code>           <code>    1</code>  <code>     # 3021    </code>  
   <code>FEED_TIMER</code>                 <code>    1</code>  <code>     # 3022    </code>  
   <code>CUR_PART_TIMER</code>             <code>    1</code>  <code>     # 3023    </code>  
   <code>LAST_COMPLETE_PART_TIMER</code>   <code>    1</code>  <code>     # 3024    </code>  
   <code>LAST_PART_TIMER</code>            <code>    1</code>  <code>     # 3025    </code>  
   <code>TOOL_IN_SPIDLE</code>             <code>    1</code>  <code>     # 3026    </code>  
   <code>SPINDLE_RPM</code>                <code>    1</code>  <code>     # 3027    </code>  
   <code>PALLET_LOADED</code>              <code>    1</code>  <code>     # 3028    </code>  
   <code>GAP11</code>                      <code>    1</code>  <code>     # 3029    </code>  
   <code>SINGLE_BLOCK</code>               <code>    1</code>  <code>     # 3030    </code>  
   <code>AGAP</code>                       <code>    1</code>  <code>     # 3031    </code>  
   <code>BLOCK_DELETE</code>               <code>    1</code>  <code>     # 3032    </code>  
   <code>OPT_STOP</code>                   <code>    1</code>  <code>     # 3033    </code>  
   <code>GAP12</code>                      <code>  162</code>  <code># 3034 … # 3195</code>  
   <code>TIMER_CELL_SAFE</code>            <code>    1</code>  <code>     # 3196    </code>  
   <code>GAP13</code>                      <code>    4</code>  <code># 3197 … # 3200</code>  
   <code>TOOL_TBL_DIAMETER</code>          <code>  200</code>  <code># 3201 … # 3400</code>  
   <code>TOOL_TBL_COOLANT_POSITION</code>  <code>  200</code>  <code># 3401 … # 3600</code>  
   <code>GAP14</code>                      <code>  300</code>  <code># 3601 … # 3900</code>  
   <code>M30_COUNT1</code>                 <code>    1</code>  <code>     # 3901    </code>  
   <code>M30_COUNT2</code>                 <code>    1</code>  <code>     # 3902    </code>  
   <code>GAP15</code>                      <code>   98</code>  <code># 3903 … # 4000</code>  
   <code>LAST_BLOCK_G</code>               <code>   13</code>  <code># 4001 … # 4013</code>  
   <code>LAST_WCS</code>                   <code>    1</code>  <code>     # 4014    </code>  
   <code>GAP16</code>                      <code>   79</code>  <code># 4022 … # 4100</code>  
   <code>LAST_BLOCK_ADDRESS</code>         <code>   26</code>  <code># 4101 … # 4126</code>  
   <code>GAP17</code>                      <code>  874</code>  <code># 4127 … # 5000</code>  
   <code>LAST_TARGET_POS</code>            <code>naxes</code>  <code>    # 5001…    </code>  
   <code>MACHINE_POS</code>                <code>naxes</code>  <code>    # 5021…    </code>  
   <code>MACHINE</code>                    <code>naxes</code>  <code>    # 5021…    </code>  
   <code>G53</code>                        <code>naxes</code>  <code>    # 5021…    </code>  
   <code>WORK_POS</code>                   <code>naxes</code>  <code>    # 5041…    </code>  
   <code>WORK</code>                       <code>naxes</code>  <code>    # 5041…    </code>  
   <code>SKIP_POS</code>                   <code>naxes</code>  <code>    # 5061…    </code>  
   <code>PROBE</code>                      <code>naxes</code>  <code>    # 5061…    </code>  
   <code>TOOL_OFFSET</code>                <code>   20</code>  <code># 5081 … # 5100</code>  
   <code>GAP18</code>                      <code>  100</code>  <code># 5101 … # 5200</code>  
   <code>G52</code>                        <code>naxes</code>  <code>    # 5201…    </code>  
   <code>G54</code>                        <code>naxes</code>  <code>    # 5221…    </code>  
   <code>G55</code>                        <code>naxes</code>  <code>    # 5241…    </code>  
   <code>G56</code>                        <code>naxes</code>  <code>    # 5261…    </code>  
   <code>G57</code>                        <code>naxes</code>  <code>    # 5281…    </code>  
   <code>G58</code>                        <code>naxes</code>  <code>    # 5301…    </code>  
   <code>G59</code>                        <code>naxes</code>  <code>    # 5321…    </code>  
   <code>GAP19</code>                      <code>   60</code>  <code># 5341 … # 5400</code>  
   <code>TOOL_TBL_FEED_TIMERS</code>       <code>  100</code>  <code># 5401 … # 5500</code>  
   <code>TOOL_TBL_TOTAL_TIMERS</code>      <code>  100</code>  <code># 5501 … # 5600</code>  
   <code>TOOL_TBL_LIFE_LIMITS</code>       <code>  100</code>  <code># 5601 … # 5700</code>  
   <code>TOOL_TBL_LIFE_COUNTERS</code>     <code>  100</code>  <code># 5701 … # 5800</code>  
   <code>TOOL_TBL_LIFE_MAX_LOADS</code>    <code>  100</code>  <code># 5801 … # 5900</code>  
   <code>TOOL_TBL_LIFE_LOAD_LIMITS</code>  <code>  100</code>  <code># 5901 … # 6000</code>  
   <code>GAP20</code>                      <code>  197</code>  <code># 6001 … # 6197</code>  
   <code>NGC_CF</code>                     <code>    1</code>  <code>     # 6198    </code>  
   <code>GAP21</code>                      <code>  802</code>  <code># 6199 … # 7000</code>  
   <code>G154_P1</code>                    <code>naxes</code>  <code>    # 7001…    </code>  
   <code>G154_P2</code>                    <code>naxes</code>  <code>    # 7021…    </code>  
   <code>G154_P3</code>                    <code>naxes</code>  <code>    # 7041…    </code>  
   <code>G154_P4</code>                    <code>naxes</code>  <code>    # 7061…    </code>  
   <code>G154_P5</code>                    <code>naxes</code>  <code>    # 7081…    </code>  
   <code>G154_P6</code>                    <code>naxes</code>  <code>    # 7101…    </code>  
   <code>G154_P7</code>                    <code>naxes</code>  <code>    # 7121…    </code>  
   <code>G154_P8</code>                    <code>naxes</code>  <code>    # 7141…    </code>  
   <code>G154_P9</code>                    <code>naxes</code>  <code>    # 7161…    </code>  
   <code>G154_P10</code>                   <code>naxes</code>  <code>    # 7181…    </code>  
   <code>G154_P11</code>                   <code>naxes</code>  <code>    # 7201…    </code>  
   <code>G154_P12</code>                   <code>naxes</code>  <code>    # 7221…    </code>  
   <code>G154_P13</code>                   <code>naxes</code>  <code>    # 7241…    </code>  
   <code>G154_P14</code>                   <code>naxes</code>  <code>    # 7261…    </code>  
   <code>G154_P15</code>                   <code>naxes</code>  <code>    # 7281…    </code>  
   <code>G154_P16</code>                   <code>naxes</code>  <code>    # 7301…    </code>  
   <code>G154_P17</code>                   <code>naxes</code>  <code>    # 7321…    </code>  
   <code>G154_P18</code>                   <code>naxes</code>  <code>    # 7341…    </code>  
   <code>G154_P19</code>                   <code>naxes</code>  <code>    # 7361…    </code>  
   <code>G154_P20</code>                   <code>naxes</code>  <code>    # 7381…    </code>  
   <code>GAP22</code>                      <code>  100</code>  <code># 7401 … # 7500</code>  
   <code>PALLET_PRIORITY</code>            <code>  100</code>  <code># 7501 … # 7600</code>  
   <code>PALLET_STATUS</code>              <code>  100</code>  <code># 7601 … # 7700</code>  
   <code>PALLET_PROGRAM</code>             <code>  100</code>  <code># 7701 … # 7800</code>  
   <code>PALLET_USAGE</code>               <code>  100</code>  <code># 7801 … # 7900</code>  
   <code>GAP23</code>                      <code>  599</code>  <code># 7901 … # 8499</code>  
   <code>ATM_ID</code>                     <code>    1</code>  <code>     # 8500    </code>  
   <code>ATM_PERCENT</code>                <code>    1</code>  <code>     # 8501    </code>  
   <code>ATM_TOTAL_AVL_USAGE</code>        <code>    1</code>  <code>     # 8502    </code>  
   <code>ATM_TOTAL_AVL_HOLE_COUNT</code>   <code>    1</code>  <code>     # 8503    </code>  
   <code>ATM_TOTAL_AVL_FEED_TIME</code>    <code>    1</code>  <code>     # 8504    </code>  
   <code>ATM_TOTAL_AVL_TOTAL_TIME</code>   <code>    1</code>  <code>     # 8505    </code>  
   <code>GAP24</code>                      <code>    4</code>  <code># 8506 … # 8509</code>  
   <code>ATM_NEXT_TOOL_NUMBER</code>       <code>    1</code>  <code>     # 8510    </code>  
   <code>ATM_NEXT_TOOL_LIFE</code>         <code>    1</code>  <code>     # 8511    </code>  
   <code>ATM_NEXT_TOOL_AVL_USAGE</code>    <code>    1</code>  <code>     # 8512    </code>  
   <code>ATM_NEXT_TOOL_HOLE_COUNT</code>   <code>    1</code>  <code>     # 8513    </code>  
   <code>ATM_NEXT_TOOL_FEED_TIME</code>    <code>    1</code>  <code>     # 8514    </code>  
   <code>ATM_NEXT_TOOL_TOTAL_TIME</code>   <code>    1</code>  <code>     # 8515    </code>  
   <code>GAP25</code>                      <code>   34</code>  <code># 8516 … # 8549</code>  
   <code>TOOL_ID</code>                    <code>    1</code>  <code>     # 8550    </code>  
   <code>TOOL_FLUTES</code>                <code>    1</code>  <code>     # 8551    </code>  
   <code>TOOL_MAX_VIBRATION</code>         <code>    1</code>  <code>     # 8552    </code>  
   <code>TOOL_LENGTH_OFFSETS</code>        <code>    1</code>  <code>     # 8553    </code>  
   <code>TOOL_LENGTH_WEAR</code>           <code>    1</code>  <code>     # 8554    </code>  
   <code>TOOL_DIAMETER_OFFSETS</code>      <code>    1</code>  <code>     # 8555    </code>  
   <code>TOOL_DIAMETER_WEAR</code>         <code>    1</code>  <code>     # 8556    </code>  
   <code>TOOL_ACTUAL_DIAMETER</code>       <code>    1</code>  <code>     # 8557    </code>  
   <code>TOOL_COOLANT_POSITION</code>      <code>    1</code>  <code>     # 8558    </code>  
   <code>TOOL_FEED_TIMER</code>            <code>    1</code>  <code>     # 8559    </code>  
   <code>TOOL_TOTAL_TIMER</code>           <code>    1</code>  <code>     # 8560    </code>  
   <code>TOOL_LIFE_LIMIT</code>            <code>    1</code>  <code>     # 8561    </code>  
   <code>TOOL_LIFE_COUNTER</code>          <code>    1</code>  <code>     # 8562    </code>  
   <code>TOOL_LIFE_MAX_LOAD</code>         <code>    1</code>  <code>     # 8563    </code>  
   <code>TOOL_LIFE_LOAD_LIMIT</code>       <code>    1</code>  <code>     # 8564    </code>  
   <code>GAP26</code>                      <code>  435</code>  <code># 8565 … # 8999</code>  
   <code>THERMAL_COMP_ACC</code>           <code>    1</code>  <code>     # 9000    </code>  
   <code>GAP27</code>                      <code>   15</code>  <code># 9001 … # 9015</code>  
   <code>THERMAL_SPINDLE_COMP_ACC</code>   <code>    1</code>  <code>     # 9016    </code>  
   <code>GAP28</code>                      <code>  983</code>  <code># 9017 … # 9999</code>  
   <code>GVARIABLES3</code>                <code> 1000</code>  <code>#10000 … #10999</code>  
   <code>INPUTS1</code>                    <code>  256</code>  <code>#11000 … #11255</code>  
   <code>GAP29</code>                      <code>  744</code>  <code>#11256 … #11999</code>  
   <code>OUTPUT1</code>                    <code>  256</code>  <code>#12000 … #12255</code>  
   <code>GAP30</code>                      <code>  744</code>  <code>#12256 … #12999</code>  
   <code>FILTERED_ANALOG1</code>           <code>   13</code>  <code>#13000 … #13012</code>  
   <code>COOLANT_LEVEL</code>              <code>    1</code>  <code>     #13013    </code>  
   <code>FILTERED_ANALOG2</code>           <code>   50</code>  <code>#13014 … #13063</code>  
   <code>GAP31</code>                      <code>  936</code>  <code>#13064 … #13999</code>  
   <code>SETTING</code>                    <code>10000</code>  <code>#20000 … #29999</code>  
   <code>PARAMETER</code>                  <code>10000</code>  <code>#30000 … #39999</code>  
   <code>TOOL_TYP</code>                   <code>  200</code>  <code>#50001 … #50200</code>  
   <code>TOOL_MATERIAL</code>              <code>  200</code>  <code>#50201 … #50400</code>  
   <code>GAP32</code>                      <code>50600</code>  <code>#50401 … #101000</code> 
   <code>CURRENT_OFFSET</code>             <code>  200</code>  <code>#50601 … #50800</code>  
   <code>CURRENT_OFFSET2</code>            <code>  200</code>  <code>#50801 … #51000</code>  
   <code>GAP32</code>                      <code>51300</code>  <code>#51001 … #102300</code> 
   <code>VPS_TEMPLATE_OFFSET</code>        <code>  100</code>  <code>#51301 … #51400</code>  
   <code>WORK_MATERIAL</code>              <code>  200</code>  <code>#51401 … #51600</code>  
   <code>VPS_FEEDRATE</code>               <code>  200</code>  <code>#51601 … #51800</code>  
   <code>APPROX_LENGTH</code>              <code>  200</code>  <code>#51801 … #52000</code>  
   <code>APPROX_DIAMETER</code>            <code>  200</code>  <code>#52001 … #52200</code>  
   <code>EDGE_MEASURE_HEIGHT</code>        <code>  200</code>  <code>#52201 … #52400</code>  
   <code>TOOL_TOLERANCE</code>             <code>  200</code>  <code>#52401 … #52600</code>  
   <code>PROBE_TYPE</code>                 <code>  200</code>  <code>#52601 … #52800</code>  



  ----------------------------------------------------------------------


16 Why
======

  Waiting for a replacement stylus *and* tool setter to arrive, I
  wondered if were possible to replace the hundreds of inscrutible lines
  of Hass WIPS Renishaw G-code with just a few lines of Python?

  %80 there.

  ----------------------------------------------------------------------
