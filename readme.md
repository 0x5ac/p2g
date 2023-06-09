---

![img](https://codecov.io/gh/0x5ac/p2g/branch/master/graph/badge.svg?token=FKR0R7P8U1) ![img](https://img.shields.io/badge/License-MIT%20v3-blue.svg) ![img](https://github.com/0x5ac/p2g/actions/workflows/build.yml/badge.svg)


### Version 0.2.29+14

---


# Introduction.

Many styli died to bring us this information.

This project makes it simpl(er) to ensure that parts are in fixtures correctly, coordinate systems are adjusted to deal with stock placement and cope with movement and rotation of workpieces through multiple operations.

P2G is a compiler; it takes Python code, some definitions of machine specific variables, a little glue and makes G-code, so far, Haas ideomatic.

Thanks to magic it can do surprising things with python data structures, anything reasonably calculated statically during compilation can be used in the source, classes, dicts, and so on.

It comes with a set of macro variable definitions for a Haas mill with NCD. And a few example settings for my own VF-3SSYT.

---


# Table of Contents

1.  [Introduction.](#org14a1a02)
2.  [Usage.](#orgfdaa18c)
3.  [Install:](#org1f12b64)
4.  [A taste.](#org2f6e420)
5.  [Variables](#org7fe3aee)
6.  [Coordinates.](#org9f7caf3)
7.  [Expressions](#orgc4b0dfc)
8.  [Axes](#org4a90fcb)
9.  [Goto.](#org92f8b71)
10. [Printing](#orgcfc46cc)
11. [Symbol Tables.](#org345d108)
12. [Notes.](#orga671e6d)
13. [HAAS macro var definitions](#org042ac60)
14. [Why:](#org7cc8055)

---


# Usage.

```
Turns a python program into a gcode program.

Usage:
   p2g [--function=<fname> ]
       [--job=<jobname>]
       [options] gen <srcfile> [<outfile>]
 
        Read from python <srcfile>, emit G-Code.
 
          Output file name may include {time} which will create a decrementing
          prefix for the output file which makes looking for the .nc in a
          crowded directory simpler.
 
        Examples:
           p2g gen foo.py ~/_nc_/{time}O001-foo.nc
              Makes an output of the form ~/_nc_/001234O001-foo.nc
 
           p2g gen --func=thisone -
              Read from stdin, look for the 'thisone' function and write to
              to stdout.
 
   p2g examples <exampledir>
          Create <exampledir>, populate with examples and compile.
 
          Examples:
            p2g examples showme
              Copies the examples into ./showme and then runs
               p2g gen showme/vicecenter.py
               p2g gen showme/checkprobe.py
 
   p2g doc
          Send readme.txt to console.
 
   p2g help
          Show complete command line help.
 
   p2g version
          Show version.
 
   p2g location
          Show which p2g is running.
 
       For maintenance:
     p2g [options] stdvars [--txt=<txt>] [--dev=<dev>]
                           [--py=<py>] [--org=<org>]
                Recreate internal files.

 Options:
  --narrow                    Narrow output; formatted to fit in the
                              narrow space of the CNC machine's program
                              display.
 
       For maintenance:
           --no-boiler-plate  Turn of job entry and terminal M30.
           --break            Breakpoint on error.
           --debug            Enter debugging code.
           --verbose          Too much.
           --logio            Even more.
```

---


# Install:

```
$ pip install p2g
```

for a show:

```
$ p2g examples dstdir
```

something smaller:

```
$ cat > tst.py <<EOF
```

```python
import p2g 
def t():
  x = p2g.Var(9)
  for y in range(10):
    x += y
#EOF
```

```
p2g gen tst.py
```

```
  O0001                           ( t                             )
  #100= 9.                        (   x = Var[9]                  )
  #102= 0.                        (   for y in range[10]:         )
N1000
  IF [#102 GE 10.] GOTO 1002
  #100= #100 + #102               ( x += y                        )
  #102= #102 + 1.
  GOTO 1000
N1002
  M30
```

---


# A taste.

```python
from p2g import *
from p2g.haas import *

fast_go = goto.feed(640)
fast_probe = goto.probe.feed(30)

class SearchParams:
    def __init__(self, name, search_depth, iota, delta):
	self.name = name
	self.its = 10
	self.search_depth = search_depth
	self.iota = iota
	self.delta = delta
	self.probe = goto.probe.feed(30)
	self.go = goto.feed(640)

def search(cursor, sch):
    # stick from class SearchParams  iterations into macro var
    its = Var(sch.its)
    while its > 0:
	# goto start point
	sch.go(cursor)
	# down until hit - or not.
	sch.probe(z=sch.search_depth)
	# if probe is below (+some slack) hit
	# point, then done.
	if SKIP_POS.z < sch.search_depth + sch.iota:
	    break
	# otherwise move to next point
	cursor.xy += sch.delta
	its -= 1
    else:
	message(ALARM, f"too far {sch.name}.")

def demo1():
    cursor = Var[3](2, 3, 41)
    # searching right, look down 0.4", move
    # 1.5" right if nothing hit.
    sch1 = SearchParams(name="right", search_depth=-0.4, iota=-0.1, delta=(1.5, 0))
    search(cursor, sch1)


```

⇨ `p2g gen demo1.py` ⇨

```
  O0001                           ( demo1                         )
  #100= 2.                        ( cursor = Var[3][2, 3, 41]     )
  #101= 3.
  #102= 41.
  #103= 10.                       ( its = Var[sch.its]            )
N1000                             ( while its > 0:                )
  IF [#103 LE 0.] GOTO 1002
  G01 G90 F640. x#100 y#101 z#102 (     sch.go[cursor]            )
  G01 G90 G31 F30. z-0.4          (     sch.probe[z=sch.search_depth])
  IF [#5063 LT -0.5] GOTO 1001    (     if SKIP_POS.z < sch.search_depth + sch.iota:)
  #100= #100 + 1.5                (     cursor.xy += sch.delta    )
  #103= #103 - 1.                 (     its -= 1                  )
  GOTO 1000
N1002
  (# 3000) = 101 (too far right.)
N1001                             (     message[ALARM, f"too far {sch.name}."])
  M30
```

---


# Variables

-   Give names to macro variables at a known address:
    
    `Fixed` ❰ `[` *size* `]` ❱<sub>opt</sub> (`addr=` *addr* ❰ `,` *init* &#x2026; ❱<sub>opt</sub> `)`

-   Give names to macro variables automatically per function.
    
    `Var` ❰ `[` *size* `]` ❱<sub>opt</sub> (❰ `,` *init* &#x2026; ❱<sub>opt</sub> `)`

-   Not actually a variable, but same syntax.
    
    `Const` ❰ `[` *size* `]` ❱<sub>opt</sub> (❰ `,` *init* &#x2026; ❱<sub>opt</sub> `)`

Example:

```python

from p2g import *   # this is the common header
from p2g.haas import *

def ex2():
    # On my machine, Renishaw skip positions are
    # in 5061, 5062, 5063.  Look in p2g.haas.py
    # for : SKIP_POS = p2g.Fixed[20](addr=5061)    
    skip0 = SKIP_POS

    # can be done manualy too.
    skip1 = Fixed[3](addr=5061)

    # grab 5041.. from globals oto.
    workpos = WORK_POS


    tmp0 = Var( skip0.xyz * 2.0 + workpos + skip1)


    com("Define a constant ")
    above_tdc = Const (111,222,1333)

    com("Use it ")
    tmp0 += above_tdc

```

⇨ `p2g gen var1.py` ⇨

```
  O0001                           ( ex2                           )
  #100= #5061 * 2. + #5041 + #5061( tmp0 = Var[ skip0.xyz * 2.0 + workpos + skip1])
  #101= #5062 * 2. + #5042 + #5062
  #102= #5063 * 2. + #5043 + #5063
( Define a constant  )
( Use it  )
  #100= #100 + 111.               ( tmp0 += above_tdc             )
  #101= #101 + 222.
  #102= #102 + 1333.
  M30
```

---


# Coordinates.

Describe position, with axis by location, in sequence or by name.

```python
from p2g import *       # this is the common header
from p2g.haas import *  # to all the examples

def co1():
    com ("Describe 3 variables at 3000")    
    dst = Fixed[3](addr=3000)
    com ("Fill with 1,2,3")
    dst.var = (1,2,3)


    com ("Set by parts")
    dst.y = 7
    dst.z = 71
    dst.x = 19

    offset = Const(0.101,0.102,0.103)
    com ("Arithmetic")
    dst.var += (1,2,3)
    dst.var -= offset
    dst.var %= sin(asin(offset) + 7)

    com ("When describing a location:")
    com ("Coords by order.")
    p1 = Fixed[3](1, 2, 3, addr=100)

    com ("Coords by axis name.")
    p2 = Fixed[3](z=333, y=222, x=111, addr=200)
    p2.x = 17

    com ("Coords by index.")      
    p1.xyz = p2[2]
    p2[1:3] = 7

    com ("Mix them up.")
    p1.yz = p2.yz[1]


```

⇨ `p2g gen co1.py` ⇨

```
  O0001                           ( co1                           )
( Describe 3 variables at 3000 )
( Fill with 1,2,3 )
  #3000= 1.                       ( dst.var = [1,2,3]             )
  #3001= 2.
  #3002= 3.
( Set by parts )
  #3001= 7.                       ( dst.y = 7                     )
  #3002= 71.                      ( dst.z = 71                    )
  #3000= 19.                      ( dst.x = 19                    )
( Arithmetic )
  #3000= #3000 + 1.               ( dst.var += [1,2,3]            )
  #3001= #3001 + 2.
  #3002= #3002 + 3.
  #3000= #3000 - 0.101            ( dst.var -= offset             )
  #3001= #3001 - 0.102
  #3002= #3002 - 0.103
  #3000= #3000 MOD 0.2215         ( dst.var %= sin[asin[offset] + 7])
  #3001= #3001 MOD 0.2225
  #3002= #3002 MOD 0.2235
( When describing a location: )
( Coords by order. )
  #100= 1.                        ( p1 = Fixed[3][1, 2, 3, addr=100])
  #101= 2.
  #102= 3.
( Coords by axis name. )
  #200= 111.                      ( p2 = Fixed[3][z=333, y=222, x=111, addr=200])
  #201= 222.
  #202= 333.
  #200= 17.                       ( p2.x = 17                     )
( Coords by index. )
  #100= #202                      ( p1.xyz = p2[2]                )
  #101= #202
  #102= #202
  #201= 7.                        ( p2[1:3] = 7                   )
  #202= 7.
( Mix them up. )
  #101= #202                      ( p1.yz = p2.yz[1]              )
  #102= #202
  M30
```

---


# Expressions

Python expressions turn into G-Code as you may expect, save that native Python uses radians for trig, and G-Code uses degrees, so folding is done in degrees.

```python
from p2g import *       # this is the common header
from p2g.haas import *  # to all the examples

def exp11():
    com ("Variables go into macro variables.")
    theta = Var(0.3)
    angle = Var(sin(theta))

    com ("Constants don't exist in G-code.")
    thetak = Const(0.3)
    anglek = Var(sin(thetak))

    com ("Lots of things are folded.")
    t1 = Var(2 * thetak  + 7)

    com ("Simple array math:")

    box_size = Const([ 4,4,2 ])
    tlhc = Var( - box_size / 2)
    brhc = Var(box_size / 2)
    diff = Var(tlhc - brhc)


    a,b,x = Var(),Var(),Var()
    a = tlhc[0] / tlhc[1]
    b = tlhc[0] % tlhc[1]
    x = tlhc[0] & tlhc[1]        
    tlhc.xy = ((a - b + 3) / sin(x),
	       (a + b + 3) / cos(x))




```

⇨ `p2g gen exp1.py` ⇨

```
  O0001                           ( exp11                         )
( Variables go into macro variables. )
  #100= 0.3                       ( theta = Var[0.3]              )
  #101= SIN[#100]                 ( angle = Var[sin[theta]]       )
( Constants don't exist in G-code. )
  #102= 0.0052                    ( anglek = Var[sin[thetak]]     )
( Lots of things are folded. )
  #103= 7.6                       ( t1 = Var[2 * thetak  + 7]     )
( Simple array math: )
  #104= -2.                       ( tlhc = Var[ - box_size / 2]   )
  #105= -2.
  #106= -1.
  #107= 2.                        ( brhc = Var[box_size / 2]      )
  #108= 2.
  #109= 1.
  #110= #104 - #107               ( diff = Var[tlhc - brhc]       )
  #111= #105 - #108
  #112= #106 - #109
  #113= #104 / #105               ( a = tlhc[0] / tlhc[1]         )
  #114= #104 MOD #105             ( b = tlhc[0] % tlhc[1]         )
  #115= #104 AND #105             ( x = tlhc[0] & tlhc[1]         )
( tlhc.xy = [[a - b + 3] / sin[x],)
  #104= [#113 - #114 + 3.] / SIN[#115]
  #105= [#113 + #114 + 3.] / COS[#115]
  M30
```

---


# Axes

Any number of axes are supported, default just being xy and z.

A rotary on ac can be set with p2g.axis.NAMES="xyza\*c". The axis letters should be the same order as your machine expects coordinates to turn up in work offset registers.

```python

from p2g import *
from p2g.haas import *

def a5():
   p2g.axis.NAMES = 'xyza*c'
   p2g.com ("rhs of vector ops get expanded as needed")
   G55.var = [0,1]
   p2g.com ("fill yz and c with some stuff")
   tmp1 = Const(y=3, z=9, c=p2g.asin(.5))
   p2g.com ("Unmentioned axes values are assumed",
	    "to be 0, so adding them makes no code.")
   G55.var += tmp1
   p2g.com ("")
   G55.ac *= 2.0

   com ("Rotaries.")
   p4 = Fixed[6]()
   p4.a = 180
   p4.c = asin (0.5)



def a3():
   # xyz is the default.
   # but overridden because a5 called first, so
   p2g.axis.NAMES = 'xyz'
   p2g.com ("Filling to number of axes.")
   G55.var = [0]
   tmp = p2g.Var(G55 * 34)


def axes():
   a5()
   a3()   
```

⇨ `p2g gen axes.py` ⇨

```
  O0001                           ( axes                          )
( rhs of vector ops get expanded as needed )
  #5241= 0.                       (    G55.var = [0,1]            )
  #5242= 1.
  #5243= 0.
  #5244= 1.
  #5245= 0.
  #5246= 1.
( fill yz and c with some stuff )
( Unmentioned axes values are assumed    )
( to be 0, so adding them makes no code. )
  #5242= #5242 + 3.               (    G55.var += tmp1            )
  #5243= #5243 + 9.
  #5246= #5246 + 30.

  #5244= #5244 * 2.               (    G55.ac *= 2.0              )
  #5246= #5246 * 2.
( Rotaries. )
  #103= 180.                      (    p4.a = 180                 )
  #105= 30.                       (    p4.c = asin [0.5]          )
( Filling to number of axes. )
  #5241= 0.                       (    G55.var = [0]              )
  #5242= 0.
  #5243= 0.
  #106= #5241 * 34.               (    tmp = Var[G55 * 34]        )
  #107= #5242 * 34.
  #108= #5243 * 34.
  M30
```

---


# Goto.

Goto functions are constructed from parts, and make building blocks when partially applied.

`goto` ❰ `.` *modifier* ❱\* `(` *coordinates* `)`

*modifier* :

-   `r9810` Use Renishaw macro 9810 to do a protected positioning cycle.
-   `work` Use current work coordinate system. - whatever set with set\_wcs
-   `machine` Use the machine coordinate system - G53
-   `relative` Use relative coordinate system - G91
-   `absolute` Use absolute coordinate system - G90
-   `z_then_xy` move Z axis first.
-   `xy_then_z` move the other axes before the Z.
-   `probe` Emit probe code using G31.
-   `xyz` Move all axes at once.
-   `feed(` *expr* `)` Set feed rate.
-   `mcode(` *string* `)` Apply an mcode.

```python
from p2g import *

def goto1():
    symbol.Table.print = True
    g1 = goto.work.feed (20)

    comment ("in work cosys, goto x=1, y=2, z=3 at 20ips")
    g1 (1,2,3)

    comment ("make a variable, 2,3,4")
    v1 = Var(x=2,y=3,z=4)        

    absslow = goto.machine.feed(10)

    comment ("In the machine cosys, move to v1.z then v1.xy, slowly")

    absslow.z_then_xy(v1)

    comment ("p1 is whatever absslow was, with feed adjusted to 100.")
    p1 = absslow.feed(100)
    p1.xy_then_z(v1)

    comment ("p2 is whatever p1 was, with changed to a probe.")
    p2 = p1.probe
    p2.xy_then_z(v1)

    comment ("p3 is whatever p1 was, with a probe and relative,",
	     "using only the x and y axes")
    p3 = p1.relative.probe
    p3.xy_then_z(v1.xy)

    comment ("move a and c axes ")
    axis.NAMES = 'xyza*c'
    goto.feed(20) (a=9, c= 90)


    comment ("probe with a hass MUST_SKIP mcode.")
    goto.probe.feed(10).mcode("M79")(3,4,5)


    comment ("Define shortcut for safe_goto and use.")
    safe_goto = goto.feed(20).r9810

    safe_goto.z_then_xy(1,2,3)
```

⇨ \`p2g gen goto1.py\` ⇨

```
( v1        :  #100.x  #101.y  #102.z )
( absslow   : 10 machine xyz          )
( g1        : 20 work xyz             )
( p1        : 100 machine xyz         )
( p2        : 100 machine xyz probe   )
( safe_goto : 20 r9810 xyz            )
  O0001                           ( goto1                         )

( in work cosys, goto x=1, y=2, z=3 at 20ips )
  G01 G90 F20. x1. y2. z3.        ( g1 [1,2,3]                    )

( make a variable, 2,3,4 )
  #100= 2.                        ( v1 = Var[x=2,y=3,z=4]         )
  #101= 3.
  #102= 4.

( In the machine cosys, move to v1.z then v1.xy, slowly )
  G01 G53 G90 F10. z#102          ( absslow.z_then_xy[v1]         )
  G01 G53 G90 F10. x#100 y#101

( p1 is whatever absslow was, with feed adjusted to 100. )
  G01 G53 G90 F100. x#100 y#101   ( p1.xy_then_z[v1]              )
  G01 G53 G90 F100. z#102

( p2 is whatever p1 was, with changed to a probe. )
( p2.xy_then_z[v1]              )
  G01 G53 G90 G31 F100. x#100 y#101
  G01 G53 G90 G31 F100. z#102

( p3 is whatever p1 was, with a probe and relative, )
( using only the x and y axes                       )
( p3.xy_then_z[v1.xy]           )
  G01 G53 G91 G31 F100. x#100 y#101

( move a and c axes  )
  G01 G90 F20. a9. c90.           ( goto.feed[20] [a=9, c= 90]    )

( probe with a hass MUST_SKIP mcode. )
  G01 G90 G31 M79 F10. x3. y4. z5.( goto.probe.feed[10].mcode["M79"][3,4,5])

( Define shortcut for safe_goto and use. )
  G65 R9810 F20. z3.              ( safe_goto.z_then_xy[1,2,3]    )
  G65 R9810 F20. x1. y2.
  M30
```

---


# Printing

Turns Python f string prints into G-code DPRNT. Make sure that your print string does not have any characters in it that your machine considers to be illegal in a DPRNT string.

```python
from p2g import *
from p2g.haas import *

def exprnt():
  x = Var(2)
  y = Var(27)  

  for q in range(10):
    dprint(f"X is {x:3.1f}, Y+Q is {y+q:5.2f}")


```

⇨ `p2g gen exprnt.py` ⇨

```
  O0001                           ( exprnt                        )
  #100= 2.                        (   x = Var[2]                  )
  #101= 27.                       (   y = Var[27]                 )
  #103= 0.                        (   for q in range[10]:         )
N2000
  IF [#103 GE 10.] GOTO 2002
DPRNT[X*is*[#100][31],*Y+Q*is*[#101+#103][52]]
  #103= #103 + 1.                 ( dprint[f"X is {x:3.1f}, Y+Q is {y+q:5.2f}"])
  GOTO 2000
N2002
  M30
```

---


# Symbol Tables.

Set the global `p2g.symbol.Table.print` to get a symbol table in the output file.

```python
import p2g
x1 = -7
MACHINE_ABS_ABOVE_OTS = p2g.Const(x=x1, y=8, z=9)
MACHINE_ABS_ABOVE_SEARCH_ROTARY_LHS_5X8 = p2g.Const(100, 101, 102)
MACHINE_ABS_ABOVE_VICE = p2g.Const(x=17, y=18, z=19)
RAW_ANALOG = p2g.Fixed[10](addr=1080)
fish = 10
not_used = 12

def stest():
    p2g.symbol.Table.print = True    
    p2g.comment("Only used symbols are in output table.")
    p2g.Var(MACHINE_ABS_ABOVE_OTS)
    p2g.Var(MACHINE_ABS_ABOVE_VICE * fish)
    v1 = p2g.Var()
    v1 += RAW_ANALOG[7]
```

⇨ \`p2g gen stest.py\` ⇨

```
( RAW_ANALOG                              : #1080[10]               )
( v1                                      :  #106.x                 )
( MACHINE_ABS_ABOVE_OTS                   :  -7.000,  8.000,  9.000 )
( MACHINE_ABS_ABOVE_SEARCH_ROTARY_LHS_5X8 : 100.000,101.000,102.000 )
( MACHINE_ABS_ABOVE_VICE                  :  17.000, 18.000, 19.000 )
  O0001                           ( stest                         )

( Only used symbols are in output table. )
  #100= -7.                       ( Var[MACHINE_ABS_ABOVE_OTS]    )
  #101= 8.
  #102= 9.
  #103= 170.                      ( Var[MACHINE_ABS_ABOVE_VICE * fish])
  #104= 180.
  #105= 190.
  #106= #106 + #1087              ( v1 += RAW_ANALOG[7]           )
  M30
```

---


# Notes.

The entire thing is brittle; I've only used it to make code for my own limited purposes.

Nice things:

```python

from p2g import *
from p2g.haas import *

class X():
	 def __init__(self, a,b):
	       self.thisone = a
	       self.b = b
	 def adjust(self, tof):
	       self.thisone += tof.x
	       self.b += tof.y

class Y():
	 def __init__(self, a):
	       self.val = a
	 def adjust(self, tof):
	       self.val += tof
	 # an example of overloading.
	 # I'm not recommending replacing
	 # add with multiply, but it would work.
	 def __add__(self, other):
	       return self.val * other + 3

def cool():
      com ("You can do surprising things.")

      avariable = Var(100)
      objp = X(avariable,34)
      another = Var(7,8)

      objp.adjust(TOOL_OFFSET)

      q = Y(another) + (objp.thisone,objp.b)
      dprint(f"{q[0]}{q[1]}")

```

      O0001                           ( cool                          )
    ( You can do surprising things. )
      #100= 100.                      (   avariable = Var[100]        )
      #101= 7.                        (   another = Var[7,8]          )
      #102= 8.
    DPRNT[[#101*[#100+#5081]+3.][#102*[#5082+34.]+3.]]
      M30

```python
from p2g import *
from p2g.haas import *

G55 = p2g.Fixed[3](addr=5241)

def beware():
    com(
	"Names on the left hand side of an assignment need to be",
	"treated with care.  A simple.",
    )
    G55 = [0, 0, 0]
    com(
	"Will not do what you want - this will overwrite the definition",
	"of G55 above - so no code will be generated.",
    )

    com(
	"You need to use .var (for everything), explicitly name the axes,"
	"or use magic slicing."
    )

    G56.var = [1, 1, 1]
    G56.xyz = [2, 2, 2]
    G56[:] = [3, 3, 3]



```

```
  O0001                           ( beware                        )
( Names on the left hand side of an assignment need to be )
( treated with care.  A simple.                           )
( Will not do what you want - this will overwrite the definition )
( of G55 above - so no code will be generated.                   )
( You need to use .var [for everything], explicitly name the axes,or use magic slicing. )
  #5261= 1.                       ( G56.var = [1, 1, 1]           )
  #5262= 1.
  #5263= 1.
  #5261= 2.                       ( G56.xyz = [2, 2, 2]           )
  #5262= 2.
  #5263= 2.
  #5261= 3.                       ( G56[:] = [3, 3, 3]            )
  #5262= 3.
  #5263= 3.
  M30
```

```python
from p2g import *
from p2g.haas import *
def beware1():
   com ("It's easy to forget that only macro variables will get into",
      "the output code. Other code will go away.")
   x = 123  # not a var
   y = Var(7)
   if x==23 :  # look here
     y = 9

   com ("Should look like:")
   x = Var(123)  # is a var
   y = Var(7)
   if x==23 :  # look here
     y = 9
   else:
     y = 99

```

```
  O0001                           ( beware1                       )
( It's easy to forget that only macro variables will get into )
( the output code. Other code will go away.                   )
  #100= 7.                        (    y = Var[7]                 )
( Should look like: )
  #101= 123.                      (    x = Var[123]  # is a var   )
  #102= 7.                        (    y = Var[7]                 )
  #100= #102
  IF [#101 NE 23.] GOTO 1002      (    if x==23 :  # look here    )
  #100= 9.                        (  y = 9                        )
  GOTO 1003
N1002
  #100= 99.                       (  y = 99                       )
N1003
  M30
```

---


# HAAS macro var definitions

Names predefined in p2g.haas:

| <code>Name</code>                          | <code>Size</code>  | <code>Address</code>         |
| ---                                        | ---                | ---                          |
| <code>NULL</code>                          | <code>    1</code> | <code>     #    0    </code> |
| <code>MACRO\_ARGUMENTS</code>              | <code>   33</code> | <code>#    1 … #   33</code> |
| <code>GP\_SAVED1</code>                    | <code>  100</code> | <code>#  100 … #  199</code> |
| <code>GP\_SAVED2</code>                    | <code>   50</code> | <code>#  500 … #  549</code> |
| <code>PROBE\_CALIBRATION1</code>           | <code>    6</code> | <code>#  550 … #  555</code> |
| <code>PROBE\_R</code>                      | <code>    3</code> | <code>#  556 … #  558</code> |
| <code>PROBE\_CALIBRATION2</code>           | <code>   22</code> | <code>#  559 … #  580</code> |
| <code>GP\_SAVED3</code>                    | <code>  119</code> | <code>#  581 … #  699</code> |
| <code>GP\_SAVED4</code>                    | <code>  200</code> | <code>#  800 … #  999</code> |
| <code>INPUTS</code>                        | <code>   64</code> | <code># 1000 … # 1063</code> |
| <code>MAX\_LOADS\_XYZAB</code>             | <code>    5</code> | <code># 1064 … # 1068</code> |
| <code>RAW\_ANALOG</code>                   | <code>   10</code> | <code># 1080 … # 1089</code> |
| <code>FILTERED\_ANALOG</code>              | <code>    8</code> | <code># 1090 … # 1097</code> |
| <code>SPINDLE\_LOAD</code>                 | <code>    1</code> | <code>     # 1098    </code> |
| <code>MAX\_LOADS\_CTUVW</code>             | <code>    5</code> | <code># 1264 … # 1268</code> |
| <code>TOOL\_TBL\_FLUTES</code>             | <code>  200</code> | <code># 1601 … # 1800</code> |
| <code>TOOL\_TBL\_VIBRATION</code>          | <code>  200</code> | <code># 1801 … # 2000</code> |
| <code>TOOL\_TBL\_OFFSETS</code>            | <code>  200</code> | <code># 2001 … # 2200</code> |
| <code>TOOL\_TBL\_WEAR</code>               | <code>  200</code> | <code># 2201 … # 2400</code> |
| <code>TOOL\_TBL\_DROFFSET</code>           | <code>  200</code> | <code># 2401 … # 2600</code> |
| <code>TOOL\_TBL\_DRWEAR</code>             | <code>  200</code> | <code># 2601 … # 2800</code> |
| <code>ALARM</code>                         | <code>    1</code> | <code>     # 3000    </code> |
| <code>T\_MS</code>                         | <code>    1</code> | <code>     # 3001    </code> |
| <code>T\_HR</code>                         | <code>    1</code> | <code>     # 3002    </code> |
| <code>SINGLE\_BLOCK\_OFF</code>            | <code>    1</code> | <code>     # 3003    </code> |
| <code>FEED\_HOLD\_OFF</code>               | <code>    1</code> | <code>     # 3004    </code> |
| <code>MESSAGE</code>                       | <code>    1</code> | <code>     # 3006    </code> |
| <code>YEAR\_MONTH\_DAY</code>              | <code>    1</code> | <code>     # 3011    </code> |
| <code>HOUR\_MINUTE\_SECOND</code>          | <code>    1</code> | <code>     # 3012    </code> |
| <code>POWER\_ON\_TIME</code>               | <code>    1</code> | <code>     # 3020    </code> |
| <code>CYCLE\_START\_TIME</code>            | <code>    1</code> | <code>     # 3021    </code> |
| <code>FEED\_TIMER</code>                   | <code>    1</code> | <code>     # 3022    </code> |
| <code>CUR\_PART\_TIMER</code>              | <code>    1</code> | <code>     # 3023    </code> |
| <code>LAST\_COMPLETE\_PART\_TIMER</code>   | <code>    1</code> | <code>     # 3024    </code> |
| <code>LAST\_PART\_TIMER</code>             | <code>    1</code> | <code>     # 3025    </code> |
| <code>TOOL\_IN\_SPIDLE</code>              | <code>    1</code> | <code>     # 3026    </code> |
| <code>SPINDLE\_RPM</code>                  | <code>    1</code> | <code>     # 3027    </code> |
| <code>PALLET\_LOADED</code>                | <code>    1</code> | <code>     # 3028    </code> |
| <code>SINGLE\_BLOCK</code>                 | <code>    1</code> | <code>     # 3030    </code> |
| <code>AGAP</code>                          | <code>    1</code> | <code>     # 3031    </code> |
| <code>BLOCK\_DELETE</code>                 | <code>    1</code> | <code>     # 3032    </code> |
| <code>OPT\_STOP</code>                     | <code>    1</code> | <code>     # 3033    </code> |
| <code>TIMER\_CELL\_SAFE</code>             | <code>    1</code> | <code>     # 3196    </code> |
| <code>TOOL\_TBL\_DIAMETER</code>           | <code>  200</code> | <code># 3201 … # 3400</code> |
| <code>TOOL\_TBL\_COOLANT\_POSITION</code>  | <code>  200</code> | <code># 3401 … # 3600</code> |
| <code>M30\_COUNT1</code>                   | <code>    1</code> | <code>     # 3901    </code> |
| <code>M30\_COUNT2</code>                   | <code>    1</code> | <code>     # 3902    </code> |
| <code>LAST\_BLOCK\_G</code>                | <code>   21</code> | <code># 4001 … # 4021</code> |
| <code>LAST\_BLOCK\_ADDRESS</code>          | <code>   26</code> | <code># 4101 … # 4126</code> |
| <code>LAST\_TARGET\_POS</code>             | <code>naxes</code> | <code>    # 5001…    </code> |
| <code>MACHINE\_POS</code>                  | <code>naxes</code> | <code>    # 5021…    </code> |
| <code>MACHINE</code>                       | <code>naxes</code> | <code>    # 5021…    </code> |
| <code>G53</code>                           | <code>naxes</code> | <code>    # 5021…    </code> |
| <code>WORK\_POS</code>                     | <code>naxes</code> | <code>    # 5041…    </code> |
| <code>WORK</code>                          | <code>naxes</code> | <code>    # 5041…    </code> |
| <code>SKIP\_POS</code>                     | <code>naxes</code> | <code>    # 5061…    </code> |
| <code>PROBE</code>                         | <code>naxes</code> | <code>    # 5061…    </code> |
| <code>TOOL\_OFFSET</code>                  | <code>   20</code> | <code># 5081 … # 5100</code> |
| <code>G52</code>                           | <code>naxes</code> | <code>    # 5201…    </code> |
| <code>G54</code>                           | <code>naxes</code> | <code>    # 5221…    </code> |
| <code>G55</code>                           | <code>naxes</code> | <code>    # 5241…    </code> |
| <code>G56</code>                           | <code>naxes</code> | <code>    # 5261…    </code> |
| <code>G57</code>                           | <code>naxes</code> | <code>    # 5281…    </code> |
| <code>G58</code>                           | <code>naxes</code> | <code>    # 5301…    </code> |
| <code>G59</code>                           | <code>naxes</code> | <code>    # 5321…    </code> |
| <code>TOOL\_TBL\_FEED\_TIMERS</code>       | <code>  100</code> | <code># 5401 … # 5500</code> |
| <code>TOOL\_TBL\_TOTAL\_TIMERS</code>      | <code>  100</code> | <code># 5501 … # 5600</code> |
| <code>TOOL\_TBL\_LIFE\_LIMITS</code>       | <code>  100</code> | <code># 5601 … # 5700</code> |
| <code>TOOL\_TBL\_LIFE\_COUNTERS</code>     | <code>  100</code> | <code># 5701 … # 5800</code> |
| <code>TOOL\_TBL\_LIFE\_MAX\_LOADS</code>   | <code>  100</code> | <code># 5801 … # 5900</code> |
| <code>TOOL\_TBL\_LIFE\_LOAD\_LIMITS</code> | <code>  100</code> | <code># 5901 … # 6000</code> |
| <code>NGC\_CF</code>                       | <code>    1</code> | <code>     # 6198    </code> |
| <code>G154\_P1</code>                      | <code>naxes</code> | <code>    # 7001…    </code> |
| <code>G154\_P2</code>                      | <code>naxes</code> | <code>    # 7021…    </code> |
| <code>G154\_P3</code>                      | <code>naxes</code> | <code>    # 7041…    </code> |
| <code>G154\_P4</code>                      | <code>naxes</code> | <code>    # 7061…    </code> |
| <code>G154\_P5</code>                      | <code>naxes</code> | <code>    # 7081…    </code> |
| <code>G154\_P6</code>                      | <code>naxes</code> | <code>    # 7101…    </code> |
| <code>G154\_P7</code>                      | <code>naxes</code> | <code>    # 7121…    </code> |
| <code>G154\_P8</code>                      | <code>naxes</code> | <code>    # 7141…    </code> |
| <code>G154\_P9</code>                      | <code>naxes</code> | <code>    # 7161…    </code> |
| <code>G154\_P10</code>                     | <code>naxes</code> | <code>    # 7181…    </code> |
| <code>G154\_P11</code>                     | <code>naxes</code> | <code>    # 7201…    </code> |
| <code>G154\_P12</code>                     | <code>naxes</code> | <code>    # 7221…    </code> |
| <code>G154\_P13</code>                     | <code>naxes</code> | <code>    # 7241…    </code> |
| <code>G154\_P14</code>                     | <code>naxes</code> | <code>    # 7261…    </code> |
| <code>G154\_P15</code>                     | <code>naxes</code> | <code>    # 7281…    </code> |
| <code>G154\_P16</code>                     | <code>naxes</code> | <code>    # 7301…    </code> |
| <code>G154\_P17</code>                     | <code>naxes</code> | <code>    # 7321…    </code> |
| <code>G154\_P18</code>                     | <code>naxes</code> | <code>    # 7341…    </code> |
| <code>G154\_P19</code>                     | <code>naxes</code> | <code>    # 7361…    </code> |
| <code>G154\_P20</code>                     | <code>naxes</code> | <code>    # 7381…    </code> |
| <code>PALLET\_PRIORITY</code>              | <code>  100</code> | <code># 7501 … # 7600</code> |
| <code>PALLET\_STATUS</code>                | <code>  100</code> | <code># 7601 … # 7700</code> |
| <code>PALLET\_PROGRAM</code>               | <code>  100</code> | <code># 7701 … # 7800</code> |
| <code>PALLET\_USAGE</code>                 | <code>  100</code> | <code># 7801 … # 7900</code> |
| <code>ATM\_ID</code>                       | <code>    1</code> | <code>     # 8500    </code> |
| <code>ATM\_PERCENT</code>                  | <code>    1</code> | <code>     # 8501    </code> |
| <code>ATM\_TOTAL\_AVL\_USAGE</code>        | <code>    1</code> | <code>     # 8502    </code> |
| <code>ATM\_TOTAL\_AVL\_HOLE\_COUNT</code>  | <code>    1</code> | <code>     # 8503    </code> |
| <code>ATM\_TOTAL\_AVL\_FEED\_TIME</code>   | <code>    1</code> | <code>     # 8504    </code> |
| <code>ATM\_TOTAL\_AVL\_TOTAL\_TIME</code>  | <code>    1</code> | <code>     # 8505    </code> |
| <code>ATM\_NEXT\_TOOL\_NUMBER</code>       | <code>    1</code> | <code>     # 8510    </code> |
| <code>ATM\_NEXT\_TOOL\_LIFE</code>         | <code>    1</code> | <code>     # 8511    </code> |
| <code>ATM\_NEXT\_TOOL\_AVL\_USAGE</code>   | <code>    1</code> | <code>     # 8512    </code> |
| <code>ATM\_NEXT\_TOOL\_HOLE\_COUNT</code>  | <code>    1</code> | <code>     # 8513    </code> |
| <code>ATM\_NEXT\_TOOL\_FEED\_TIME</code>   | <code>    1</code> | <code>     # 8514    </code> |
| <code>ATM\_NEXT\_TOOL\_TOTAL\_TIME</code>  | <code>    1</code> | <code>     # 8515    </code> |
| <code>TOOL\_ID</code>                      | <code>    1</code> | <code>     # 8550    </code> |
| <code>TOOL\_FLUTES</code>                  | <code>    1</code> | <code>     # 8551    </code> |
| <code>TOOL\_MAX\_VIBRATION</code>          | <code>    1</code> | <code>     # 8552    </code> |
| <code>TOOL\_LENGTH\_OFFSETS</code>         | <code>    1</code> | <code>     # 8553    </code> |
| <code>TOOL\_LENGTH\_WEAR</code>            | <code>    1</code> | <code>     # 8554    </code> |
| <code>TOOL\_DIAMETER\_OFFSETS</code>       | <code>    1</code> | <code>     # 8555    </code> |
| <code>TOOL\_DIAMETER\_WEAR</code>          | <code>    1</code> | <code>     # 8556    </code> |
| <code>TOOL\_ACTUAL\_DIAMETER</code>        | <code>    1</code> | <code>     # 8557    </code> |
| <code>TOOL\_COOLANT\_POSITION</code>       | <code>    1</code> | <code>     # 8558    </code> |
| <code>TOOL\_FEED\_TIMER</code>             | <code>    1</code> | <code>     # 8559    </code> |
| <code>TOOL\_TOTAL\_TIMER</code>            | <code>    1</code> | <code>     # 8560    </code> |
| <code>TOOL\_LIFE\_LIMIT</code>             | <code>    1</code> | <code>     # 8561    </code> |
| <code>TOOL\_LIFE\_COUNTER</code>           | <code>    1</code> | <code>     # 8562    </code> |
| <code>TOOL\_LIFE\_MAX\_LOAD</code>         | <code>    1</code> | <code>     # 8563    </code> |
| <code>TOOL\_LIFE\_LOAD\_LIMIT</code>       | <code>    1</code> | <code>     # 8564    </code> |
| <code>THERMAL\_COMP\_ACC</code>            | <code>    1</code> | <code>     # 9000    </code> |
| <code>THERMAL\_SPINDLE\_COMP\_ACC</code>   | <code>    1</code> | <code>     # 9016    </code> |
| <code>GVARIABLES3</code>                   | <code> 1000</code> | <code>#10000 … #10999</code> |
| <code>INPUTS1</code>                       | <code>  256</code> | <code>#11000 … #11255</code> |
| <code>OUTPUT1</code>                       | <code>  256</code> | <code>#12000 … #12255</code> |
| <code>FILTERED\_ANALOG1</code>             | <code>   13</code> | <code>#13000 … #13012</code> |
| <code>COOLANT\_LEVEL</code>                | <code>    1</code> | <code>     #13013    </code> |
| <code>FILTERED\_ANALOG2</code>             | <code>   50</code> | <code>#13014 … #13063</code> |
| <code>SETTING</code>                       | <code>10000</code> | <code>#20000 … #29999</code> |
| <code>PARAMETER</code>                     | <code>10000</code> | <code>#30000 … #39999</code> |
| <code>TOOL\_TYP</code>                     | <code>  200</code> | <code>#50001 … #50200</code> |
| <code>TOOL\_MATERIAL</code>                | <code>  200</code> | <code>#50201 … #50400</code> |
| <code>CURRENT\_OFFSET</code>               | <code>  200</code> | <code>#50601 … #50800</code> |
| <code>CURRENT\_OFFSET2</code>              | <code>  200</code> | <code>#50801 … #51000</code> |
| <code>VPS\_TEMPLATE\_OFFSET</code>         | <code>  100</code> | <code>#51301 … #51400</code> |
| <code>WORK\_MATERIAL</code>                | <code>  200</code> | <code>#51401 … #51600</code> |
| <code>VPS\_FEEDRATE</code>                 | <code>  200</code> | <code>#51601 … #51800</code> |
| <code>APPROX\_LENGTH</code>                | <code>  200</code> | <code>#51801 … #52000</code> |
| <code>APPROX\_DIAMETER</code>              | <code>  200</code> | <code>#52001 … #52200</code> |
| <code>EDGE\_MEASURE\_HEIGHT</code>         | <code>  200</code> | <code>#52201 … #52400</code> |
| <code>TOOL\_TOLERANCE</code>               | <code>  200</code> | <code>#52401 … #52600</code> |
| <code>PROBE\_TYPE</code>                   | <code>  200</code> | <code>#52601 … #52800</code> |

---


# Why:

Waiting for a replacement stylus **and** tool setter to arrive, I wondered if were possible to replace the hundreds of inscrutible lines of Hass WIPS Renishaw G-code with just a few lines of Python?

Maybe.

---