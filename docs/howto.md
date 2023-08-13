<img src="/docs/pytest.svg" alt=""><img src="/docs/mit.svg" alt=""><img src="/docs/coverage.svg" alt="">


# Introduction


## Version 0.3.10

P2G makes it simple to ensure that parts are in fixtures correctly, coordinate systems are adjusted to deal with stock placement and cope with movement and rotation of workpieces through multiple operations.

P2G is a compiler; it takes Python code, some definitions of machine specific variables, a little glue and makes G-code, so far, Haas ideomatic.

Thanks to magic it can do surprising things with python data structures, anything reasonably calculated statically during compilation can be used in the source, classes, dicts, and so on.

It comes with a set of macro variable definitions for a Haas mill with NCD. And a few example settings for my own VF-3SSYT.


# Table of Contents

1.  [Introduction](#introduction)
2.  [Install](#install)
3.  [Usage](#usage)
4.  [Demo.](#vdemo)
5.  [Examples](#examples)
6.  [Variables](#variables)
7.  [Coordinates](#coordinates)
8.  [Goto](#goto)
9.  [Axes](#axes)
10. [When](#when)
11. [DPRNT](#dprnt)
12. [Symbol Tables](#symboltables)
13. [Notes](#notes)
14. [MIT License](#mit)
15. [Authors](#authors)
16. [Thanks](#thanks)
17. [Haas macro variables](#haas)


# Install


## From pypi

```

$ pip install p2g

```


## From github


### fetch dependencies, rebuild and install with pip

```
$ git clone https://github.com/0x5ac/attempt1 p2g
$ cd p2g
$ make install
```


### fetch dependencies and rebuild

```
$ git clone https://github.com/0x5ac/attempt1 p2g
$ cd p2g
$ make
```


# Usage

```python

```

```
p2g - Turn Python into G-Code.

Usage:
  p2g [options]  <srcfile> [<dstfile>]
  p2g help [ all | topics | maint | version | location | <topic> ]
  p2g examples <dstdir>

   For bare p2g:
       p2g tram-rotary.py ~/_nc_/O{countdown}tr.nc
        Makes an output of the form ~/_nc_/O1234tr.nc

       p2g --func=thisone -
        Read from stdin, look for the 'thisone' function and write to
        to stdout.


Arguments:
  <srcfile>   Source python file. [default: stdin]
  <dstfile>   Destination G-Code file. [default: stdout]
               {countdown} in file name creates a decrementing prefix
               for the output file which makes looking for the .nc in
               a crowded directory less painful - it's at the top.
               (It's the number of seconds until midnight, so clear
               the directory once a day.)
  <topic>      [ all | topics | maint | version | location | <topic> ]
         all      Print all readme.
         topics   List all topics.
         maint    Print maintenance options.
         version  Show version
         location Show absdir of main
         <topic>  Print from readme starting at topic.




Options:
     --job=<jobname>      Olabel for output code.
     --function=<fname>   Function to be compiled,
                           default is last one in source file.
     --narrow             Emit comments on their own line,
                           makes text fit more easily into
                           a narrow program window.
     --short-filenames    Emit just the lsb of filenames.
```


# Demo.

<a href="https://youtu.be/PX818-iRb1Q">
<img src="/docs/png/vicecenter1.png" alt="link to youtube.">
</a>


# Examples

for a show:

```
$ p2g examples dstdir
```

---


## Simple demo

echo "

```python

import p2g
def simple_demo():
  x = p2g.Var(199)
  for y in range(10):
    x += y

```

" ⇨ `directly` ⇨

```
O0001 (simple_demo: 0.3.10)
  #100= 199.                      (   x = Var[199]                )
  #102= 0.                        (   for y in range[10]:         )
N1000
  IF [#102 GE 10.] GOTO 1002      (   for y in range[10]:         )
  #100= #100 + #102               ( x += y                        )
  #102= #102 + 1.
  GOTO 1000
N1002
  M30
%
```

---


## Find largest number of flutes in tool table

```python

import p2g

# stop with alarm code showing largest
# flute count in table.
def maxflutes():

    mx_flutes = p2g.Var(p2g.haas.TOOL_TBL_FLUTES[0])
    for n_flutes in p2g.haas.TOOL_TBL_FLUTES:
        if n_flutes > mx_flutes:
            mx_flutes = n_flutes

    p2g.haas.MESSAGE.var = mx_flutes

```

⇨ `p2g maxflutes.py` ⇨

```
O0001 (maxflutes: 0.3.10)
  #100= #1601                     ( mx_flutes = Var[haas.TOOL_TBL_FLUTES[0]])
  #101= 1601.                     ( for n_flutes in haas.TOOL_TBL_FLUTES:)
N1000
  IF [#101 GE 1801.] GOTO 1002    ( for n_flutes in haas.TOOL_TBL_FLUTES:)
  IF [#[#101] LE #100] GOTO 1003  (     if n_flutes > mx_flutes:  )
  #100= #[#101]                   (         mx_flutes = n_flutes  )
  GOTO 1004
N1003
N1004
  #101= #101 + 1.
  GOTO 1000
N1002
  #3006= #100                     ( haas.MESSAGE.var = mx_flutes  )
  M30
%
```

---


## Less trivial example

```python
from p2g import *
from p2g.haas import *
class SearchParams:
    def __init__(self, name, search_depth, iota, delta):
        self.name = name
        self.its = 10
        self.search_depth = search_depth
        self.iota = iota
        self.delta = delta
        self.probe = goto.probe.work.feed(30).all
        self.go = goto.feed(640).work.all


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
        sys.message(ALARM[0], f"too far {sch.name}.")


def less_trivial():
    cursor = Var[3](2, 3, 4)
    # searching right, look down 0.4", move
    # 1.5" right if nothing hit.
    sch1 = SearchParams(name="right", search_depth=-0.4, iota=-0.1, delta=(1.5, 0))
    search(cursor, sch1)

```

⇨ `p2g less_trival.py` ⇨

```
O0001 (less_trivial: 0.3.10)
  #100= 2.                        ( cursor = Var[3][2, 3, 4]      )
  #101= 3.
  #102= 4.
  #103= 10.                       ( its = Var[sch.its]            )
N1000
  IF [#103 LE 0.] GOTO 1002       ( while its > 0:                )
(     sch.go[cursor]            )
  G90 G01 G55 F640. x#100 y#101 z#102
  G90 G31 G55 F30. z-0.4          (     sch.probe[z=sch.search_depth])
  IF [#5063 LT -0.5] GOTO 1001    (     if SKIP_POS.z < sch.search_depth + sch.iota:)
  #100= #100 + 1.5                (     cursor.xy += sch.delta    )
  #103= #103 - 1.                 (     its -= 1                  )
  GOTO 1000
N1002
  #3000 = 101 (too far right.)
N1001
  M30
%
```


# Variables

-   Give names to macro variables at a known address:
    
    `Fixed` ❰ `[` *size* `]` ❱\_{opt} (`addr=` *addr* ❰ `,` *init* &#x2026; ❱\_{opt} `)`

-   Give names to macro variables automatically per function.
    
    `Var` ❰ `[` *size* `]` ❱\_{opt} (❰ `,` *init* &#x2026; ❱\_{opt} `)`

-   Not actually a variable, but same syntax.
    
    `Const` ❰ `[` *size* `]` ❱\_{opt} (❰ `,` *init* &#x2026; ❱\_{opt} `)`

Example:

```python

from p2g import *  # this is the common header

def variables():
    # On my machine, Renishaw skip positions are
    # in 5061, 5062, 5063.  Look in p2g.haas.py
    # for : SKIP_POS = p2g.Fixed[20](addr=5061)
    skip0 = haas.SKIP_POS

    # can be done manualy too.
    skip1 = Fixed[3](addr=5061)

    # grab 5041.. from globals oto.
    workpos = haas.WORK_POS
    tmp0 = Var(skip0.xyz * 2.0 + workpos + skip1)

    com("Define a constant ")
    above_tdc = Const(111, 222, 3331)

    com("Use it. ")
    tmp0 += above_tdc  + 3

```

⇨ `p2g variables.py` ⇨

```
O0001 (variables: 0.3.10)
  #100= #5061 * 2. + #5041 + #5061( tmp0 = Var[skip0.xyz * 2.0 + workpos + skip1])
  #101= #5062 * 2. + #5042 + #5062
  #102= #5063 * 2. + #5043 + #5063
( Define a constant  )
( Use it.  )
  #100= #100 + 114.               ( tmp0 += above_tdc  + 3        )
  #101= #101 + 225.
  #102= #102 + 3334.
  M30
%
```


# Coordinates

Describe position, with axis by location, in sequence or by name.

```python
from p2g import *  # this is the common header
from p2g.haas import *  # to all the examples


def coordinates():
    com("Describe 3 variables at 3000")
    dst = Fixed[3](addr=3000)
    com("Fill with 1,2,31")
    dst.var = (1, 2, 31)

    com("Set by parts")
    dst.y = 7
    dst.z = 71
    dst.x = 19

    offset = Const(0.101, 0.102, 0.103)
    com("Arithmetic")
    dst.var += (1, 2, 3)
    dst.var -= offset
    dst.var %= sin(asin(offset) + 7)

    com("When describing a location:")
    com("Coords by order.")
    p1 = Fixed[3](1, 2, 3, addr=100)

    com("Coords by axis name.")
    p2 = Fixed[3](z=333, y=222, x=111, addr=200)
    p2.x = 17

    com("Coords by index.")
    p1.xyz = p2[2]
    p2[1:3] = 7

    com("Mix them up.")
    p1.yz = p2.yz[1]
```

⇨ `p2g coordinates.py` ⇨

```
O0001 (coordinates: 0.3.10)
( Describe 3 variables at 3000 )
( Fill with 1,2,31 )
  #3000= 1.                       ( dst.var = [1, 2, 31]          )
  #3001= 2.
  #3002= 31.
( Set by parts )
  #3001= 7.                       ( dst.y = 7                     )
  #3002= 71.                      ( dst.z = 71                    )
  #3000= 19.                      ( dst.x = 19                    )
( Arithmetic )
  #3000= #3000 + 1.               ( dst.var += [1, 2, 3]          )
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
%
```


# Goto

Goto functions are constructed from parts, and make building blocks when partially applied.

**goto** [ . «modifier» ]⋆ **(** «coordinates» **)**

«modifier» :

-   `r9810` Use Renishaw macro 9810 to do a protected positioning cycle.
-   `work` Use current work coordinate system. - whatever set with set\_wcs
-   `machine` Use the machine coordinate system - G53
-   `relative` Use relative coordinate system - G91
-   `absolute` Use absolute coordinate system - G90
-   `z_first` move Z axis first.
-   `z_last` move the other axes bef1ore the Z.
-   `probe` Emit probe code using G31.
-   `xyz` Move all axes at once.
-   `feed(` *expr* `)` Set feed rate.
-   `mcode(` *string* `)` Apply an mcode.

```python
from p2g import *

def goto_demo():
    g1 = goto.work.feed(20).all

    comment("in work cosys, goto x=1, y=2, z=3 at 20ips")
    g1(1, 2, 3)

    comment("make a variable, 2,3,4")
    v1 = Var(x=2, y=3, z=4)

    absslow = goto.machine.feed(10)

    comment("In the machine cosys, move to v1.z then v1.xy, slowly")

    absslow.z_first(v1)

    comment("p1 is whatever absslow was, with feed adjusted to 100.")
    p1 = absslow.feed(100)
    p1.z_last(v1)

    comment("p2 is whatever p1 was, with changed to a probe.")
    p2 = p1.probe
    p2.z_last(v1)

    comment("move a and c axes ")
    axis.NAMES = "xyza*c"
    goto.feed(20).all.relative(a=9, c=90)

    comment("probe with a hass MUST_SKIP mcode.")
    goto.probe.feed(10).mcode("M79").relative.all(3, 4, 5)

    comment("Define shortcut for safe_goto and use.")
    safe_goto = goto.feed(27).r9810

    safe_goto.z_first(1, 2, 3)
```

⇨ `p2g goto_demo.py` ⇨

```
O0001 (goto_demo: 0.3.10)

( in work cosys, goto x=1, y=2, z=3 at 20ips )
  G90 G01 G55 F20. x1. y2. z3.    ( g1[1, 2, 3]                   )

( make a variable, 2,3,4 )
  #100= 2.                        ( v1 = Var[x=2, y=3, z=4]       )
  #101= 3.
  #102= 4.

( In the machine cosys, move to v1.z then v1.xy, slowly )
  G90 G53 G01 G55 F10. z#102      ( absslow.z_first[v1]           )
  G90 G53 G01 G55 F10. x#100 y#101

( p1 is whatever absslow was, with feed adjusted to 100. )
( p1.z_last[v1]                 )
  G90 G53 G01 G55 F100. x#100 y#101
  G90 G53 G01 G55 F100. z#102

( p2 is whatever p1 was, with changed to a probe. )
( p2.z_last[v1]                 )
  G90 G53 G31 G55 F100. x#100 y#101
  G90 G53 G31 G55 F100. z#102

( move a and c axes  )
  G91 G01 G55 F20. a9. c90.       ( goto.feed[20].all.relative[a=9, c=90])

( probe with a hass MUST_SKIP mcode. )
  G91 G31 G55 M79 F10. x3. y4. z5.( goto.probe.feed[10].mcode["M79"].relative.all[3, 4, 5])

( Define shortcut for safe_goto and use. )
  G65 R9810 F27. z3.              ( safe_goto.z_first[1, 2, 3]    )
  G65 R9810 F27. x1. y2.
  M30
%
```


# Axes

Any number of axes are supported, default just being xy and z.

A rotary on ac can be set with p2g.axis.NAMES="xyza\*c". The axis letters should be the same order as your machine expects coordinates to turn up in work offset registers.

```python
import p2g
from p2g.haas import *


def a5():
    p2g.axis.NAMES = "xyza*c"
    p2g.com("rhs of vector ops get expanded as needed")
    G55.var = [0, 1]
    p2g.com("fill yz and c with some stuff")
    tmp1 = p2g.Const(y=3, z=9, c=p2g.asin(0.5))
    p2g.com(
        "Unmentioned axes values are assumed", "to be 0, so adding them makes no code."
    )
    G55.var += tmp1
    p2g.com("")
    G55.ac *= 2.0

    p2g.com("Rotaries.")
    p4 = p2g.Fixed[6](addr=200)
    p4.a = 180
    p4.c = p2g.asin(0.5)


def a3():
    # xyz is the default.
    # but overridden because a5 called first, so
    p2g.axis.NAMES = "xyz"
    p2g.com("Filling to number of axes.")
    G55.var = [0]
    tmp = p2g.Var(G55 * 34)


def axes():
    a5()
    a3()
```

⇨ `p2g axes.py` ⇨

```
O0001 (axes: 0.3.10)
( rhs of vector ops get expanded as needed )
  #5241= 0.                       ( G55.var = [0, 1]              )
  #5242= 1.
  #5243= 0.
  #5244= 1.
  #5245= 0.
  #5246= 1.
( fill yz and c with some stuff )
( Unmentioned axes values are assumed    )
( to be 0, so adding them makes no code. )
  #5242= #5242 + 3.               ( G55.var += tmp1               )
  #5243= #5243 + 9.
  #5246= #5246 + 30.

  #5244= #5244 * 2.               ( G55.ac *= 2.0                 )
  #5246= #5246 * 2.
( Rotaries. )
  #203= 180.                      ( p4.a = 180                    )
  #205= 30.                       ( p4.c = asin[0.5]              )
( Filling to number of axes. )
  #5241= 0.                       ( G55.var = [0]                 )
  #5242= 0.
  #5243= 0.
  #100= #5241 * 34.               ( tmp = Var[G55 * 34]           )
  #101= #5242 * 34.
  #102= #5243 * 34.
  M30
%
```


# When

'when' works as in python, save there are no exceptions; useful for turning on probing and magically getting it turned off,. Or setting and restoring the wcs etc etc (look in p2g/sys.py)


## Setting and resetting lookahead.

```python
import p2g

def start():
    p2g.comment ("turn  off lookahead before the probe")
    with p2g.sys.Lookahead(lookahead = False) :
         p2g.goto.probe.work.feed(20).z_first(z = -10)

    p2g.comment("back here.")
    p2g.goto.work.feed(200).z_first(z = 10)

    p2g.comment ("ask to turn it on, it's already on,",
                 "so doesn't emit the code again.")

    with p2g.sys.Lookahead(lookahead = True) :
         p2g.goto.machine.feed(20).xyz(1,32,3)


```

⇨ `p2g when_lookahead.py` ⇨

```
O0001 (start: 0.3.10)

( turn  off lookahead before the probe )
  M97 P123                        ( with sys.Lookahead[lookahead = False] :)
  G90 G31 G55 F20. z-10.          (      goto.probe.work.feed[20].z_first[z = -10])
  G103

( back here. )
  G90 G01 G55 F200. z10.          ( goto.work.feed[200].z_first[z = 10])

( ask to turn it on, it's already on, )
( so doesn't emit the code again.     )
(      goto.machine.feed[20].xyz[1,32,3])
  G90 G53 G01 G55 F20. x1. y32. z3.
  M30
N123
  G103 P1
  G04 P1
  G04 P1
  G04 P1
  G04 P1
  M99
%
```

Here's setting and resetting block delete, the code 'when' code is already in p2g.sys.Optional

```python
import p2g
from p2g import haas

PROBE = 1

class Optional:
    prev: str
    def __init__(self):
        self.prev = p2g.gbl.Control.code_prefix
        p2g.gbl.Control.code_prefix = "/"

    def __enter__(self):
        pass

    def __exit__(self, *_):
       p2g.gbl.Control.code_prefix = self.prev

class Probe:
    def __enter__(self):
        p2g.sys.load_tool(PROBE)
        p2g.codenl(haas.SPINDLE_PROBE_ON, comment_txt="Probe on.")

    def __exit__(self, *_):
        p2g.codenl(haas.SPINDLE_PROBE_OFF, comment_txt="Probe off.")


def when_demo_block_delete():
    with Probe():
        tmp = p2g.Var(9)
        with Optional():
            tmp.var += 91
        p2g.sys.print(f"tmp is {tmp}")


```

    O0001 (when_demo_block_delete: 0.3.10)
      T01 M06                         (     sys.load_tool[PROBE]      )
      G65 P9832                       ( Probe on.                     )
      #100= 9.                        (     tmp = Var[9]              )
    /  #100= #100 + 91.               (         tmp.var += 91         )
    DPRNT[tmp*is*#100[42]]
      G65 P9833                       ( Probe off.                    )
      M30
    %


# DPRNT

P2G turns Python f string into runes that DPRNT can digest.

The conversion makes print operation on vectors easy.


## DPRNT examples


### Constants

```python
import p2g
def dprint_constants():
    src = p2g.Const(12.34,2,3)
    p2g.sys.print (f"A {src}")
    p2g.sys.print (f"B {src:6.2}")
    p2g.sys.print (f"C {src:a###.###b}")
    p2g.sys.print (f"D {src:a###.###b?, }")
```

⇨ `p2g dprnt_constants.py` ⇨

    O0001 (dprint_constants: 0.3.10)
    DPRNT[A***12.34***2.00***3.00]
    DPRNT[B**12.34**2.00**3.00]
    DPRNT[C*a*12.340ba**2.000ba**3.000b]
    DPRNT[D*a*12.340b,*a**2.000b,*a**3.000b]
      M30
    %


### Vectors

```python
import p2g
def dprint_vectors():
    src = p2g.Fixed[2](addr=100)
    p2g.sys.print (f"A {src}")
    p2g.sys.print (f"B {src:6.2}")
    p2g.sys.print (f"C {src:a###.###b}")
    p2g.sys.print (f"D {src:a###.###b?, }")
```

⇨ `p2g dprnt_vectors.py` ⇨

    O0001 (dprint_vectors: 0.3.10)
    DPRNT[A*#100[42]#101[42]]
    DPRNT[B*#100[32]#101[32]]
    DPRNT[C*a#100[33]ba#101[33]b]
    DPRNT[D*a#100[33]b,*a#101[33]b]
      M30
    %


### In subroutines.

```python
import p2g

def dprint_something(src):
    p2g.sys.print (f"results: {src:j!###.#?, }")

def dprnt_subs():
    dprint_something(p2g.Fixed[2](addr=100))
    dprint_something(p2g.Const[2](7.34,8.12))

```

⇨ `p2g dprnt_subs.py` ⇨

    O0001 (dprnt_subs: 0.3.10)
    DPRNT[results:*j0#100[31],*j1#101[31]]
    DPRNT[results:*j0**7.3,*j1**8.1]
      M30
    %


### So painless.

```python
import p2g

def dprnt_painless():
    n = p2g.Fixed[10](addr=200)
    for idx in range(10):
        p2g.sys.print (f"this is row {idx:##}, el is {n[idx]:###.#}")

```

⇨ `p2g dprnt_painless.py` ⇨

```
O0001 (dprnt_painless: 0.3.10)
  #101= 0.                        ( for idx in range[10]:         )
N1000
  IF [#101 GE 10.] GOTO 1002      ( for idx in range[10]:         )
  #102= #[#101 + 200]             (     sys.print [f"this is row {idx:##}, el is {n[idx]:###.#}"])
DPRNT[this*is*row*#101[20],*el*is*#102[31]]
  #101= #101 + 1.
  GOTO 1000
N1002
  M30
%
```


### Can use Python f-strings too.

```python
from p2g import *
from p2g.haas import *

def dprnt_std_python():
    x = Var(32)
    y = Var(27)

    for q in range(10):
        sys.print(f"X is {x:3.1f}, Y+Q is {y+q:5.2f}")

```

⇨ `p2g dprnt_std_python.py` ⇨

```
O0001 (dprnt_std_python: 0.3.10)
  #100= 32.                       ( x = Var[32]                   )
  #101= 27.                       ( y = Var[27]                   )
  #103= 0.                        ( for q in range[10]:           )
N1000
  IF [#103 GE 10.] GOTO 1002      ( for q in range[10]:           )
  #104= #101 + #103               (     sys.print[f"X is {x:3.1f}, Y+Q is {y+q:5.2f}"])
DPRNT[X*is*#100[11],*Y+Q*is*#104[22]]
  #103= #103 + 1.
  GOTO 1000
N1002
  M30
%
```


## Extended f-string syntax

-   **[  «digit» [ .«digit» ]﹖] **f**:** standard Python floating point format.
-   «e-string» [ «number-spec» ] «e-string» [ **?** «separator-string» ]﹖]
    -   **«e-string»:** Text, with some characters substituted on output.
        -   `!` Index of element.
        -   `@` Axis name of element.
    
    -   **«number-spec»:** A picture describing the layout of the number to be printed using `#` signs.
    
    -   **«separator-string»:** As an «e-string», but only expanded between items.


# Symbol Tables

Set the global `p2g.Control.symbol_table` to get a symbol table in the output file.

```python
import p2g
x1 = -7
MACHINE_ABS_ABOVE_OTS = p2g.Const(x=x1, y=8, z=9)
MACHINE_ABS_ABOVE_SEARCH_ROTARY_LHS_5X8 = p2g.Const(100, 101, 102)
MACHINE_ABS_ABOVE_VICE = p2g.Const(x=17, y=18, z=19)
RAW_ANALOG = p2g.Fixed[10](addr=1080)
fish = 10
not_used = 12

def symbol_table_demo():
      p2g.Control.symbol_table = True    
      p2g.comment("Only used symbols are in output table.")
      p2g.Var(MACHINE_ABS_ABOVE_OTS)
      p2g.Var(MACHINE_ABS_ABOVE_VICE * fish)
      v1 = p2g.Var()
      v1 += RAW_ANALOG[7]
```

⇨ `p2g symbol_table_demo.py` ⇨

```
O0001 (symbol_table_demo: 0.3.10)
( Symbol Table )

 ( MACHINE_ABS_ABOVE_OTS                   :  -7.000,  8.000,  9.000 )
 ( MACHINE_ABS_ABOVE_SEARCH_ROTARY_LHS_5X8 : 100.000,101.000,102.000 )
 ( MACHINE_ABS_ABOVE_VICE                  :  17.000, 18.000, 19.000 )

 ( RAW_ANALOG                              : #1080[10]               )
 ( v1                                      :  #106.x                 )


( Only used symbols are in output table. )
  #100= -7.                       (   Var[MACHINE_ABS_ABOVE_OTS]  )
  #101= 8.
  #102= 9.
  #103= 170.                      (   Var[MACHINE_ABS_ABOVE_VICE * fish])
  #104= 180.
  #105= 190.
  #106= #106 + #1087              (   v1 += RAW_ANALOG[7]         )
  M30
%
```


# Notes


## Stuff you already know

As someone who uses a machine that can reduce $1000 of flat bar into a bucket of chips, bits and coolant before you can say "I forgot to tighten the vice.", you know about some of the bad things that would happen if skynet were to notice you.

You'll make a wise and considered decision about using some random internet stranger's program to control your machine.

If p2g crashes your mill so hard it kills your cat, well, you should have seen what it did to my cat. Stumpy was a good cat.

That said, p2g makes it pleasant to write code to manipulate the translations on work pieces so that complex fixtures aren't needed.


## Cool example

```python

from p2g import *
class X:
    def __init__(self, a, b):
        self.thisone = a
        self.b = b

    def adjust(self, tof):
        self.thisone += tof.x
        self.b += tof.y

class Y:
    def __init__(self, a):
        self.val = a

    def adjust(self, tof):
        self.val += tof

    # an example of overloading.
    # I'm not recommending replacing add with
    # multiply, but it would work. Don't do this
    # if you're sending a probe to mars.
    def __add__(self, other):
        return self.val * other + 3

def cool():
    com("You can do surprising things.")

    avariable_scalar = Var(100)
    x_instance = X(avariable_scalar, 34)
    another_xandy = Var(7, 8)

    x_instance.adjust(haas.TOOL_OFFSET)

    q = Y(another_xandy) + (x_instance.thisone, x_instance.b)
    sys.print(f"{q[0]}{q[1]}")


```

⇨ `p2g cool.py` ⇨

```
O0001 (cool: 0.3.10)
( You can do surprising things. )
  #100= 100.                      ( avariable_scalar = Var[100]   )
  #101= 7.                        ( another_xandy = Var[7, 8]     )
  #102= 8.
  #103= #101 * [#100 + #5081] + 3.( sys.print[f"{q[0]}{q[1]}"]    )
  #104= #102 * [#5082 + 34.] + 3.
DPRNT[#103[42]#104[42]]
  M30
%
```


## Beware

Unexpected (to Python users) assignment semantics.

```python

import p2g

def beware0():
    a = p2g.Fixed(addr=100)
    b = p2g.Fixed(addr=200)
    c = p2g.Fixed[3](addr=100)
    p2g.com("this moves contents of macro var 200 into 100",
            "it doesn't rewrite a.")
    a =  b[0]
    p2g.com("again, this copies the referees.")
    a =  b
    p2g.com("and this")
    a[0] =  b
    p2g.com("this moves three from 200 into 100")
    c =  b
    p2g.com("anything can be the source")
    c[0:2] = c[1:3] + 2 * b
    p2g.com("anything can be the source")
    c.xyz = 1,2,3

    p2g.com("but p2g is too dumb to do it in the ",
            "right order to avoid overwiting the source")
    c[1:3] = c[0:2] + 2 * b

```

⇨ `p2g beware0.py` ⇨

```
O0001 (beware0: 0.3.10)
( this moves contents of macro var 200 into 100 )
( it doesn't rewrite a.                         )
  #100= #200                      ( a =  b[0]                     )
( again, this copies the referees. )
  #100= #200                      ( a =  b                        )
( and this )
  #100= #200                      ( a[0] =  b                     )
( this moves three from 200 into 100 )
  #100= #200                      ( c =  b                        )
  #101= #200
  #102= #200
( anything can be the source )
  #100= #101 + #200 * 2.          ( c[0:2] = c[1:3] + 2 * b       )
  #101= #102 + #200 * 2.
( anything can be the source )
  #100= 1.                        ( c.xyz = 1,2,3                 )
  #101= 2.
  #102= 3.
( but p2g is too dumb to do it in the        )
( right order to avoid overwiting the source )
  #101= #100 + #200 * 2.          ( c[1:3] = c[0:2] + 2 * b       )
  #102= #101 + #200 * 2.
  M30
%
```


# MIT License

Copyright © 2023 Steve Chamberlain

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


# Authors

sac@pobox.com


# Thanks

all the good parts of walk\*.py are from:

```
Python AST interpreter written in Python

This module is part of the Pycopy https://github.com/pfalcon/pycopy
project.

Copyright (c) 2019 Paul Sokolovsky

The MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
```


# Haas macro variables

```
                           HAAS Macro Variables                            
┏━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃      Range      ┃      N ┃  K ┃    Type     ┃ Name                      ┃
┡━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│       #0        │      1 │ v< │    float    │ NULL                      │
│    #1 … #33     │     33 │  V │    float    │ MACRO_ARGUMENTS           │
│    #34 … #99    │     66 │  _ │    float    │ an error                  │
│   #100 … #149   │     50 │  V │    float    │ GP_SAVED1                 │
│   #150 … #199   │     50 │  V │    float    │ PROBE_VALUES              │
│   #200 … #499   │    300 │  _ │    float    │ GAP02                     │
│   #500 … #549   │     50 │  V │    float    │ GP_SAVED2                 │
│   #550 … #555   │      6 │  V │    float    │ PROBE_CALIB1              │
│   #556 … #558   │      3 │  V │    float    │ PROBE_R                   │
│   #559 … #580   │     22 │  V │    float    │ PROBE_CALIB2              │
│   #581 … #699   │    119 │  V │    float    │ GP_SAVED3                 │
│   #700 … #799   │    100 │  _ │    float    │ GAP03                     │
│   #800 … #999   │    200 │  V │    float    │ GP_SAVED4                 │
│  #1000 … #1063  │     64 │  V │    float    │ INPUTS                    │
│  #1064 … #1068  │      5 │  V │    float    │ MAX_LOADS_XYZAB           │
│  #1069 … #1079  │     11 │  _ │    float    │ GAP04                     │
│  #1080 … #1089  │     10 │  V │    float    │ RAW_ANALOG                │
│  #1090 … #1097  │      8 │  V │    float    │ FILTERED_ANALOG           │
│      #1098      │      1 │ v< │    float    │ SPINDLE_LOAD              │
│  #1099 … #1263  │    165 │  _ │    float    │ GAP05                     │
│  #1264 … #1268  │      5 │  V │    float    │ MAX_LOADS_CTUVW           │
│  #1269 … #1600  │    332 │  _ │    float    │ GAP06                     │
│  #1601 … #1800  │    200 │  T │     int     │ TOOL_TBL_FLUTES           │
│  #1801 … #2000  │    200 │  T │    float    │ TOOL_TBL_VIBRATION        │
│  #2001 … #2200  │    200 │  T │    float    │ TOOL_TBL_OFFSETS          │
│  #2201 … #2400  │    200 │  T │    float    │ TOOL_TBL_WEAR             │
│  #2401 … #2600  │    200 │  T │    float    │ TOOL_TBL_DROFFSET         │
│  #2601 … #2800  │    200 │  T │    float    │ TOOL_TBL_DRWEAR           │
│  #2801 … #2999  │    199 │  _ │    float    │ GAP07                     │
│      #3000      │      1 │ v< │     int     │ ALARM                     │
│      #3001      │      1 │ v< │    Time     │ T_MS                      │
│      #3002      │      1 │ v< │    Time     │ T_HR                      │
│      #3003      │      1 │ v< │     int     │ SINGLE_BLOCK_OFF          │
│      #3004      │      1 │ v< │     int     │ FEED_HOLD_OFF             │
│      #3005      │      1 │  _ │    float    │ GAP08                     │
│      #3006      │      1 │ v< │     int     │ MESSAGE                   │
│  #3007 … #3010  │      4 │  _ │    float    │ GAP09                     │
│      #3011      │      1 │ v< │    Time     │ YEAR_MONTH_DAY            │
│      #3012      │      1 │ v< │    Time     │ HOUR_MINUTE_SECOND        │
│  #3013 … #3019  │      7 │  _ │    float    │ GAP10                     │
│      #3020      │      1 │ v< │    Time     │ POWER_ON_TIME             │
│      #3021      │      1 │ v< │    Time     │ CYCLE_START_TIME          │
│      #3022      │      1 │ v< │    Time     │ FEED_TIMER                │
│      #3023      │      1 │ v< │    Time     │ CUR_PART_TIMER            │
│      #3024      │      1 │ v< │    Time     │ LAST_COMPLETE_PART_TIMER  │
│      #3025      │      1 │ v< │    Time     │ LAST_PART_TIMER           │
│      #3026      │      1 │ v< │     int     │ TOOL_IN_SPIDLE            │
│      #3027      │      1 │ v< │     int     │ SPINDLE_RPM               │
│      #3028      │      1 │ v< │     int     │ PALLET_LOADED             │
│      #3029      │      1 │  _ │    float    │ GAP11                     │
│      #3030      │      1 │ v< │     int     │ SINGLE_BLOCK              │
│      #3031      │      1 │ v< │    float    │ AGAP                      │
│      #3032      │      1 │ v< │     int     │ BLOCK_DELETE              │
│      #3033      │      1 │ v< │     int     │ OPT_STOP                  │
│  #3034 … #3195  │    162 │  _ │    float    │ GAP12                     │
│      #3196      │      1 │ v< │    Time     │ TIMER_CELL_SAFE           │
│  #3197 … #3200  │      4 │  _ │    float    │ GAP13                     │
│  #3201 … #3400  │    200 │  T │    float    │ TOOL_TBL_DIAMETER         │
│  #3401 … #3600  │    200 │  T │    float    │ TOOL_TBL_COOLANT_POSITION │
│  #3601 … #3900  │    300 │  _ │    float    │ GAP14                     │
│      #3901      │      1 │ v< │     int     │ M30_COUNT1                │
│      #3902      │      1 │ v< │     int     │ M30_COUNT2                │
│  #3903 … #4000  │     98 │  _ │    float    │ GAP15                     │
│  #4001 … #4013  │     13 │  V │    float    │ PREV_BLOCK                │
│      #4014      │      1 │  V │    float    │ PREV_WCS                  │
│  #4015 … #4021  │      7 │  _ │    float    │ PREV_BLOCK_B              │
│  #4022 … #4100  │     79 │  _ │    float    │ GAP122                    │
│  #4101 … #4126  │     26 │  V │    float    │ PREV_BLOCK_ADDRESS        │
│  #4127 … #5000  │    874 │  _ │    float    │ an error                  │
│  #5001 … #5020  │  naxes │  m │    float    │ LAST_TARGET_POS           │
│  #5021 … #5040  │  naxes │  m │    float    │ MACHINE_POS               │
│  #5021 … #5040  │     20 │  A │    float    │  also MACHINE             │
│  #5021 … #5040  │     20 │  A │    float    │  also G53                 │
│  #5041 … #5060  │  naxes │  m │    float    │ WORK_POS                  │
│  #5041 … #5060  │     20 │  A │    float    │  also WORK                │
│      #5041      │    -20 │  _ │    float    │ an error                  │
│  #5061 … #5080  │  naxes │  m │    float    │ SKIP_POS                  │
│  #5061 … #5080  │     20 │  A │    float    │  also PROBE               │
│      #5061      │    -40 │  _ │    float    │ an error                  │
│  #5081 … #5100  │  naxes │  V │    float    │ TOOL_OFFSET               │
│      #5081      │    -40 │  _ │    float    │ an error                  │
│  #5101 … #5200  │    100 │  _ │    float    │ GAP18                     │
│  #5201 … #5220  │  naxes │  m │    float    │ G52                       │
│  #5221 … #5240  │  naxes │  m │    float    │ G54                       │
│  #5241 … #5260  │  naxes │  m │    float    │ G55                       │
│  #5261 … #5280  │  naxes │  m │    float    │ G56                       │
│  #5281 … #5300  │  naxes │  m │    float    │ G57                       │
│  #5301 … #5320  │  naxes │  m │    float    │ G58                       │
│  #5321 … #5340  │  naxes │  m │    float    │ G59                       │
│  #5341 … #5400  │     60 │  _ │    float    │ GAP19                     │
│  #5401 … #5500  │    100 │  T │    Secs     │ TOOL_TBL_FEED_TIMERS      │
│  #5501 … #5600  │    100 │  T │    Secs     │ TOOL_TBL_TOTAL_TIMERS     │
│  #5601 … #5700  │    100 │  T │     int     │ TOOL_TBL_LIFE_LIMITS      │
│  #5701 … #5800  │    100 │  T │     int     │ TOOL_TBL_LIFE_COUNTERS    │
│  #5801 … #5900  │    100 │  T │    float    │ TOOL_TBL_LIFE_MAX_LOADS   │
│  #5901 … #6000  │    100 │  T │    float    │ TOOL_TBL_LIFE_LOAD_LIMITS │
│  #6001 … #6197  │    197 │  _ │    float    │ GAP20                     │
│      #6198      │      1 │ v< │     int     │ NGC_CF                    │
│  #6199 … #7000  │    802 │  _ │    float    │ GAP21                     │
│  #7001 … #7020  │  naxes │  m │    float    │ G154_P1                   │
│  #7021 … #7040  │  naxes │  m │    float    │ G154_P2                   │
│  #7041 … #7060  │  naxes │  m │    float    │ G154_P3                   │
│  #7061 … #7080  │  naxes │  m │    float    │ G154_P4                   │
│  #7081 … #7100  │  naxes │  m │    float    │ G154_P5                   │
│  #7101 … #7120  │  naxes │  m │    float    │ G154_P6                   │
│  #7121 … #7140  │  naxes │  m │    float    │ G154_P7                   │
│  #7141 … #7160  │  naxes │  m │    float    │ G154_P8                   │
│  #7161 … #7180  │  naxes │  m │    float    │ G154_P9                   │
│  #7181 … #7200  │  naxes │  m │    float    │ G154_P10                  │
│  #7201 … #7220  │  naxes │  m │    float    │ G154_P11                  │
│  #7221 … #7240  │  naxes │  m │    float    │ G154_P12                  │
│  #7241 … #7260  │  naxes │  m │    float    │ G154_P13                  │
│  #7261 … #7280  │  naxes │  m │    float    │ G154_P14                  │
│  #7281 … #7300  │  naxes │  m │    float    │ G154_P15                  │
│  #7301 … #7320  │  naxes │  m │    float    │ G154_P16                  │
│  #7321 … #7340  │  naxes │  m │    float    │ G154_P17                  │
│  #7341 … #7360  │  naxes │  m │    float    │ G154_P18                  │
│  #7361 … #7380  │  naxes │  m │    float    │ G154_P19                  │
│  #7381 … #7400  │  naxes │  m │    float    │ G154_P20                  │
│  #7401 … #7500  │    100 │  _ │    float    │ GAP22                     │
│  #7501 … #7600  │    100 │  L │ PalletTable │ PALLET_PRIORITY           │
│  #7601 … #7700  │    100 │  L │ PalletTable │ PALLET_STATUS             │
│  #7701 … #7800  │    100 │  L │ PalletTable │ PALLET_PROGRAM            │
│  #7801 … #7900  │    100 │  L │ PalletTable │ PALLET_USAGE              │
│  #7901 … #8499  │    599 │  _ │    float    │ GAP23                     │
│      #8500      │      1 │ v< │     int     │ ATM_ID                    │
│      #8501      │      1 │ v< │   Percent   │ ATM_PERCENT               │
│      #8502      │      1 │ v< │     int     │ ATM_TOTAL_AVL_USAGE       │
│      #8503      │      1 │ v< │     int     │ ATM_TOTAL_AVL_HOLE_COUNT  │
│      #8504      │      1 │ v< │    Secs     │ ATM_TOTAL_AVL_FEED_TIME   │
│      #8505      │      1 │ v< │    Secs     │ ATM_TOTAL_AVL_TOTAL_TIME  │
│  #8506 … #8509  │      4 │  _ │    float    │ GAP24                     │
│      #8510      │      1 │ v< │     int     │ ATM_NEXT_TOOL_NUMBER      │
│      #8511      │      1 │ v< │   Percent   │ ATM_NEXT_TOOL_LIFE        │
│      #8512      │      1 │ v< │     int     │ ATM_NEXT_TOOL_AVL_USAGE   │
│      #8513      │      1 │ v< │     int     │ ATM_NEXT_TOOL_HOLE_COUNT  │
│      #8514      │      1 │ v< │    Secs     │ ATM_NEXT_TOOL_FEED_TIME   │
│      #8515      │      1 │ v< │    Secs     │ ATM_NEXT_TOOL_TOTAL_TIME  │
│  #8516 … #8549  │     34 │  _ │    float    │ GAP25                     │
│      #8550      │      1 │ v< │     int     │ TOOL_ID                   │
│      #8551      │      1 │ v< │     int     │ TOOL_FLUTES               │
│      #8552      │      1 │ v< │    float    │ TOOL_MAX_VIBRATION        │
│      #8553      │      1 │ v< │    float    │ TOOL_LENGTH_OFFSETS       │
│      #8554      │      1 │ v< │    float    │ TOOL_LENGTH_WEAR          │
│      #8555      │      1 │ v< │    float    │ TOOL_DIAMETER_OFFSETS     │
│      #8556      │      1 │ v< │    float    │ TOOL_DIAMETER_WEAR        │
│      #8557      │      1 │ v< │    float    │ TOOL_ACTUAL_DIAMETER      │
│      #8558      │      1 │ v< │     int     │ TOOL_COOLANT_POSITION     │
│      #8559      │      1 │ v< │    Secs     │ TOOL_FEED_TIMER           │
│      #8560      │      1 │ v< │    Secs     │ TOOL_TOTAL_TIMER          │
│      #8561      │      1 │ v< │    float    │ TOOL_LIFE_LIMIT           │
│      #8562      │      1 │ v< │    float    │ TOOL_LIFE_COUNTER         │
│      #8563      │      1 │ v< │    float    │ TOOL_LIFE_MAX_LOAD        │
│      #8564      │      1 │ v< │    float    │ TOOL_LIFE_LOAD_LIMIT      │
│  #8565 … #8999  │    435 │  _ │    float    │ GAP26                     │
│      #9000      │      1 │ v< │    float    │ THERMAL_COMP_ACC          │
│  #9001 … #9015  │     15 │  _ │    float    │ GAP27                     │
│      #9016      │      1 │ v< │    float    │ THERMAL_SPINDLE_COMP_ACC  │
│  #9017 … #9999  │    983 │  _ │    float    │ an error                  │
│ #10000 … #10999 │   1000 │  V │    float    │ GVARIABLES3               │
│ #10150 … #10199 │     50 │  V │    float    │ PROBE_VALUES_             │
│ #10200 … #10399 │    200 │  V │    float    │ GPS1                      │
│ #10400 … #10499 │    100 │  V │    float    │ GPNS1                     │
│ #10500 … #10549 │     50 │  V │    float    │ GPS2                      │
│ #10550 … #10599 │     50 │  V │    float    │ PROBE_CALIB_              │
│ #10600 … #10699 │    100 │  V │    float    │ GPS3                      │
│ #10700 … #10799 │    100 │  V │    float    │ GPNS3                     │
│ #10800 … #10999 │    200 │  V │    float    │ GPS4                      │
│     #11000      │   -850 │  _ │    float    │ an error                  │
│ #11000 … #11255 │    256 │  V │    float    │ INPUTS1                   │
│ #11256 … #11999 │    744 │  _ │    float    │ GAP29                     │
│ #12000 … #12255 │    256 │  V │    float    │ OUTPUT1                   │
│ #12256 … #12999 │    744 │  _ │    float    │ GAP30                     │
│ #13000 … #13012 │     13 │  V │    float    │ FILTERED_ANALOG1          │
│     #13013      │      1 │ v< │    float    │ COOLANT_LEVEL             │
│ #13014 … #13063 │     50 │  V │    float    │ FILTERED_ANALOG2          │
│ #13064 … #13999 │    936 │  _ │    float    │ GAP31                     │
│ #14000 … #19999 │   6000 │  _ │    float    │ an error                  │
│ #20000 … #29999 │  10000 │  V │    float    │ SETTING                   │
│ #30000 … #39999 │  10000 │  V │    float    │ PARAMETER                 │
│ #40000 … #50000 │  10001 │  _ │    float    │ an error                  │
│ #50001 … #50200 │    200 │  V │    float    │ TOOL_TYP                  │
│ #50201 … #50400 │    200 │  V │    float    │ TOOL_MATERIAL             │
│ #50401 … #50600 │    200 │  _ │    float    │ GAP32                     │
│ #50601 … #50800 │    200 │  V │    float    │ CURRENT_OFFSET            │
│ #50801 … #51000 │    200 │  _ │    float    │ an error                  │
│ #50801 … #51000 │    200 │  V │    float    │ CURRENT_OFFSET2           │
│ #51001 … #51300 │    300 │  _ │    float    │ GAP33                     │
│ #51001 … #51300 │    300 │  _ │    float    │ an error                  │
│     #51301      │   -500 │  _ │    float    │ an error                  │
│ #51301 … #51400 │    100 │  V │    float    │ VPS_TEMPLATE_OFFSET       │
│ #51401 … #51600 │    200 │  V │    float    │ WORK_MATERIAL             │
│ #51601 … #51800 │    200 │  V │    float    │ VPS_FEEDRATE              │
│ #51801 … #52000 │    200 │  V │    float    │ APPROX_LENGTH             │
│ #52001 … #52200 │    200 │  V │    float    │ APPROX_DIAMETER           │
│ #52201 … #52400 │    200 │  V │    float    │ EDGE_MEASURE_HEIGHT       │
│ #52401 … #52600 │    200 │  V │    float    │ TOOL_TOLERANCE            │
│ #52601 … #52800 │    200 │  V │    float    │ PROBE_TYPE                │
│     #52801      │ -47740 │  _ │    float    │ an error                  │
└─────────────────┴────────┴────┴─────────────┴───────────────────────────┘
         Generated by /home/sac/vf3/progs/p2g/tools/makestdvars.py         
```