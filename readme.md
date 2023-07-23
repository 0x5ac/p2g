---

<https://codecov.io/gh/0x5ac/p2g/branch/master/graph/badge.svg?token=FKR0R7P8U1>
![img](https://img.shields.io/badge/License-MIT%20v3-blue.svg)
![img](https://github.com/0x5ac/p2g/actions/workflows/build.yml/badge.svg)


<a id="Version"></a>

### Version  0.2.104

---


<a id="Introduction"></a>

# Introduction.

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

---


# Table of Contents

1.  [Introduction.](#Introduction)
2.  [Usage.](#Usage)
3.  [Install:](#Install)
4.  [Examples.](#Examples.)
    1.  [Simple demo.](#SimpleDemo)
    2.  [Non trivial demo:](#NonTrivalDemo)
5.  [Variables](#Variables)
6.  [Coordinates.](#Coordinates)
7.  [Expressions](#Expressions)
8.  [Axes](#Axes)
9.  [When](#When)
10. [Goto](#Goto)
11. [Printing](#Printing)
12. [Symbol Tables.](#SymbolTables)
13. [Notes](#Notes)
14. [HAAS macro var definitions](#Haas)
15. [Why](#Why)

---


<a id="Usage"></a>

# Usage.

    

    Example of program with many options using docopt.
    
    Usage:
      p2g.py [options]  <srcfile> [<dstfile>] 
      p2g.py --help [<topic>]
    
        Example:
            p2g foo.py ~/_nc_/O{countdown}vc1-foo.nc
             Makes an output of the form ~/_nc_/O1234vc1-foo.nc
     
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
      
      <topic>     [ topics | all | <topic>]
              <topic>  Print from readme starting at topic.                 
              topics:  List all topics.
              all      Print all readme.
    
    Options:
         --job=<jobname>      Olabel for output code.
         --function=<fname>   Function to be compiled,
                               default is last one in source file.
         --break              pdb.set_trace() on error.
         --no-version         Don't put version number in outputs.
         --narrow             Emit comments on their own line,
                               makes text fit more easily into
                               a narrow program window.
         --verbose=<level>    Set verbosity level [default: 0]
         --version            Print version.
         --location           Print path of running executable.
         --examples=<dstdir>  Create <dstdir>, populate with
                                  examples and compile.
     
              Examples:
                p2g examples showme
                  Copies the examples into ./showme and then runs
                   p2g showme/vicecenter.py showme/vicecenter.nc
                   p2g showme/checkprobe.py showme/checkprobe.nc

---


<a id="Install"></a>

# Install:

    $ pip install p2g

---

---


<a id="Examples."></a>

# Examples.

for a show:

    $ p2g examples dstdir

---


<a id="SimpleDemo"></a>

## Simple demo.

    $ echo "

    import p2g
    def t():
      x = p2g.Var(99)
      for y in range(10):
        x += y

" | p2g  -

    ⇨ directly ⇨

    O0001 (t: 0.2.351)
      #100= 99.                       (   x = Var[99]                 )
      #102= 0.                        (   for y in range[10]:         )
    N1000
      IF [#102 GE 10.] GOTO 1002      (   for y in range[10]:         )
      #100= #100 + #102               ( x += y                        )
      #102= #102 + 1.
      GOTO 1000
    N1002
      M30
    %

---


<a id="NonTrivalDemo"></a>

## Non trivial demo:

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
            message(ALARM[0], f"too far {sch.name}.")
    
    
    def demo1():
        cursor = Var[3](2, 3, 4)
        # searching right, look down 0.4", move
        # 1.5" right if nothing hit.
        sch1 = SearchParams(name="right", search_depth=-0.4, iota=-0.1, delta=(1.5, 0))
        search(cursor, sch1)

⇨ `p2g demo1.py` ⇨

    O0001 (demo1: 0.2.350)
      #100= 2.                        (   cursor = Var[3][2, 3, 4]    )
      #101= 3.
      #102= 4.
      #103= 10.                       (   its = Var[sch.its]          )
    N1000
      IF [#103 LE 0.] GOTO 1002       (   while its > 0:              )
      G90 G01 F640. x#100 y#101 z#102 (       sch.go[cursor]          )
      G90 G31 F30. z-0.4              (       sch.probe[z=sch.search_depth])
      IF [#5063 LT -0.5] GOTO 1001    (       if SKIP_POS.z < sch.search_depth + sch.iota:)
      #100= #100 + 1.5                (       cursor.xy += sch.delta  )
      #103= #103 - 1.                 (       its -= 1                )
      GOTO 1000
    N1002
      #3000 = 101 (too far right.)
    N1001
      M30
    %

---


<a id="Variables"></a>

# Variables

-   Give names to macro variables at a known address:
    
    `Fixed` ❰ `[` *size* `]` ❱<sub>opt</sub> (`addr=` *addr* ❰ `,` *init* &#x2026; ❱<sub>opt</sub> `)`

-   Give names to macro variables automatically per function.
    
    `Var` ❰ `[` *size* `]` ❱<sub>opt</sub> (❰ `,` *init* &#x2026; ❱<sub>opt</sub> `)`

-   Not actually a variable, but same syntax.
    
    `Const` ❰ `[` *size* `]` ❱<sub>opt</sub> (❰ `,` *init* &#x2026; ❱<sub>opt</sub> `)`

Example:   

    
    from p2g import *  # this is the common header
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
        tmp0 = Var(skip0.xyz * 2.0 + workpos + skip1)
    
        com("Define a constant ")
        above_tdc = Const(111, 222, 1333)
    
        com("Use it ")
        tmp0 += above_tdc

⇨ `p2g var1.py` ⇨

    O0001 (ex2)
      #100= #5061 * 2. + #5041 + #5061( tmp0 = Var[ skip0.xyz * 2.0 + workpos + skip1])
      #101= #5062 * 2. + #5042 + #5062
      #102= #5063 * 2. + #5043 + #5063
    ( Define a constant  )
    ( Use it  )
      #100= #100 + 111.               ( tmp0 += above_tdc             )
      #101= #101 + 222.
      #102= #102 + 1333.
      M30
    %                                 ( 0.2.301                       )

---


<a id="Coordinates"></a>

# Coordinates.

Describe position, with axis by location, in sequence or by name.

    from p2g import *  # this is the common header
    from p2g.haas import *  # to all the examples
    
    
    def co1():
        com("Describe 3 variables at 3000")
        dst = Fixed[3](addr=3000)
        com("Fill with 1,2,3")
        dst.var = (1, 2, 3)
    
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

⇨ `p2g co1.py` ⇨

    O0001 (co1)
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
    %                                 ( 0.2.301                       )

---


<a id="Expressions"></a>

# Expressions

Python expressions turn into G-Code as you may expect, save that
native Python uses radians for trig, and G-Code uses degrees, so
folding is done in degrees.

    from p2g import *  # this is the common header
    from p2g.haas import *  # to all the examples
    
    
    def exp11():
        com("Variables go into macro variables.")
        theta = Var(0.3)
        angle = Var(sin(theta))
    
        com("Constants don't exist in G-code.")
        thetak = Const(0.3)
        anglek = Var(sin(thetak))
    
        com("Lots of things are folded.")
        t1 = Var(2 * thetak + 7)
    
        com("Simple array math:")
    
        box_size = Const([4, 4, 2])
        tlhc = Var(-box_size / 2)
        brhc = Var(box_size / 2)
        diff = Var(tlhc - brhc)
    
        a, b, x = Var(), Var(), Var()
        a = tlhc[0] / tlhc[1]
        b = tlhc[0] % tlhc[1]
        x = tlhc[0] & tlhc[1]
        tlhc.xy = ((a - b + 3) / sin(x), (a + b + 3) / cos(x))

⇨ `p2g exp1.py` ⇨

    O0001 (exp11)
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
    %                                 ( 0.2.301                       )

---


<a id="Axes"></a>

# Axes

Any number of axes are supported, default just being xy and z.

A rotary on ac can be set with p2g.axis.NAMES="xyza\*c".
The axis letters should be the same order as your machine expects
coordinates to turn up in work offset registers.

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

⇨ `p2g axes.py` ⇨

    O0001 (axes)
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
      #203= 180.                      (    p4.a = 180                 )
      #205= 30.                       (    p4.c = asin [0.5]          )
    ( Filling to number of axes. )
      #5241= 0.                       (    G55.var = [0]              )
      #5242= 0.
      #5243= 0.
      #100= #5241 * 34.               (    tmp = Var[G55 * 34]        )
      #101= #5242 * 34.
      #102= #5243 * 34.
      M30
    %                                 ( 0.2.301                       )

---


<a id="When"></a>

# When

'when' works as in python, save there are no exceptions;
useful for turning on probing and magically getting it turned
off,.  Or setting and restoring the wcs etc etc (look in p2g/lib.py)

    import p2g
    from p2g import haas
    
    PROBE = 1
    
    
    class Optional:
        prev: str
    
        def __init__(self):
            self.prev = p2g.stat.OPT_PREFIX
            p2g.stat.OPT_PREFIX = "/ "
    
        def __enter__(self):
            pass
    
        def __exit__(self, *_):
            p2g.stat.OPT_PREFIX = self.prev
    
    
    class Probe:
        def __enter__(self):
            p2g.load_tool(PROBE)
            p2g.codenl(haas.SPINDLE_PROBE_ON, comment_txt="Probe on.")
    
        def __exit__(self, *_):
            p2g.codenl(haas.SPINDLE_PROBE_OFF, comment_txt="Probe off.")
    
    
    def when_demo():
        with Probe():
            tmp = p2g.Var(9)
            with Optional():
                tmp.var += 98
            p2g.dprint(f"tmp is {tmp}")

⇨ `p2g whendemo.py` ⇨

    O0001 (when_demo : 0.2.333)
      T01 M06                         (     load_tool[PROBE]          )
      G65 P9832                       ( Probe on.                     )
      #100= 9.                        (  tmp = Var[9]                 )
    /   #100= #100 + 98.                (     tmp.var += 98             )
    DPRNT[tmp*is*[#100]]
      G65 P9833                       ( Probe off.                    )
      M30
    %

---


<a id="Goto"></a>

# Goto

Goto functions are constructed from parts, and make
building  blocks when partially applied.

`goto` ❰ `.`  *modifier* ❱\*  `(` *coordinates* `)`

*modifier* :

-   `r9810`
    Use Renishaw macro 9810 to do a protected positioning cycle.
-   `work`
    Use current work coordinate system. - whatever set with set\_wcs
-   `machine`
    Use the machine coordinate system - G53
-   `relative`
    Use relative coordinate system - G91
-   `absolute`
    Use absolute coordinate system - G90
-   `z_first`
    move Z axis first.
-   `z_last`
    move the other axes before the Z.
-   `probe`
    Emit probe code using G31.
-   `xyz`
    Move all axes at once.
-   `feed(` *expr* `)`
    Set feed rate.
-   `mcode(` *string* `)`
    Apply an mcode.

    from p2g import *
    
    
    def goto1():
        symbol.Table.print = True
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
        safe_goto = goto.feed(20).r9810
    
        safe_goto.z_first(1, 2, 3)

⇨ \`p2g goto1.py\` ⇨

    O0001 (goto1)
    ( Symbol Table )
    
     ( v1 :  #100.x  #101.y  #102.z )
    
    
    ( in work cosys, goto x=1, y=2, z=3 at 20ips )
      G90 G01 F20. x1. y2. z3.        ( g1 [1,2,3]                    )
    
    ( make a variable, 2,3,4 )
      #100= 2.                        ( v1 = Var[x=2,y=3,z=4]         )
      #101= 3.
      #102= 4.
    
    ( In the machine cosys, move to v1.z then v1.xy, slowly )
      G90 G53 G01 F10. z#102          ( absslow.z_first[v1]           )
      G90 G53 G01 F10. x#100 y#101
    
    ( p1 is whatever absslow was, with feed adjusted to 100. )
      G90 G53 G01 F100. x#100 y#101   ( p1.z_last[v1]                 )
      G90 G53 G01 F100. z#102
    
    ( p2 is whatever p1 was, with changed to a probe. )
      G90 G53 G31 F100. x#100 y#101   ( p2.z_last[v1]                 )
      G90 G53 G31 F100. z#102
    
    ( move a and c axes  )
      G91 G01 F20. a9. c90.           ( goto.feed[20].all.relative [a=9, c= 90])
    
    ( probe with a hass MUST_SKIP mcode. )
      G91 G31 M79 F10. x3. y4. z5.    ( goto.probe.feed[10].mcode["M79"].relative.all[3,4,5])
    
    ( Define shortcut for safe_goto and use. )
      G65 R9810 F20. z3.              ( safe_goto.z_first[1,2,3]      )
      G65 R9810 F20. x1. y2.
      M30
    %                                 ( 0.2.301                       )

---


<a id="Printing"></a>

# Printing

Turns Python f string prints into G-code DPRNT.  Make sure
that your print string does not have any characters in it that
your machine considers to be illegal in a DPRNT string.

    from p2g import *
    from p2g.haas import *
    
    
    def exprnt():
        x = Var(2)
        y = Var(27)
    
        for q in range(10):
            dprint(f"X is {x:3.1f}, Y+Q is {y+q:5.2f}")

⇨ `p2g exprnt.py` ⇨

    O0001 (exprnt : 0.2.333)
      #100= 2.                        (   x = Var[2]                  )
      #101= 27.                       (   y = Var[27]                 )
      #103= 0.                        (   for q in range[10]:         )
    N1000
      IF [#103 GE 10.] GOTO 1002      (   for q in range[10]:         )
    DPRNT[X*is*[#100][31],*Y+Q*is*[#101+#103][52]]
      #103= #103 + 1.                 ( dprint[f"X is {x:3.1f}, Y+Q is {y+q:5.2f}"])
      GOTO 1000
    N1002
      M30
    %

---


<a id="SymbolTables"></a>

# Symbol Tables.

Set the global `p2g.symbol.Table.print` to get a symbol
table in the output file.

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

⇨ \`p2g stest.py\` ⇨

    O0001 (stest)
    ( Symbol Table )
    
     ( MACHINE_ABS_ABOVE_OTS                   :  -7.000,  8.000,  9.000 )
     ( MACHINE_ABS_ABOVE_SEARCH_ROTARY_LHS_5X8 : 100.000,101.000,102.000 )
     ( MACHINE_ABS_ABOVE_VICE                  :  17.000, 18.000, 19.000 )
    
     ( RAW_ANALOG                              : #1080[10]               )
     ( v1                                      :  #106.x                 )
    
    
    ( Only used symbols are in output table. )
      #100= -7.                       ( Var[MACHINE_ABS_ABOVE_OTS]    )
      #101= 8.
      #102= 9.
      #103= 170.                      ( Var[MACHINE_ABS_ABOVE_VICE * fish])
      #104= 180.
      #105= 190.
      #106= #106 + #1087              ( v1 += RAW_ANALOG[7]           )
      M30
    %                                 ( 0.2.301                       )

---


<a id="Notes"></a>

# Notes

The entire thing is brittle; I've only used it to make code
for my own limited purposes. 

Nice things:

    
    from p2g import *
    from p2g.haas import *
    
    
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
        # I'm not recommending replacing
        # add with multiply, but it would work.
        def __add__(self, other):
            return self.val * other + 3
    
    
    def cool():
        com("You can do surprising things.")
    
        avariable = Var(100)
        objp = X(avariable, 34)
        another = Var(7, 8)
    
        objp.adjust(TOOL_OFFSET)
    
        q = Y(another) + (objp.thisone, objp.b)
        dprint(f"{q[0]}{q[1]}")

⇨ `p2g notes.py` ⇨

    O0001 (cool)
    ( You can do surprising things. )
      #100= 100.                      (   avariable = Var[100]        )
      #101= 7.                        (   another = Var[7,8]          )
      #102= 8.
    DPRNT[[#101*[#100+#5081]+3.][#102*[#5082+34.]+3.]]
      M30
    %                                 ( 0.2.301                       )

    import p2g
    from p2g.haas import *
    
    G55 = p2g.Fixed[3](addr=5241)
    
    def beware():
            p2g.com(
                "Names on the left hand side of an assignment need to be",
                "treated with care.  A simple.",
            )
            G55 = [0, 0, 0]
            p2g.com(
                "Will not do what you want - this will overwrite the definition",
                "of G55 above - so no code will be generated.",
            )
    
            p2g.com(
                "You need to use .var (for everything), explicitly name the axes,"
                "or use magic slicing."
            )
    
            G56.var = [1, 1, 1]
            G56.xyz = [2, 2, 2]
            G56[:] = [3, 3, 3]

⇨ `p2g beware.py` ⇨

    O0001 (beware)
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
    %                                 ( 0.2.301                       )

    from p2g import *
    from p2g.haas import *
    
    
    def beware1():
        com(
            "It's easy to forget that only macro variables will get into",
            "the output code. Other code will go away.",
        )
        x = 123  # not a var
        y = Var(7)
        if x == 23:  # look here
            y = 9
    
        com("Should look like:")
        x = Var(123)  # is a var
        y = Var(7)
        if x == 23:  # look here
            y = 9
        else:
            y = 99

    O0001 (beware1)
    ( It's easy to forget that only macro variables will get into )
    ( the output code. Other code will go away.                   )
      #100= 7.                        ( y = Var[7]                    )
    ( Should look like: )
      #101= 123.                      ( x = Var[123]  # is a var      )
      #102= 7.                        ( y = Var[7]                    )
      #100= #102
      IF [#101 NE 23.] GOTO 1002      ( if x == 23:  # look here      )
      #100= 9.                        (     y = 9                     )
      GOTO 1003
    N1002
      #100= 99.                       (     y = 99                    )
    N1003
      M30
    %

---


<a id="Haas"></a>

# HAAS macro var definitions

Names predefined in p2g.haas:

<table border="2" cellspacing="0" cellpadding="6" rules="groups" frame="hsides">


<colgroup>
<col  class="org-left" />

<col  class="org-left" />

<col  class="org-left" />
</colgroup>
<tbody>
<tr>
<td class="org-left"><code>Name</code></td>
<td class="org-left"><code>Size</code></td>
<td class="org-left"><code>Address</code></td>
</tr>


<tr>
<td class="org-left">---</td>
<td class="org-left">---</td>
<td class="org-left">---</td>
</tr>


<tr>
<td class="org-left"><code>NULL</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     #    0    </code></td>
</tr>


<tr>
<td class="org-left"><code>MACRO\_ARGUMENTS</code></td>
<td class="org-left"><code>   33</code></td>
<td class="org-left"><code>#    1 … #   33</code></td>
</tr>


<tr>
<td class="org-left"><code>GAP01</code></td>
<td class="org-left"><code>   66</code></td>
<td class="org-left"><code>#   34 … #   99</code></td>
</tr>


<tr>
<td class="org-left"><code>GP\_SAVED1</code></td>
<td class="org-left"><code>  100</code></td>
<td class="org-left"><code>#  100 … #  199</code></td>
</tr>


<tr>
<td class="org-left"><code>GAP02</code></td>
<td class="org-left"><code>  300</code></td>
<td class="org-left"><code>#  200 … #  499</code></td>
</tr>


<tr>
<td class="org-left"><code>GP\_SAVED2</code></td>
<td class="org-left"><code>   50</code></td>
<td class="org-left"><code>#  500 … #  549</code></td>
</tr>


<tr>
<td class="org-left"><code>PROBE\_CALIBRATION1</code></td>
<td class="org-left"><code>    6</code></td>
<td class="org-left"><code>#  550 … #  555</code></td>
</tr>


<tr>
<td class="org-left"><code>PROBE\_R</code></td>
<td class="org-left"><code>    3</code></td>
<td class="org-left"><code>#  556 … #  558</code></td>
</tr>


<tr>
<td class="org-left"><code>PROBE\_CALIBRATION2</code></td>
<td class="org-left"><code>   22</code></td>
<td class="org-left"><code>#  559 … #  580</code></td>
</tr>


<tr>
<td class="org-left"><code>GP\_SAVED3</code></td>
<td class="org-left"><code>  119</code></td>
<td class="org-left"><code>#  581 … #  699</code></td>
</tr>


<tr>
<td class="org-left"><code>GAP03</code></td>
<td class="org-left"><code>  100</code></td>
<td class="org-left"><code>#  700 … #  799</code></td>
</tr>


<tr>
<td class="org-left"><code>GP\_SAVED4</code></td>
<td class="org-left"><code>  200</code></td>
<td class="org-left"><code>#  800 … #  999</code></td>
</tr>


<tr>
<td class="org-left"><code>INPUTS</code></td>
<td class="org-left"><code>   64</code></td>
<td class="org-left"><code># 1000 … # 1063</code></td>
</tr>


<tr>
<td class="org-left"><code>MAX\_LOADS\_XYZAB</code></td>
<td class="org-left"><code>    5</code></td>
<td class="org-left"><code># 1064 … # 1068</code></td>
</tr>


<tr>
<td class="org-left"><code>GAP04</code></td>
<td class="org-left"><code>   11</code></td>
<td class="org-left"><code># 1069 … # 1079</code></td>
</tr>


<tr>
<td class="org-left"><code>RAW\_ANALOG</code></td>
<td class="org-left"><code>   10</code></td>
<td class="org-left"><code># 1080 … # 1089</code></td>
</tr>


<tr>
<td class="org-left"><code>FILTERED\_ANALOG</code></td>
<td class="org-left"><code>    8</code></td>
<td class="org-left"><code># 1090 … # 1097</code></td>
</tr>


<tr>
<td class="org-left"><code>SPINDLE\_LOAD</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 1098    </code></td>
</tr>


<tr>
<td class="org-left"><code>GAP05</code></td>
<td class="org-left"><code>  165</code></td>
<td class="org-left"><code># 1099 … # 1263</code></td>
</tr>


<tr>
<td class="org-left"><code>MAX\_LOADS\_CTUVW</code></td>
<td class="org-left"><code>    5</code></td>
<td class="org-left"><code># 1264 … # 1268</code></td>
</tr>


<tr>
<td class="org-left"><code>GAP06</code></td>
<td class="org-left"><code>  332</code></td>
<td class="org-left"><code># 1269 … # 1600</code></td>
</tr>


<tr>
<td class="org-left"><code>TOOL\_TBL\_FLUTES</code></td>
<td class="org-left"><code>  200</code></td>
<td class="org-left"><code># 1601 … # 1800</code></td>
</tr>


<tr>
<td class="org-left"><code>TOOL\_TBL\_VIBRATION</code></td>
<td class="org-left"><code>  200</code></td>
<td class="org-left"><code># 1801 … # 2000</code></td>
</tr>


<tr>
<td class="org-left"><code>TOOL\_TBL\_OFFSETS</code></td>
<td class="org-left"><code>  200</code></td>
<td class="org-left"><code># 2001 … # 2200</code></td>
</tr>


<tr>
<td class="org-left"><code>TOOL\_TBL\_WEAR</code></td>
<td class="org-left"><code>  200</code></td>
<td class="org-left"><code># 2201 … # 2400</code></td>
</tr>


<tr>
<td class="org-left"><code>TOOL\_TBL\_DROFFSET</code></td>
<td class="org-left"><code>  200</code></td>
<td class="org-left"><code># 2401 … # 2600</code></td>
</tr>


<tr>
<td class="org-left"><code>TOOL\_TBL\_DRWEAR</code></td>
<td class="org-left"><code>  200</code></td>
<td class="org-left"><code># 2601 … # 2800</code></td>
</tr>


<tr>
<td class="org-left"><code>GAP07</code></td>
<td class="org-left"><code>  199</code></td>
<td class="org-left"><code># 2801 … # 2999</code></td>
</tr>


<tr>
<td class="org-left"><code>ALARM</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 3000    </code></td>
</tr>


<tr>
<td class="org-left"><code>T\_MS</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 3001    </code></td>
</tr>


<tr>
<td class="org-left"><code>T\_HR</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 3002    </code></td>
</tr>


<tr>
<td class="org-left"><code>SINGLE\_BLOCK\_OFF</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 3003    </code></td>
</tr>


<tr>
<td class="org-left"><code>FEED\_HOLD\_OFF</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 3004    </code></td>
</tr>


<tr>
<td class="org-left"><code>GAP08</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 3005    </code></td>
</tr>


<tr>
<td class="org-left"><code>MESSAGE</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 3006    </code></td>
</tr>


<tr>
<td class="org-left"><code>GAP09</code></td>
<td class="org-left"><code>    4</code></td>
<td class="org-left"><code># 3007 … # 3010</code></td>
</tr>


<tr>
<td class="org-left"><code>YEAR\_MONTH\_DAY</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 3011    </code></td>
</tr>


<tr>
<td class="org-left"><code>HOUR\_MINUTE\_SECOND</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 3012    </code></td>
</tr>


<tr>
<td class="org-left"><code>GAP10</code></td>
<td class="org-left"><code>    7</code></td>
<td class="org-left"><code># 3013 … # 3019</code></td>
</tr>


<tr>
<td class="org-left"><code>POWER\_ON\_TIME</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 3020    </code></td>
</tr>


<tr>
<td class="org-left"><code>CYCLE\_START\_TIME</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 3021    </code></td>
</tr>


<tr>
<td class="org-left"><code>FEED\_TIMER</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 3022    </code></td>
</tr>


<tr>
<td class="org-left"><code>CUR\_PART\_TIMER</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 3023    </code></td>
</tr>


<tr>
<td class="org-left"><code>LAST\_COMPLETE\_PART\_TIMER</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 3024    </code></td>
</tr>


<tr>
<td class="org-left"><code>LAST\_PART\_TIMER</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 3025    </code></td>
</tr>


<tr>
<td class="org-left"><code>TOOL\_IN\_SPIDLE</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 3026    </code></td>
</tr>


<tr>
<td class="org-left"><code>SPINDLE\_RPM</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 3027    </code></td>
</tr>


<tr>
<td class="org-left"><code>PALLET\_LOADED</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 3028    </code></td>
</tr>


<tr>
<td class="org-left"><code>GAP11</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 3029    </code></td>
</tr>


<tr>
<td class="org-left"><code>SINGLE\_BLOCK</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 3030    </code></td>
</tr>


<tr>
<td class="org-left"><code>AGAP</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 3031    </code></td>
</tr>


<tr>
<td class="org-left"><code>BLOCK\_DELETE</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 3032    </code></td>
</tr>


<tr>
<td class="org-left"><code>OPT\_STOP</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 3033    </code></td>
</tr>


<tr>
<td class="org-left"><code>GAP12</code></td>
<td class="org-left"><code>  162</code></td>
<td class="org-left"><code># 3034 … # 3195</code></td>
</tr>


<tr>
<td class="org-left"><code>TIMER\_CELL\_SAFE</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 3196    </code></td>
</tr>


<tr>
<td class="org-left"><code>GAP13</code></td>
<td class="org-left"><code>    4</code></td>
<td class="org-left"><code># 3197 … # 3200</code></td>
</tr>


<tr>
<td class="org-left"><code>TOOL\_TBL\_DIAMETER</code></td>
<td class="org-left"><code>  200</code></td>
<td class="org-left"><code># 3201 … # 3400</code></td>
</tr>


<tr>
<td class="org-left"><code>TOOL\_TBL\_COOLANT\_POSITION</code></td>
<td class="org-left"><code>  200</code></td>
<td class="org-left"><code># 3401 … # 3600</code></td>
</tr>


<tr>
<td class="org-left"><code>GAP14</code></td>
<td class="org-left"><code>  300</code></td>
<td class="org-left"><code># 3601 … # 3900</code></td>
</tr>


<tr>
<td class="org-left"><code>M30\_COUNT1</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 3901    </code></td>
</tr>


<tr>
<td class="org-left"><code>M30\_COUNT2</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 3902    </code></td>
</tr>


<tr>
<td class="org-left"><code>GAP15</code></td>
<td class="org-left"><code>   98</code></td>
<td class="org-left"><code># 3903 … # 4000</code></td>
</tr>


<tr>
<td class="org-left"><code>LAST\_BLOCK\_G</code></td>
<td class="org-left"><code>   13</code></td>
<td class="org-left"><code># 4001 … # 4013</code></td>
</tr>


<tr>
<td class="org-left"><code>LAST\_WCS</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 4014    </code></td>
</tr>


<tr>
<td class="org-left"><code>GAP16</code></td>
<td class="org-left"><code>   79</code></td>
<td class="org-left"><code># 4022 … # 4100</code></td>
</tr>


<tr>
<td class="org-left"><code>LAST\_BLOCK\_ADDRESS</code></td>
<td class="org-left"><code>   26</code></td>
<td class="org-left"><code># 4101 … # 4126</code></td>
</tr>


<tr>
<td class="org-left"><code>GAP17</code></td>
<td class="org-left"><code>  874</code></td>
<td class="org-left"><code># 4127 … # 5000</code></td>
</tr>


<tr>
<td class="org-left"><code>LAST\_TARGET\_POS</code></td>
<td class="org-left"><code>naxes</code></td>
<td class="org-left"><code>    # 5001…    </code></td>
</tr>


<tr>
<td class="org-left"><code>MACHINE\_POS</code></td>
<td class="org-left"><code>naxes</code></td>
<td class="org-left"><code>    # 5021…    </code></td>
</tr>


<tr>
<td class="org-left"><code>MACHINE</code></td>
<td class="org-left"><code>naxes</code></td>
<td class="org-left"><code>    # 5021…    </code></td>
</tr>


<tr>
<td class="org-left"><code>G53</code></td>
<td class="org-left"><code>naxes</code></td>
<td class="org-left"><code>    # 5021…    </code></td>
</tr>


<tr>
<td class="org-left"><code>WORK\_POS</code></td>
<td class="org-left"><code>naxes</code></td>
<td class="org-left"><code>    # 5041…    </code></td>
</tr>


<tr>
<td class="org-left"><code>WORK</code></td>
<td class="org-left"><code>naxes</code></td>
<td class="org-left"><code>    # 5041…    </code></td>
</tr>


<tr>
<td class="org-left"><code>SKIP\_POS</code></td>
<td class="org-left"><code>naxes</code></td>
<td class="org-left"><code>    # 5061…    </code></td>
</tr>


<tr>
<td class="org-left"><code>PROBE</code></td>
<td class="org-left"><code>naxes</code></td>
<td class="org-left"><code>    # 5061…    </code></td>
</tr>


<tr>
<td class="org-left"><code>TOOL\_OFFSET</code></td>
<td class="org-left"><code>   20</code></td>
<td class="org-left"><code># 5081 … # 5100</code></td>
</tr>


<tr>
<td class="org-left"><code>GAP18</code></td>
<td class="org-left"><code>  100</code></td>
<td class="org-left"><code># 5101 … # 5200</code></td>
</tr>


<tr>
<td class="org-left"><code>G52</code></td>
<td class="org-left"><code>naxes</code></td>
<td class="org-left"><code>    # 5201…    </code></td>
</tr>


<tr>
<td class="org-left"><code>G54</code></td>
<td class="org-left"><code>naxes</code></td>
<td class="org-left"><code>    # 5221…    </code></td>
</tr>


<tr>
<td class="org-left"><code>G55</code></td>
<td class="org-left"><code>naxes</code></td>
<td class="org-left"><code>    # 5241…    </code></td>
</tr>


<tr>
<td class="org-left"><code>G56</code></td>
<td class="org-left"><code>naxes</code></td>
<td class="org-left"><code>    # 5261…    </code></td>
</tr>


<tr>
<td class="org-left"><code>G57</code></td>
<td class="org-left"><code>naxes</code></td>
<td class="org-left"><code>    # 5281…    </code></td>
</tr>


<tr>
<td class="org-left"><code>G58</code></td>
<td class="org-left"><code>naxes</code></td>
<td class="org-left"><code>    # 5301…    </code></td>
</tr>


<tr>
<td class="org-left"><code>G59</code></td>
<td class="org-left"><code>naxes</code></td>
<td class="org-left"><code>    # 5321…    </code></td>
</tr>


<tr>
<td class="org-left"><code>GAP19</code></td>
<td class="org-left"><code>   60</code></td>
<td class="org-left"><code># 5341 … # 5400</code></td>
</tr>


<tr>
<td class="org-left"><code>TOOL\_TBL\_FEED\_TIMERS</code></td>
<td class="org-left"><code>  100</code></td>
<td class="org-left"><code># 5401 … # 5500</code></td>
</tr>


<tr>
<td class="org-left"><code>TOOL\_TBL\_TOTAL\_TIMERS</code></td>
<td class="org-left"><code>  100</code></td>
<td class="org-left"><code># 5501 … # 5600</code></td>
</tr>


<tr>
<td class="org-left"><code>TOOL\_TBL\_LIFE\_LIMITS</code></td>
<td class="org-left"><code>  100</code></td>
<td class="org-left"><code># 5601 … # 5700</code></td>
</tr>


<tr>
<td class="org-left"><code>TOOL\_TBL\_LIFE\_COUNTERS</code></td>
<td class="org-left"><code>  100</code></td>
<td class="org-left"><code># 5701 … # 5800</code></td>
</tr>


<tr>
<td class="org-left"><code>TOOL\_TBL\_LIFE\_MAX\_LOADS</code></td>
<td class="org-left"><code>  100</code></td>
<td class="org-left"><code># 5801 … # 5900</code></td>
</tr>


<tr>
<td class="org-left"><code>TOOL\_TBL\_LIFE\_LOAD\_LIMITS</code></td>
<td class="org-left"><code>  100</code></td>
<td class="org-left"><code># 5901 … # 6000</code></td>
</tr>


<tr>
<td class="org-left"><code>GAP20</code></td>
<td class="org-left"><code>  197</code></td>
<td class="org-left"><code># 6001 … # 6197</code></td>
</tr>


<tr>
<td class="org-left"><code>NGC\_CF</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 6198    </code></td>
</tr>


<tr>
<td class="org-left"><code>GAP21</code></td>
<td class="org-left"><code>  802</code></td>
<td class="org-left"><code># 6199 … # 7000</code></td>
</tr>


<tr>
<td class="org-left"><code>G154\_P1</code></td>
<td class="org-left"><code>naxes</code></td>
<td class="org-left"><code>    # 7001…    </code></td>
</tr>


<tr>
<td class="org-left"><code>G154\_P2</code></td>
<td class="org-left"><code>naxes</code></td>
<td class="org-left"><code>    # 7021…    </code></td>
</tr>


<tr>
<td class="org-left"><code>G154\_P3</code></td>
<td class="org-left"><code>naxes</code></td>
<td class="org-left"><code>    # 7041…    </code></td>
</tr>


<tr>
<td class="org-left"><code>G154\_P4</code></td>
<td class="org-left"><code>naxes</code></td>
<td class="org-left"><code>    # 7061…    </code></td>
</tr>


<tr>
<td class="org-left"><code>G154\_P5</code></td>
<td class="org-left"><code>naxes</code></td>
<td class="org-left"><code>    # 7081…    </code></td>
</tr>


<tr>
<td class="org-left"><code>G154\_P6</code></td>
<td class="org-left"><code>naxes</code></td>
<td class="org-left"><code>    # 7101…    </code></td>
</tr>


<tr>
<td class="org-left"><code>G154\_P7</code></td>
<td class="org-left"><code>naxes</code></td>
<td class="org-left"><code>    # 7121…    </code></td>
</tr>


<tr>
<td class="org-left"><code>G154\_P8</code></td>
<td class="org-left"><code>naxes</code></td>
<td class="org-left"><code>    # 7141…    </code></td>
</tr>


<tr>
<td class="org-left"><code>G154\_P9</code></td>
<td class="org-left"><code>naxes</code></td>
<td class="org-left"><code>    # 7161…    </code></td>
</tr>


<tr>
<td class="org-left"><code>G154\_P10</code></td>
<td class="org-left"><code>naxes</code></td>
<td class="org-left"><code>    # 7181…    </code></td>
</tr>


<tr>
<td class="org-left"><code>G154\_P11</code></td>
<td class="org-left"><code>naxes</code></td>
<td class="org-left"><code>    # 7201…    </code></td>
</tr>


<tr>
<td class="org-left"><code>G154\_P12</code></td>
<td class="org-left"><code>naxes</code></td>
<td class="org-left"><code>    # 7221…    </code></td>
</tr>


<tr>
<td class="org-left"><code>G154\_P13</code></td>
<td class="org-left"><code>naxes</code></td>
<td class="org-left"><code>    # 7241…    </code></td>
</tr>


<tr>
<td class="org-left"><code>G154\_P14</code></td>
<td class="org-left"><code>naxes</code></td>
<td class="org-left"><code>    # 7261…    </code></td>
</tr>


<tr>
<td class="org-left"><code>G154\_P15</code></td>
<td class="org-left"><code>naxes</code></td>
<td class="org-left"><code>    # 7281…    </code></td>
</tr>


<tr>
<td class="org-left"><code>G154\_P16</code></td>
<td class="org-left"><code>naxes</code></td>
<td class="org-left"><code>    # 7301…    </code></td>
</tr>


<tr>
<td class="org-left"><code>G154\_P17</code></td>
<td class="org-left"><code>naxes</code></td>
<td class="org-left"><code>    # 7321…    </code></td>
</tr>


<tr>
<td class="org-left"><code>G154\_P18</code></td>
<td class="org-left"><code>naxes</code></td>
<td class="org-left"><code>    # 7341…    </code></td>
</tr>


<tr>
<td class="org-left"><code>G154\_P19</code></td>
<td class="org-left"><code>naxes</code></td>
<td class="org-left"><code>    # 7361…    </code></td>
</tr>


<tr>
<td class="org-left"><code>G154\_P20</code></td>
<td class="org-left"><code>naxes</code></td>
<td class="org-left"><code>    # 7381…    </code></td>
</tr>


<tr>
<td class="org-left"><code>GAP22</code></td>
<td class="org-left"><code>  100</code></td>
<td class="org-left"><code># 7401 … # 7500</code></td>
</tr>


<tr>
<td class="org-left"><code>PALLET\_PRIORITY</code></td>
<td class="org-left"><code>  100</code></td>
<td class="org-left"><code># 7501 … # 7600</code></td>
</tr>


<tr>
<td class="org-left"><code>PALLET\_STATUS</code></td>
<td class="org-left"><code>  100</code></td>
<td class="org-left"><code># 7601 … # 7700</code></td>
</tr>


<tr>
<td class="org-left"><code>PALLET\_PROGRAM</code></td>
<td class="org-left"><code>  100</code></td>
<td class="org-left"><code># 7701 … # 7800</code></td>
</tr>


<tr>
<td class="org-left"><code>PALLET\_USAGE</code></td>
<td class="org-left"><code>  100</code></td>
<td class="org-left"><code># 7801 … # 7900</code></td>
</tr>


<tr>
<td class="org-left"><code>GAP23</code></td>
<td class="org-left"><code>  599</code></td>
<td class="org-left"><code># 7901 … # 8499</code></td>
</tr>


<tr>
<td class="org-left"><code>ATM\_ID</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 8500    </code></td>
</tr>


<tr>
<td class="org-left"><code>ATM\_PERCENT</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 8501    </code></td>
</tr>


<tr>
<td class="org-left"><code>ATM\_TOTAL\_AVL\_USAGE</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 8502    </code></td>
</tr>


<tr>
<td class="org-left"><code>ATM\_TOTAL\_AVL\_HOLE\_COUNT</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 8503    </code></td>
</tr>


<tr>
<td class="org-left"><code>ATM\_TOTAL\_AVL\_FEED\_TIME</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 8504    </code></td>
</tr>


<tr>
<td class="org-left"><code>ATM\_TOTAL\_AVL\_TOTAL\_TIME</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 8505    </code></td>
</tr>


<tr>
<td class="org-left"><code>GAP24</code></td>
<td class="org-left"><code>    4</code></td>
<td class="org-left"><code># 8506 … # 8509</code></td>
</tr>


<tr>
<td class="org-left"><code>ATM\_NEXT\_TOOL\_NUMBER</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 8510    </code></td>
</tr>


<tr>
<td class="org-left"><code>ATM\_NEXT\_TOOL\_LIFE</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 8511    </code></td>
</tr>


<tr>
<td class="org-left"><code>ATM\_NEXT\_TOOL\_AVL\_USAGE</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 8512    </code></td>
</tr>


<tr>
<td class="org-left"><code>ATM\_NEXT\_TOOL\_HOLE\_COUNT</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 8513    </code></td>
</tr>


<tr>
<td class="org-left"><code>ATM\_NEXT\_TOOL\_FEED\_TIME</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 8514    </code></td>
</tr>


<tr>
<td class="org-left"><code>ATM\_NEXT\_TOOL\_TOTAL\_TIME</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 8515    </code></td>
</tr>


<tr>
<td class="org-left"><code>GAP25</code></td>
<td class="org-left"><code>   34</code></td>
<td class="org-left"><code># 8516 … # 8549</code></td>
</tr>


<tr>
<td class="org-left"><code>TOOL\_ID</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 8550    </code></td>
</tr>


<tr>
<td class="org-left"><code>TOOL\_FLUTES</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 8551    </code></td>
</tr>


<tr>
<td class="org-left"><code>TOOL\_MAX\_VIBRATION</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 8552    </code></td>
</tr>


<tr>
<td class="org-left"><code>TOOL\_LENGTH\_OFFSETS</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 8553    </code></td>
</tr>


<tr>
<td class="org-left"><code>TOOL\_LENGTH\_WEAR</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 8554    </code></td>
</tr>


<tr>
<td class="org-left"><code>TOOL\_DIAMETER\_OFFSETS</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 8555    </code></td>
</tr>


<tr>
<td class="org-left"><code>TOOL\_DIAMETER\_WEAR</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 8556    </code></td>
</tr>


<tr>
<td class="org-left"><code>TOOL\_ACTUAL\_DIAMETER</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 8557    </code></td>
</tr>


<tr>
<td class="org-left"><code>TOOL\_COOLANT\_POSITION</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 8558    </code></td>
</tr>


<tr>
<td class="org-left"><code>TOOL\_FEED\_TIMER</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 8559    </code></td>
</tr>


<tr>
<td class="org-left"><code>TOOL\_TOTAL\_TIMER</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 8560    </code></td>
</tr>


<tr>
<td class="org-left"><code>TOOL\_LIFE\_LIMIT</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 8561    </code></td>
</tr>


<tr>
<td class="org-left"><code>TOOL\_LIFE\_COUNTER</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 8562    </code></td>
</tr>


<tr>
<td class="org-left"><code>TOOL\_LIFE\_MAX\_LOAD</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 8563    </code></td>
</tr>


<tr>
<td class="org-left"><code>TOOL\_LIFE\_LOAD\_LIMIT</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 8564    </code></td>
</tr>


<tr>
<td class="org-left"><code>GAP26</code></td>
<td class="org-left"><code>  435</code></td>
<td class="org-left"><code># 8565 … # 8999</code></td>
</tr>


<tr>
<td class="org-left"><code>THERMAL\_COMP\_ACC</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 9000    </code></td>
</tr>


<tr>
<td class="org-left"><code>GAP27</code></td>
<td class="org-left"><code>   15</code></td>
<td class="org-left"><code># 9001 … # 9015</code></td>
</tr>


<tr>
<td class="org-left"><code>THERMAL\_SPINDLE\_COMP\_ACC</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 9016    </code></td>
</tr>


<tr>
<td class="org-left"><code>GAP28</code></td>
<td class="org-left"><code>  983</code></td>
<td class="org-left"><code># 9017 … # 9999</code></td>
</tr>


<tr>
<td class="org-left"><code>GVARIABLES3</code></td>
<td class="org-left"><code> 1000</code></td>
<td class="org-left"><code>#10000 … #10999</code></td>
</tr>


<tr>
<td class="org-left"><code>INPUTS1</code></td>
<td class="org-left"><code>  256</code></td>
<td class="org-left"><code>#11000 … #11255</code></td>
</tr>


<tr>
<td class="org-left"><code>GAP29</code></td>
<td class="org-left"><code>  744</code></td>
<td class="org-left"><code>#11256 … #11999</code></td>
</tr>


<tr>
<td class="org-left"><code>OUTPUT1</code></td>
<td class="org-left"><code>  256</code></td>
<td class="org-left"><code>#12000 … #12255</code></td>
</tr>


<tr>
<td class="org-left"><code>GAP30</code></td>
<td class="org-left"><code>  744</code></td>
<td class="org-left"><code>#12256 … #12999</code></td>
</tr>


<tr>
<td class="org-left"><code>FILTERED\_ANALOG1</code></td>
<td class="org-left"><code>   13</code></td>
<td class="org-left"><code>#13000 … #13012</code></td>
</tr>


<tr>
<td class="org-left"><code>COOLANT\_LEVEL</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     #13013    </code></td>
</tr>


<tr>
<td class="org-left"><code>FILTERED\_ANALOG2</code></td>
<td class="org-left"><code>   50</code></td>
<td class="org-left"><code>#13014 … #13063</code></td>
</tr>


<tr>
<td class="org-left"><code>GAP31</code></td>
<td class="org-left"><code>  936</code></td>
<td class="org-left"><code>#13064 … #13999</code></td>
</tr>


<tr>
<td class="org-left"><code>SETTING</code></td>
<td class="org-left"><code>10000</code></td>
<td class="org-left"><code>#20000 … #29999</code></td>
</tr>


<tr>
<td class="org-left"><code>PARAMETER</code></td>
<td class="org-left"><code>10000</code></td>
<td class="org-left"><code>#30000 … #39999</code></td>
</tr>


<tr>
<td class="org-left"><code>TOOL\_TYP</code></td>
<td class="org-left"><code>  200</code></td>
<td class="org-left"><code>#50001 … #50200</code></td>
</tr>


<tr>
<td class="org-left"><code>TOOL\_MATERIAL</code></td>
<td class="org-left"><code>  200</code></td>
<td class="org-left"><code>#50201 … #50400</code></td>
</tr>


<tr>
<td class="org-left"><code>GAP32</code></td>
<td class="org-left"><code>50600</code></td>
<td class="org-left"><code>#50401 … #101000</code></td>
</tr>


<tr>
<td class="org-left"><code>CURRENT\_OFFSET</code></td>
<td class="org-left"><code>  200</code></td>
<td class="org-left"><code>#50601 … #50800</code></td>
</tr>


<tr>
<td class="org-left"><code>CURRENT\_OFFSET2</code></td>
<td class="org-left"><code>  200</code></td>
<td class="org-left"><code>#50801 … #51000</code></td>
</tr>


<tr>
<td class="org-left"><code>GAP32</code></td>
<td class="org-left"><code>51300</code></td>
<td class="org-left"><code>#51001 … #102300</code></td>
</tr>


<tr>
<td class="org-left"><code>VPS\_TEMPLATE\_OFFSET</code></td>
<td class="org-left"><code>  100</code></td>
<td class="org-left"><code>#51301 … #51400</code></td>
</tr>


<tr>
<td class="org-left"><code>WORK\_MATERIAL</code></td>
<td class="org-left"><code>  200</code></td>
<td class="org-left"><code>#51401 … #51600</code></td>
</tr>


<tr>
<td class="org-left"><code>VPS\_FEEDRATE</code></td>
<td class="org-left"><code>  200</code></td>
<td class="org-left"><code>#51601 … #51800</code></td>
</tr>


<tr>
<td class="org-left"><code>APPROX\_LENGTH</code></td>
<td class="org-left"><code>  200</code></td>
<td class="org-left"><code>#51801 … #52000</code></td>
</tr>


<tr>
<td class="org-left"><code>APPROX\_DIAMETER</code></td>
<td class="org-left"><code>  200</code></td>
<td class="org-left"><code>#52001 … #52200</code></td>
</tr>


<tr>
<td class="org-left"><code>EDGE\_MEASURE\_HEIGHT</code></td>
<td class="org-left"><code>  200</code></td>
<td class="org-left"><code>#52201 … #52400</code></td>
</tr>


<tr>
<td class="org-left"><code>TOOL\_TOLERANCE</code></td>
<td class="org-left"><code>  200</code></td>
<td class="org-left"><code>#52401 … #52600</code></td>
</tr>


<tr>
<td class="org-left"><code>PROBE\_TYPE</code></td>
<td class="org-left"><code>  200</code></td>
<td class="org-left"><code>#52601 … #52800</code></td>
</tr>
</tbody>
</table>

x

<table border="2" cellspacing="0" cellpadding="6" rules="groups" frame="hsides">


<colgroup>
<col  class="org-left" />

<col  class="org-left" />

<col  class="org-left" />
</colgroup>
<tbody>
<tr>
<td class="org-left"><code>Name</code></td>
<td class="org-left"><code>Size</code></td>
<td class="org-left"><code>Address</code></td>
</tr>


<tr>
<td class="org-left">---</td>
<td class="org-left">---</td>
<td class="org-left">---</td>
</tr>


<tr>
<td class="org-left"><code>NULL</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     #    0    </code></td>
</tr>


<tr>
<td class="org-left"><code>MACRO\_ARGUMENTS</code></td>
<td class="org-left"><code>   33</code></td>
<td class="org-left"><code>#    1 … #   33</code></td>
</tr>


<tr>
<td class="org-left"><code>GAP01</code></td>
<td class="org-left"><code>   66</code></td>
<td class="org-left"><code>#   34 … #   99</code></td>
</tr>


<tr>
<td class="org-left"><code>GP\_SAVED1</code></td>
<td class="org-left"><code>  100</code></td>
<td class="org-left"><code>#  100 … #  199</code></td>
</tr>


<tr>
<td class="org-left"><code>GAP02</code></td>
<td class="org-left"><code>  300</code></td>
<td class="org-left"><code>#  200 … #  499</code></td>
</tr>


<tr>
<td class="org-left"><code>GP\_SAVED2</code></td>
<td class="org-left"><code>   50</code></td>
<td class="org-left"><code>#  500 … #  549</code></td>
</tr>


<tr>
<td class="org-left"><code>PROBE\_CALIBRATION1</code></td>
<td class="org-left"><code>    6</code></td>
<td class="org-left"><code>#  550 … #  555</code></td>
</tr>


<tr>
<td class="org-left"><code>PROBE\_R</code></td>
<td class="org-left"><code>    3</code></td>
<td class="org-left"><code>#  556 … #  558</code></td>
</tr>


<tr>
<td class="org-left"><code>PROBE\_CALIBRATION2</code></td>
<td class="org-left"><code>   22</code></td>
<td class="org-left"><code>#  559 … #  580</code></td>
</tr>


<tr>
<td class="org-left"><code>GP\_SAVED3</code></td>
<td class="org-left"><code>  119</code></td>
<td class="org-left"><code>#  581 … #  699</code></td>
</tr>


<tr>
<td class="org-left"><code>GAP03</code></td>
<td class="org-left"><code>  100</code></td>
<td class="org-left"><code>#  700 … #  799</code></td>
</tr>


<tr>
<td class="org-left"><code>GP\_SAVED4</code></td>
<td class="org-left"><code>  200</code></td>
<td class="org-left"><code>#  800 … #  999</code></td>
</tr>


<tr>
<td class="org-left"><code>INPUTS</code></td>
<td class="org-left"><code>   64</code></td>
<td class="org-left"><code># 1000 … # 1063</code></td>
</tr>


<tr>
<td class="org-left"><code>MAX\_LOADS\_XYZAB</code></td>
<td class="org-left"><code>    5</code></td>
<td class="org-left"><code># 1064 … # 1068</code></td>
</tr>


<tr>
<td class="org-left"><code>GAP04</code></td>
<td class="org-left"><code>   11</code></td>
<td class="org-left"><code># 1069 … # 1079</code></td>
</tr>


<tr>
<td class="org-left"><code>RAW\_ANALOG</code></td>
<td class="org-left"><code>   10</code></td>
<td class="org-left"><code># 1080 … # 1089</code></td>
</tr>


<tr>
<td class="org-left"><code>FILTERED\_ANALOG</code></td>
<td class="org-left"><code>    8</code></td>
<td class="org-left"><code># 1090 … # 1097</code></td>
</tr>


<tr>
<td class="org-left"><code>SPINDLE\_LOAD</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 1098    </code></td>
</tr>


<tr>
<td class="org-left"><code>GAP05</code></td>
<td class="org-left"><code>  165</code></td>
<td class="org-left"><code># 1099 … # 1263</code></td>
</tr>


<tr>
<td class="org-left"><code>MAX\_LOADS\_CTUVW</code></td>
<td class="org-left"><code>    5</code></td>
<td class="org-left"><code># 1264 … # 1268</code></td>
</tr>


<tr>
<td class="org-left"><code>GAP06</code></td>
<td class="org-left"><code>  332</code></td>
<td class="org-left"><code># 1269 … # 1600</code></td>
</tr>


<tr>
<td class="org-left"><code>TOOL\_TBL\_FLUTES</code></td>
<td class="org-left"><code>  200</code></td>
<td class="org-left"><code># 1601 … # 1800</code></td>
</tr>


<tr>
<td class="org-left"><code>TOOL\_TBL\_VIBRATION</code></td>
<td class="org-left"><code>  200</code></td>
<td class="org-left"><code># 1801 … # 2000</code></td>
</tr>


<tr>
<td class="org-left"><code>TOOL\_TBL\_OFFSETS</code></td>
<td class="org-left"><code>  200</code></td>
<td class="org-left"><code># 2001 … # 2200</code></td>
</tr>


<tr>
<td class="org-left"><code>TOOL\_TBL\_WEAR</code></td>
<td class="org-left"><code>  200</code></td>
<td class="org-left"><code># 2201 … # 2400</code></td>
</tr>


<tr>
<td class="org-left"><code>TOOL\_TBL\_DROFFSET</code></td>
<td class="org-left"><code>  200</code></td>
<td class="org-left"><code># 2401 … # 2600</code></td>
</tr>


<tr>
<td class="org-left"><code>TOOL\_TBL\_DRWEAR</code></td>
<td class="org-left"><code>  200</code></td>
<td class="org-left"><code># 2601 … # 2800</code></td>
</tr>


<tr>
<td class="org-left"><code>GAP07</code></td>
<td class="org-left"><code>  199</code></td>
<td class="org-left"><code># 2801 … # 2999</code></td>
</tr>


<tr>
<td class="org-left"><code>ALARM</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 3000    </code></td>
</tr>


<tr>
<td class="org-left"><code>T\_MS</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 3001    </code></td>
</tr>


<tr>
<td class="org-left"><code>T\_HR</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 3002    </code></td>
</tr>


<tr>
<td class="org-left"><code>SINGLE\_BLOCK\_OFF</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 3003    </code></td>
</tr>


<tr>
<td class="org-left"><code>FEED\_HOLD\_OFF</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 3004    </code></td>
</tr>


<tr>
<td class="org-left"><code>GAP08</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 3005    </code></td>
</tr>


<tr>
<td class="org-left"><code>MESSAGE</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 3006    </code></td>
</tr>


<tr>
<td class="org-left"><code>GAP09</code></td>
<td class="org-left"><code>    4</code></td>
<td class="org-left"><code># 3007 … # 3010</code></td>
</tr>


<tr>
<td class="org-left"><code>YEAR\_MONTH\_DAY</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 3011    </code></td>
</tr>


<tr>
<td class="org-left"><code>HOUR\_MINUTE\_SECOND</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 3012    </code></td>
</tr>


<tr>
<td class="org-left"><code>GAP10</code></td>
<td class="org-left"><code>    7</code></td>
<td class="org-left"><code># 3013 … # 3019</code></td>
</tr>


<tr>
<td class="org-left"><code>POWER\_ON\_TIME</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 3020    </code></td>
</tr>


<tr>
<td class="org-left"><code>CYCLE\_START\_TIME</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 3021    </code></td>
</tr>


<tr>
<td class="org-left"><code>FEED\_TIMER</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 3022    </code></td>
</tr>


<tr>
<td class="org-left"><code>CUR\_PART\_TIMER</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 3023    </code></td>
</tr>


<tr>
<td class="org-left"><code>LAST\_COMPLETE\_PART\_TIMER</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 3024    </code></td>
</tr>


<tr>
<td class="org-left"><code>LAST\_PART\_TIMER</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 3025    </code></td>
</tr>


<tr>
<td class="org-left"><code>TOOL\_IN\_SPIDLE</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 3026    </code></td>
</tr>


<tr>
<td class="org-left"><code>SPINDLE\_RPM</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 3027    </code></td>
</tr>


<tr>
<td class="org-left"><code>PALLET\_LOADED</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 3028    </code></td>
</tr>


<tr>
<td class="org-left"><code>GAP11</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 3029    </code></td>
</tr>


<tr>
<td class="org-left"><code>SINGLE\_BLOCK</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 3030    </code></td>
</tr>


<tr>
<td class="org-left"><code>AGAP</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 3031    </code></td>
</tr>


<tr>
<td class="org-left"><code>BLOCK\_DELETE</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 3032    </code></td>
</tr>


<tr>
<td class="org-left"><code>OPT\_STOP</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 3033    </code></td>
</tr>


<tr>
<td class="org-left"><code>GAP12</code></td>
<td class="org-left"><code>  162</code></td>
<td class="org-left"><code># 3034 … # 3195</code></td>
</tr>


<tr>
<td class="org-left"><code>TIMER\_CELL\_SAFE</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 3196    </code></td>
</tr>


<tr>
<td class="org-left"><code>GAP13</code></td>
<td class="org-left"><code>    4</code></td>
<td class="org-left"><code># 3197 … # 3200</code></td>
</tr>


<tr>
<td class="org-left"><code>TOOL\_TBL\_DIAMETER</code></td>
<td class="org-left"><code>  200</code></td>
<td class="org-left"><code># 3201 … # 3400</code></td>
</tr>


<tr>
<td class="org-left"><code>TOOL\_TBL\_COOLANT\_POSITION</code></td>
<td class="org-left"><code>  200</code></td>
<td class="org-left"><code># 3401 … # 3600</code></td>
</tr>


<tr>
<td class="org-left"><code>GAP14</code></td>
<td class="org-left"><code>  300</code></td>
<td class="org-left"><code># 3601 … # 3900</code></td>
</tr>


<tr>
<td class="org-left"><code>M30\_COUNT1</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 3901    </code></td>
</tr>


<tr>
<td class="org-left"><code>M30\_COUNT2</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 3902    </code></td>
</tr>


<tr>
<td class="org-left"><code>GAP15</code></td>
<td class="org-left"><code>   98</code></td>
<td class="org-left"><code># 3903 … # 4000</code></td>
</tr>


<tr>
<td class="org-left"><code>LAST\_BLOCK\_G</code></td>
<td class="org-left"><code>   13</code></td>
<td class="org-left"><code># 4001 … # 4013</code></td>
</tr>


<tr>
<td class="org-left"><code>LAST\_WCS</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 4014    </code></td>
</tr>


<tr>
<td class="org-left"><code>GAP16</code></td>
<td class="org-left"><code>   79</code></td>
<td class="org-left"><code># 4022 … # 4100</code></td>
</tr>


<tr>
<td class="org-left"><code>LAST\_BLOCK\_ADDRESS</code></td>
<td class="org-left"><code>   26</code></td>
<td class="org-left"><code># 4101 … # 4126</code></td>
</tr>


<tr>
<td class="org-left"><code>GAP17</code></td>
<td class="org-left"><code>  874</code></td>
<td class="org-left"><code># 4127 … # 5000</code></td>
</tr>


<tr>
<td class="org-left"><code>LAST\_TARGET\_POS</code></td>
<td class="org-left"><code>naxes</code></td>
<td class="org-left"><code>    # 5001…    </code></td>
</tr>


<tr>
<td class="org-left"><code>MACHINE\_POS</code></td>
<td class="org-left"><code>naxes</code></td>
<td class="org-left"><code>    # 5021…    </code></td>
</tr>


<tr>
<td class="org-left"><code>MACHINE</code></td>
<td class="org-left"><code>naxes</code></td>
<td class="org-left"><code>    # 5021…    </code></td>
</tr>


<tr>
<td class="org-left"><code>G53</code></td>
<td class="org-left"><code>naxes</code></td>
<td class="org-left"><code>    # 5021…    </code></td>
</tr>


<tr>
<td class="org-left"><code>WORK\_POS</code></td>
<td class="org-left"><code>naxes</code></td>
<td class="org-left"><code>    # 5041…    </code></td>
</tr>


<tr>
<td class="org-left"><code>WORK</code></td>
<td class="org-left"><code>naxes</code></td>
<td class="org-left"><code>    # 5041…    </code></td>
</tr>


<tr>
<td class="org-left"><code>SKIP\_POS</code></td>
<td class="org-left"><code>naxes</code></td>
<td class="org-left"><code>    # 5061…    </code></td>
</tr>


<tr>
<td class="org-left"><code>PROBE</code></td>
<td class="org-left"><code>naxes</code></td>
<td class="org-left"><code>    # 5061…    </code></td>
</tr>


<tr>
<td class="org-left"><code>TOOL\_OFFSET</code></td>
<td class="org-left"><code>   20</code></td>
<td class="org-left"><code># 5081 … # 5100</code></td>
</tr>


<tr>
<td class="org-left"><code>GAP18</code></td>
<td class="org-left"><code>  100</code></td>
<td class="org-left"><code># 5101 … # 5200</code></td>
</tr>


<tr>
<td class="org-left"><code>G52</code></td>
<td class="org-left"><code>naxes</code></td>
<td class="org-left"><code>    # 5201…    </code></td>
</tr>


<tr>
<td class="org-left"><code>G54</code></td>
<td class="org-left"><code>naxes</code></td>
<td class="org-left"><code>    # 5221…    </code></td>
</tr>


<tr>
<td class="org-left"><code>G55</code></td>
<td class="org-left"><code>naxes</code></td>
<td class="org-left"><code>    # 5241…    </code></td>
</tr>


<tr>
<td class="org-left"><code>G56</code></td>
<td class="org-left"><code>naxes</code></td>
<td class="org-left"><code>    # 5261…    </code></td>
</tr>


<tr>
<td class="org-left"><code>G57</code></td>
<td class="org-left"><code>naxes</code></td>
<td class="org-left"><code>    # 5281…    </code></td>
</tr>


<tr>
<td class="org-left"><code>G58</code></td>
<td class="org-left"><code>naxes</code></td>
<td class="org-left"><code>    # 5301…    </code></td>
</tr>


<tr>
<td class="org-left"><code>G59</code></td>
<td class="org-left"><code>naxes</code></td>
<td class="org-left"><code>    # 5321…    </code></td>
</tr>


<tr>
<td class="org-left"><code>GAP19</code></td>
<td class="org-left"><code>   60</code></td>
<td class="org-left"><code># 5341 … # 5400</code></td>
</tr>


<tr>
<td class="org-left"><code>TOOL\_TBL\_FEED\_TIMERS</code></td>
<td class="org-left"><code>  100</code></td>
<td class="org-left"><code># 5401 … # 5500</code></td>
</tr>


<tr>
<td class="org-left"><code>TOOL\_TBL\_TOTAL\_TIMERS</code></td>
<td class="org-left"><code>  100</code></td>
<td class="org-left"><code># 5501 … # 5600</code></td>
</tr>


<tr>
<td class="org-left"><code>TOOL\_TBL\_LIFE\_LIMITS</code></td>
<td class="org-left"><code>  100</code></td>
<td class="org-left"><code># 5601 … # 5700</code></td>
</tr>


<tr>
<td class="org-left"><code>TOOL\_TBL\_LIFE\_COUNTERS</code></td>
<td class="org-left"><code>  100</code></td>
<td class="org-left"><code># 5701 … # 5800</code></td>
</tr>


<tr>
<td class="org-left"><code>TOOL\_TBL\_LIFE\_MAX\_LOADS</code></td>
<td class="org-left"><code>  100</code></td>
<td class="org-left"><code># 5801 … # 5900</code></td>
</tr>


<tr>
<td class="org-left"><code>TOOL\_TBL\_LIFE\_LOAD\_LIMITS</code></td>
<td class="org-left"><code>  100</code></td>
<td class="org-left"><code># 5901 … # 6000</code></td>
</tr>


<tr>
<td class="org-left"><code>GAP20</code></td>
<td class="org-left"><code>  197</code></td>
<td class="org-left"><code># 6001 … # 6197</code></td>
</tr>


<tr>
<td class="org-left"><code>NGC\_CF</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 6198    </code></td>
</tr>


<tr>
<td class="org-left"><code>GAP21</code></td>
<td class="org-left"><code>  802</code></td>
<td class="org-left"><code># 6199 … # 7000</code></td>
</tr>


<tr>
<td class="org-left"><code>G154\_P1</code></td>
<td class="org-left"><code>naxes</code></td>
<td class="org-left"><code>    # 7001…    </code></td>
</tr>


<tr>
<td class="org-left"><code>G154\_P2</code></td>
<td class="org-left"><code>naxes</code></td>
<td class="org-left"><code>    # 7021…    </code></td>
</tr>


<tr>
<td class="org-left"><code>G154\_P3</code></td>
<td class="org-left"><code>naxes</code></td>
<td class="org-left"><code>    # 7041…    </code></td>
</tr>


<tr>
<td class="org-left"><code>G154\_P4</code></td>
<td class="org-left"><code>naxes</code></td>
<td class="org-left"><code>    # 7061…    </code></td>
</tr>


<tr>
<td class="org-left"><code>G154\_P5</code></td>
<td class="org-left"><code>naxes</code></td>
<td class="org-left"><code>    # 7081…    </code></td>
</tr>


<tr>
<td class="org-left"><code>G154\_P6</code></td>
<td class="org-left"><code>naxes</code></td>
<td class="org-left"><code>    # 7101…    </code></td>
</tr>


<tr>
<td class="org-left"><code>G154\_P7</code></td>
<td class="org-left"><code>naxes</code></td>
<td class="org-left"><code>    # 7121…    </code></td>
</tr>


<tr>
<td class="org-left"><code>G154\_P8</code></td>
<td class="org-left"><code>naxes</code></td>
<td class="org-left"><code>    # 7141…    </code></td>
</tr>


<tr>
<td class="org-left"><code>G154\_P9</code></td>
<td class="org-left"><code>naxes</code></td>
<td class="org-left"><code>    # 7161…    </code></td>
</tr>


<tr>
<td class="org-left"><code>G154\_P10</code></td>
<td class="org-left"><code>naxes</code></td>
<td class="org-left"><code>    # 7181…    </code></td>
</tr>


<tr>
<td class="org-left"><code>G154\_P11</code></td>
<td class="org-left"><code>naxes</code></td>
<td class="org-left"><code>    # 7201…    </code></td>
</tr>


<tr>
<td class="org-left"><code>G154\_P12</code></td>
<td class="org-left"><code>naxes</code></td>
<td class="org-left"><code>    # 7221…    </code></td>
</tr>


<tr>
<td class="org-left"><code>G154\_P13</code></td>
<td class="org-left"><code>naxes</code></td>
<td class="org-left"><code>    # 7241…    </code></td>
</tr>


<tr>
<td class="org-left"><code>G154\_P14</code></td>
<td class="org-left"><code>naxes</code></td>
<td class="org-left"><code>    # 7261…    </code></td>
</tr>


<tr>
<td class="org-left"><code>G154\_P15</code></td>
<td class="org-left"><code>naxes</code></td>
<td class="org-left"><code>    # 7281…    </code></td>
</tr>


<tr>
<td class="org-left"><code>G154\_P16</code></td>
<td class="org-left"><code>naxes</code></td>
<td class="org-left"><code>    # 7301…    </code></td>
</tr>


<tr>
<td class="org-left"><code>G154\_P17</code></td>
<td class="org-left"><code>naxes</code></td>
<td class="org-left"><code>    # 7321…    </code></td>
</tr>


<tr>
<td class="org-left"><code>G154\_P18</code></td>
<td class="org-left"><code>naxes</code></td>
<td class="org-left"><code>    # 7341…    </code></td>
</tr>


<tr>
<td class="org-left"><code>G154\_P19</code></td>
<td class="org-left"><code>naxes</code></td>
<td class="org-left"><code>    # 7361…    </code></td>
</tr>


<tr>
<td class="org-left"><code>G154\_P20</code></td>
<td class="org-left"><code>naxes</code></td>
<td class="org-left"><code>    # 7381…    </code></td>
</tr>


<tr>
<td class="org-left"><code>GAP22</code></td>
<td class="org-left"><code>  100</code></td>
<td class="org-left"><code># 7401 … # 7500</code></td>
</tr>


<tr>
<td class="org-left"><code>PALLET\_PRIORITY</code></td>
<td class="org-left"><code>  100</code></td>
<td class="org-left"><code># 7501 … # 7600</code></td>
</tr>


<tr>
<td class="org-left"><code>PALLET\_STATUS</code></td>
<td class="org-left"><code>  100</code></td>
<td class="org-left"><code># 7601 … # 7700</code></td>
</tr>


<tr>
<td class="org-left"><code>PALLET\_PROGRAM</code></td>
<td class="org-left"><code>  100</code></td>
<td class="org-left"><code># 7701 … # 7800</code></td>
</tr>


<tr>
<td class="org-left"><code>PALLET\_USAGE</code></td>
<td class="org-left"><code>  100</code></td>
<td class="org-left"><code># 7801 … # 7900</code></td>
</tr>


<tr>
<td class="org-left"><code>GAP23</code></td>
<td class="org-left"><code>  599</code></td>
<td class="org-left"><code># 7901 … # 8499</code></td>
</tr>


<tr>
<td class="org-left"><code>ATM\_ID</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 8500    </code></td>
</tr>


<tr>
<td class="org-left"><code>ATM\_PERCENT</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 8501    </code></td>
</tr>


<tr>
<td class="org-left"><code>ATM\_TOTAL\_AVL\_USAGE</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 8502    </code></td>
</tr>


<tr>
<td class="org-left"><code>ATM\_TOTAL\_AVL\_HOLE\_COUNT</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 8503    </code></td>
</tr>


<tr>
<td class="org-left"><code>ATM\_TOTAL\_AVL\_FEED\_TIME</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 8504    </code></td>
</tr>


<tr>
<td class="org-left"><code>ATM\_TOTAL\_AVL\_TOTAL\_TIME</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 8505    </code></td>
</tr>


<tr>
<td class="org-left"><code>GAP24</code></td>
<td class="org-left"><code>    4</code></td>
<td class="org-left"><code># 8506 … # 8509</code></td>
</tr>


<tr>
<td class="org-left"><code>ATM\_NEXT\_TOOL\_NUMBER</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 8510    </code></td>
</tr>


<tr>
<td class="org-left"><code>ATM\_NEXT\_TOOL\_LIFE</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 8511    </code></td>
</tr>


<tr>
<td class="org-left"><code>ATM\_NEXT\_TOOL\_AVL\_USAGE</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 8512    </code></td>
</tr>


<tr>
<td class="org-left"><code>ATM\_NEXT\_TOOL\_HOLE\_COUNT</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 8513    </code></td>
</tr>


<tr>
<td class="org-left"><code>ATM\_NEXT\_TOOL\_FEED\_TIME</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 8514    </code></td>
</tr>


<tr>
<td class="org-left"><code>ATM\_NEXT\_TOOL\_TOTAL\_TIME</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 8515    </code></td>
</tr>


<tr>
<td class="org-left"><code>GAP25</code></td>
<td class="org-left"><code>   34</code></td>
<td class="org-left"><code># 8516 … # 8549</code></td>
</tr>


<tr>
<td class="org-left"><code>TOOL\_ID</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 8550    </code></td>
</tr>


<tr>
<td class="org-left"><code>TOOL\_FLUTES</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 8551    </code></td>
</tr>


<tr>
<td class="org-left"><code>TOOL\_MAX\_VIBRATION</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 8552    </code></td>
</tr>


<tr>
<td class="org-left"><code>TOOL\_LENGTH\_OFFSETS</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 8553    </code></td>
</tr>


<tr>
<td class="org-left"><code>TOOL\_LENGTH\_WEAR</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 8554    </code></td>
</tr>


<tr>
<td class="org-left"><code>TOOL\_DIAMETER\_OFFSETS</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 8555    </code></td>
</tr>


<tr>
<td class="org-left"><code>TOOL\_DIAMETER\_WEAR</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 8556    </code></td>
</tr>


<tr>
<td class="org-left"><code>TOOL\_ACTUAL\_DIAMETER</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 8557    </code></td>
</tr>


<tr>
<td class="org-left"><code>TOOL\_COOLANT\_POSITION</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 8558    </code></td>
</tr>


<tr>
<td class="org-left"><code>TOOL\_FEED\_TIMER</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 8559    </code></td>
</tr>


<tr>
<td class="org-left"><code>TOOL\_TOTAL\_TIMER</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 8560    </code></td>
</tr>


<tr>
<td class="org-left"><code>TOOL\_LIFE\_LIMIT</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 8561    </code></td>
</tr>


<tr>
<td class="org-left"><code>TOOL\_LIFE\_COUNTER</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 8562    </code></td>
</tr>


<tr>
<td class="org-left"><code>TOOL\_LIFE\_MAX\_LOAD</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 8563    </code></td>
</tr>


<tr>
<td class="org-left"><code>TOOL\_LIFE\_LOAD\_LIMIT</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 8564    </code></td>
</tr>


<tr>
<td class="org-left"><code>GAP26</code></td>
<td class="org-left"><code>  435</code></td>
<td class="org-left"><code># 8565 … # 8999</code></td>
</tr>


<tr>
<td class="org-left"><code>THERMAL\_COMP\_ACC</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 9000    </code></td>
</tr>


<tr>
<td class="org-left"><code>GAP27</code></td>
<td class="org-left"><code>   15</code></td>
<td class="org-left"><code># 9001 … # 9015</code></td>
</tr>


<tr>
<td class="org-left"><code>THERMAL\_SPINDLE\_COMP\_ACC</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     # 9016    </code></td>
</tr>


<tr>
<td class="org-left"><code>GAP28</code></td>
<td class="org-left"><code>  983</code></td>
<td class="org-left"><code># 9017 … # 9999</code></td>
</tr>


<tr>
<td class="org-left"><code>GVARIABLES3</code></td>
<td class="org-left"><code> 1000</code></td>
<td class="org-left"><code>#10000 … #10999</code></td>
</tr>


<tr>
<td class="org-left"><code>INPUTS1</code></td>
<td class="org-left"><code>  256</code></td>
<td class="org-left"><code>#11000 … #11255</code></td>
</tr>


<tr>
<td class="org-left"><code>GAP29</code></td>
<td class="org-left"><code>  744</code></td>
<td class="org-left"><code>#11256 … #11999</code></td>
</tr>


<tr>
<td class="org-left"><code>OUTPUT1</code></td>
<td class="org-left"><code>  256</code></td>
<td class="org-left"><code>#12000 … #12255</code></td>
</tr>


<tr>
<td class="org-left"><code>GAP30</code></td>
<td class="org-left"><code>  744</code></td>
<td class="org-left"><code>#12256 … #12999</code></td>
</tr>


<tr>
<td class="org-left"><code>FILTERED\_ANALOG1</code></td>
<td class="org-left"><code>   13</code></td>
<td class="org-left"><code>#13000 … #13012</code></td>
</tr>


<tr>
<td class="org-left"><code>COOLANT\_LEVEL</code></td>
<td class="org-left"><code>    1</code></td>
<td class="org-left"><code>     #13013    </code></td>
</tr>


<tr>
<td class="org-left"><code>FILTERED\_ANALOG2</code></td>
<td class="org-left"><code>   50</code></td>
<td class="org-left"><code>#13014 … #13063</code></td>
</tr>


<tr>
<td class="org-left"><code>GAP31</code></td>
<td class="org-left"><code>  936</code></td>
<td class="org-left"><code>#13064 … #13999</code></td>
</tr>


<tr>
<td class="org-left"><code>SETTING</code></td>
<td class="org-left"><code>10000</code></td>
<td class="org-left"><code>#20000 … #29999</code></td>
</tr>


<tr>
<td class="org-left"><code>PARAMETER</code></td>
<td class="org-left"><code>10000</code></td>
<td class="org-left"><code>#30000 … #39999</code></td>
</tr>


<tr>
<td class="org-left"><code>TOOL\_TYP</code></td>
<td class="org-left"><code>  200</code></td>
<td class="org-left"><code>#50001 … #50200</code></td>
</tr>


<tr>
<td class="org-left"><code>TOOL\_MATERIAL</code></td>
<td class="org-left"><code>  200</code></td>
<td class="org-left"><code>#50201 … #50400</code></td>
</tr>


<tr>
<td class="org-left"><code>GAP32</code></td>
<td class="org-left"><code>50600</code></td>
<td class="org-left"><code>#50401 … #101000</code></td>
</tr>


<tr>
<td class="org-left"><code>CURRENT\_OFFSET</code></td>
<td class="org-left"><code>  200</code></td>
<td class="org-left"><code>#50601 … #50800</code></td>
</tr>


<tr>
<td class="org-left"><code>CURRENT\_OFFSET2</code></td>
<td class="org-left"><code>  200</code></td>
<td class="org-left"><code>#50801 … #51000</code></td>
</tr>


<tr>
<td class="org-left"><code>GAP32</code></td>
<td class="org-left"><code>51300</code></td>
<td class="org-left"><code>#51001 … #102300</code></td>
</tr>


<tr>
<td class="org-left"><code>VPS\_TEMPLATE\_OFFSET</code></td>
<td class="org-left"><code>  100</code></td>
<td class="org-left"><code>#51301 … #51400</code></td>
</tr>


<tr>
<td class="org-left"><code>WORK\_MATERIAL</code></td>
<td class="org-left"><code>  200</code></td>
<td class="org-left"><code>#51401 … #51600</code></td>
</tr>


<tr>
<td class="org-left"><code>VPS\_FEEDRATE</code></td>
<td class="org-left"><code>  200</code></td>
<td class="org-left"><code>#51601 … #51800</code></td>
</tr>


<tr>
<td class="org-left"><code>APPROX\_LENGTH</code></td>
<td class="org-left"><code>  200</code></td>
<td class="org-left"><code>#51801 … #52000</code></td>
</tr>


<tr>
<td class="org-left"><code>APPROX\_DIAMETER</code></td>
<td class="org-left"><code>  200</code></td>
<td class="org-left"><code>#52001 … #52200</code></td>
</tr>


<tr>
<td class="org-left"><code>EDGE\_MEASURE\_HEIGHT</code></td>
<td class="org-left"><code>  200</code></td>
<td class="org-left"><code>#52201 … #52400</code></td>
</tr>


<tr>
<td class="org-left"><code>TOOL\_TOLERANCE</code></td>
<td class="org-left"><code>  200</code></td>
<td class="org-left"><code>#52401 … #52600</code></td>
</tr>


<tr>
<td class="org-left"><code>PROBE\_TYPE</code></td>
<td class="org-left"><code>  200</code></td>
<td class="org-left"><code>#52601 … #52800</code></td>
</tr>
</tbody>
</table>

---


<a id="Why"></a>

# Why

Waiting for a replacement stylus **and** tool setter to arrive, I
wondered if were possible to replace the hundreds of inscrutible lines
of Hass WIPS Renishaw G-code with just a few lines of Python?

%80 there.

---
