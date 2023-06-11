    :Author: sac

.. contents::

1 p2g - Python 2 G-code
-----------------------

Many styli died to bring us this information.

This is a Python to G-code transplier

It takes Python code, some definitions of machine specific variables,
a little glue and makes G-code, so far, Haas ideomatic.

Thanks to magic it can do surprising things with python data
structures, anything reasonably calculated statically during
compilation can be used in the source, classes, dicts, and so on.

It comes with a set of macro variable definitions for a Haas mill with
NCD.  And a few example settings for my own VF-3SSYT.

2 Install:
----------

::

    $ pip install p2g

for big show:

::

    $ p2g examples

something smaller:

::

    $ cat > tst.py <<EOF
    import p2g
    def t():
      x = p2g.Var(9)
      for y in range(10):
        x += y
    EOF
    $ p2g gen tst.py

yields 

::

      O0001                           ( TST                           )
      #100= 9.                        (   x = Var[9]                  )
      #102= 0.                        (   for y in range[10]:         )
    L2000
      IF [#102 GE 10.] GOTO 2002
      #100= #100 + #102               ( x += y                        )
      #102= #102 + 1.
      GOTO 2000
    L2002
      M30

3 A taste.
----------

.. code:: python
    :name: demo1

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
            message(ALARM.var, f"too far {sch.name}.", code=101)

    def demo1():
        cursor = Var[3](2, 3, 4)
        # searching right, look down 0.4", move
        # 1.5" right if nothing hit.
        sch1 = SearchParams(name="right", search_depth=-0.4, iota=-0.1, delta=(1.5, 0))
        search(cursor, sch1)


⇨ ``p2g gen demo1.py`` ⇨


::

      O0001                           ( -                             )
      #100= 2.                        ( cursor = Var[3][2, 3, 4]      )
      #101= 3.
      #102= 4.
      #103= 10.                       ( its = Var[sch.its]            )
    L1000                             ( while its > 0:                )
      IF [#103 LE 0.] GOTO 1002
      G01 G90 F640. x#100 y#101 z#102 (     sch.go[cursor]            )
      G01 G90 G31 F30. z-0.4          (     sch.probe[z=sch.search_depth])
      IF [#5063 LT -0.5] GOTO 1001    (     if SKIP_POS.z < sch.search_depth + sch.iota:)
      #100= #100 + 1.5                (     cursor.xy += sch.delta    )
      #103= #103 - 1.                 (     its -= 1                  )
      GOTO 1000
    L1002
      #3000= 101.                     ( too far right.                )
    L1001                             (     message[ALARM.var, f"too far {sch.name}.", code=101])
      M30

4 Coordinates
-------------

Describe position, with axis by location, in sequence or by name.

.. code:: python
    :name: co1

    from p2g import *       # this is the common header
    from p2g.haas import *  # to all the examples

    def co1():
        com ("Coords by order.")
        p1 = Fixed[3](1, 2, 3, addr=100)

        com ("Coords by axis name.")
        p2 = Fixed[3](z=333, y=222, x=111, addr=200)
        p2.x = 17

        com ("Coords by index.")      
        p1.xyz = p2[2]
        p2[1:3] = 7

        com ("Mixemup.")
        p1.yz = p2.yz[1]

        com ("Rotaries.")
        p4 = Fixed[6]()
        p4.a = 180
        p4.c = asin (0.5)

⇨ ``p2g gen co1.py`` ⇨

::

      O0001                           ( -                             )
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
    ( Mixemup. )
      #101= #202                      ( p1.yz = p2.yz[1]              )
      #102= #202
    ( Rotaries. )
      #103= 180.                      ( p4.a = 180                    )
      #105= 30.                       ( p4.c = asin [0.5]             )
      M30

5 Variables
-----------

- Give names to macro variables at a known address:

  ``Fixed`` ❰ ``[`` *size* ``]`` ❱\ :sub:`opt`\ (``addr=`` *addr* ❰ ``,`` *init* ... ❱\ :sub:`opt`\ ``)``

- Give names to macro variables automatically per function.

  ``Var`` ❰ ``[`` *size* ``]`` ❱\ :sub:`opt`\ (❰ ``,`` *init* ... ❱\ :sub:`opt`\ ``)``

- Not actually a variable, but same syntax.

  ``Const`` ❰ ``[`` *size* ``]`` ❱\ :sub:`opt`\ (❰ ``,`` *init* ... ❱\ :sub:`opt`\ ``)``

Example:   

.. code:: python
    :name: var1


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
        above_tdc = Const (111,222,333)

        com("Use it ")
        tmp0 += above_tdc

⇨ ``p2g gen var1.py`` ⇨

::

      O0001                           ( -                             )
      #100= #5061 * 2. + #5041 + #5061( tmp0 = Var[ skip0.xyz * 2.0 + workpos + skip1])
      #101= #5062 * 2. + #5042 + #5062
      #102= #5063 * 2. + #5043 + #5063
    ( Define a constant  )
    ( Use it  )
      #100= #100 + 111.               ( tmp0 += above_tdc             )
      #101= #101 + 222.
      #102= #102 + 333.
      M30

6 Expressions
-------------

Python expressions turn into G-Code as you may expect, save that
native Python uses radians for trig, and G-Code uses degrees, so
folding is done in degrees.


.. code:: python
    :name: exp1

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

⇨ ``p2g gen exp1.py`` ⇨

::

      O0001                           ( -                             )
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

7 Axes
------

Any number of axes are supported, default just being xy and z.
A rotary on ac can be set with p2g.AXIS.NAMES="xyza\*c".
The axis letters should be the same order as your machine expects
coordinates to turn up in work offset registers.



.. code:: python
    :name: axes


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

⇨ ``p2g gen axes.py`` ⇨

::

    O0001                           ( -                             )
    #5241= 0.                       (    G55.var = [0]              )
    #5242= 0.
    #5243= 0.
    #5244= 0.
    #5245= 0.
    #5246= 0.
    #5242= #5242 + 3.               (    G55.var += tmp1            )
    #5243= #5243 + 9.
    #5246= #5246 + 30.
    #5244= #5244 * 2.               (    G55.ac *= 2.0              )
    #5246= #5246 * 2.
    #5241= 0.                       (    G55.var = [0]              )
    #5242= 0.
    #5243= 0.
    #100= #5241 * 34.               (    tmp = Var[G55 * 34]        )
    #101= #5242 * 34.
    #102= #5243 * 34.
    M30

8 Printing
----------

Turns Python f string prints into G-code DPRNT.  Make sure
that your print string does not have any characters in it that
your machine considers to be illegal in a DPRNT string.


.. code:: python
    :name: exprnt

    from p2g import *
    from p2g.haas import *

    def exprnt():
      x = Var(2)
      y = Var(27)  

      for q in range(10):
        dprint(f"X is {x:3.1f}, Y+Q is {y+q:5.2f}")

⇨ ``p2g gen exprnt.py`` ⇨

::

      O0001                           ( -                             )
      #100= 2.                        (   x = Var[2]                  )
      #101= 27.                       (   y = Var[27]                 )
      #103= 0.                        (   for q in range[10]:         )
    L1000
      IF [#103 GE 10.] GOTO 1002
    ( dprint[f"X is {x:3.1f}, Y+Q is {y+q:5.2f}"])
    DPRNT[X*is*[#100][31],*Y+Q*is*[#101+#103][52]]
      #103= #103 + 1.
      GOTO 1000
    L1002
      M30

9 Symbol Tables.
----------------

Set the global ``p2g.symbol.Table.print`` to get a symbol
table in the output file.

.. code:: python
    :name: stest

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

::

    ( RAW_ANALOG                              : #1080[10]               )
    ( v1                                      :  #106.x                 )
    ( MACHINE_ABS_ABOVE_OTS                   :  -7.000,  8.000,  9.000 )
    ( MACHINE_ABS_ABOVE_SEARCH_ROTARY_LHS_5X8 : 100.000,101.000,102.000 )
    ( MACHINE_ABS_ABOVE_VICE                  :  17.000, 18.000, 19.000 )
      O0001                           ( -                             )

    ( Only used symbols are in output table. )
      #100= -7.                       ( Var[MACHINE_ABS_ABOVE_OTS]    )
      #101= 8.
      #102= 9.
      #103= 170.                      ( Var[MACHINE_ABS_ABOVE_VICE * fish])
      #104= 180.
      #105= 190.
      #106= #106 + #1087              ( v1 += RAW_ANALOG[7]           )
      M30

10 Goto.
--------

Goto functions are constructed from parts, and make
building  blocks when partially applied.

goto [ .  / modifier / ] \*  ``(`` /coordinates/~)~

modifier :

- ``r9810``
  Use Renishaw macro 9810 to do a protected positioning cycle.

- ``work``
  Use current work coordinate system. - G90

- ``machine``
  Use the machine coordinate system - G90 G53

- ``relative``
  Use relative coordinate system - G91

- ``z_then_xy``
  move Z axis first.

- ``xy_then_z``
  move the other axes before the Z.

- ``probe``
  Emit probe code using G31.

- ``xyz``
  Move all axes at once.

- ``feed(~/expr/``)~
  Set feed rate.

- ``mcode(~/string/``)~
  Apply an mcode.


.. code:: python
    :name: goto1

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

::

    ( v1      :  #100.x  #101.y  #102.z )
    ( absslow : 10 machine xyz          )
    ( g1      : 20 work xyz             )
    ( p1      : 100 machine xyz         )
    ( p2      : 100 machine xyz probe   )
    ( p3      : 100 relative xyz probe  )
    ( r9810   : 20 r9810 xyz            )
      O0001                           ( -                             )

    ( in work cosys, goto x=1, y=2, z=3 at 20ips )
      G01 G90 F20. x1. y2. z3.        ( g1 [1,2,3]                    )

    ( make a variable, 2,3,4 )
      #100= 2.                        ( v1 = Var[x=2,y=3,z=4]         )
      #101= 3.
      #102= 4.

    ( In the machine cosys, move to v1.z then v1.xy, slowly )
      G01 G90 G53 F10. z#102          ( absslow.z_then_xy[v1]         )
      G01 G90 G53 F10. x#100 y#101

    ( p1 is whatever absslow was, with feed adjusted to 100. )
      G01 G90 G53 F100. x#100 y#101   ( p1.xy_then_z[v1]              )
      G01 G90 G53 F100. z#102

    ( p2 is whatever p1 was, with changed to a probe. )
    ( p2.xy_then_z[v1]              )
      G01 G90 G53 G31 F100. x#100 y#101
      G01 G90 G53 G31 F100. z#102

    ( p3 is whatever p1 was, with a probe and relative, )
    ( using only the x and y axes                       )
      G01 G91 G31 F100. x#100 y#101   ( p3.xy_then_z[v1.xy]           )

    ( move a and c axes  )
      G01 G90 F20. a9. c90.           ( goto.feed[20] [a=9, c= 90]    )

    ( probe with a hass MUST_SKIP mcode. )
      G01 G90 G31 M79 F10. x3. y4. z5.( goto.probe.feed[10].mcode["M79"][3,4,5])
      G01 G65 R9810 F20. z3.          ( safe_goto.z_then_xy[1,2,3]    )
      G01 G65 R9810 F20. x1. y2.
      M30

11 Notes.
---------

The entire thing is brittle; I've only used it to make code
for my own limited purposes. 

Nice things:


.. code:: python


    from p2g import *
    from p2g.haas import *

    class X():
             def __init__(self, a,b):
                   self.a = a
                   self.b = b
             def adjust(self, tof):
                   self.a += tof.x
                   self.b += tof.y

    def cool():
          com ("You can do surprising things.")
          p = X(12,34)

          p.adjust(TOOL_OFFSET)
          tmp = Var(p.a, p.b)

::

      O0001                           ( -                             )
    ( You can do surprising things. )
      #100= #5081 + 12.               (   tmp = Var[p.a, p.b]         )
      #101= #5082 + 34.
      M30






.. code:: python

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

::

      O0001                           ( -                             )
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

.. code:: python

    from p2g import *
    from p2g.haas import *
    def beware1():
       com ("It's easy to forget that only macro variables will get into",
          "the output code. Generated ifs with a constant are a give away:")
       x = 123
       y = Var()
       if x==23 :  # look here
         y = 9

       com ("Should look like:")
       x = Var(123)
       y = Var()
       if x==23 :  # look here
         y = 9
       else:
         y = 99

::

      O0001                           ( -                             )
    ( It's easy to forget that only macro variables will get into     )
    ( the output code. Generated ifs with a constant are a give away: )
      IF [1.] GOTO 1000               (    if x==23 :  # look here    )
      #100= 9.                        (  y = 9                        )
      GOTO 1001
    L1000
    L1001
    ( Should look like: )
      #101= 123.                      (    x = Var[123]               )
      #100= #102                      (    y = Var[]                  )
      IF [#101 NE 23.] GOTO 1002      (    if x==23 :  # look here    )
      #100= 9.                        (  y = 9                        )
      GOTO 1003
    L1002
      #100= 99.                       (  y = 99                       )
    L1003
      M30

12 HAAS macro var definitions
-----------------------------

Names predefined in p2g.haas:


.. table::

    +-------------------------------+-----------+---------------------+
    | Name                          |      Size | Address             |
    +-------------------------------+-----------+---------------------+
    | ``NULL``                      |     ``1`` | ``# 0``             |
    +-------------------------------+-----------+---------------------+
    | ``MACRO_ARGUMENTS``           |    ``33`` | ``# 1 … # 33``      |
    +-------------------------------+-----------+---------------------+
    | ``GP_SAVED1``                 |   ``100`` | ``# 100 … # 199``   |
    +-------------------------------+-----------+---------------------+
    | ``GP_SAVED2``                 |    ``50`` | ``# 500 … # 549``   |
    +-------------------------------+-----------+---------------------+
    | ``PROBE_CALIBRATION1``        |     ``6`` | ``# 550 … # 555``   |
    +-------------------------------+-----------+---------------------+
    | ``PROBE_R``                   |     ``3`` | ``# 556 … # 558``   |
    +-------------------------------+-----------+---------------------+
    | ``PROBE_CALIBRATION2``        |    ``22`` | ``# 559 … # 580``   |
    +-------------------------------+-----------+---------------------+
    | ``GP_SAVED3``                 |   ``119`` | ``# 581 … # 699``   |
    +-------------------------------+-----------+---------------------+
    | ``GP_SAVED4``                 |   ``200`` | ``# 800 … # 999``   |
    +-------------------------------+-----------+---------------------+
    | ``INPUTS``                    |    ``64`` | ``# 1000 … # 1063`` |
    +-------------------------------+-----------+---------------------+
    | ``MAX_LOADS_XYZAB``           |     ``5`` | ``# 1064 … # 1068`` |
    +-------------------------------+-----------+---------------------+
    | ``RAW_ANALOG``                |    ``10`` | ``# 1080 … # 1089`` |
    +-------------------------------+-----------+---------------------+
    | ``FILTERED_ANALOG``           |     ``8`` | ``# 1090 … # 1097`` |
    +-------------------------------+-----------+---------------------+
    | ``SPINDLE_LOAD``              |     ``1`` | ``# 1098``          |
    +-------------------------------+-----------+---------------------+
    | ``MAX_LOADS_CTUVW``           |     ``5`` | ``# 1264 … # 1268`` |
    +-------------------------------+-----------+---------------------+
    | ``TOOL_TBL_FLUTES``           |   ``200`` | ``# 1601 … # 1800`` |
    +-------------------------------+-----------+---------------------+
    | ``TOOL_TBL_VIBRATION``        |   ``200`` | ``# 1801 … # 2000`` |
    +-------------------------------+-----------+---------------------+
    | ``TOOL_TBL_OFFSETS``          |   ``200`` | ``# 2001 … # 2200`` |
    +-------------------------------+-----------+---------------------+
    | ``TOOL_TBL_WEAR``             |   ``200`` | ``# 2201 … # 2400`` |
    +-------------------------------+-----------+---------------------+
    | ``TOOL_TBL_DROFFSET``         |   ``200`` | ``# 2401 … # 2600`` |
    +-------------------------------+-----------+---------------------+
    | ``TOOL_TBL_DRWEAR``           |   ``200`` | ``# 2601 … # 2800`` |
    +-------------------------------+-----------+---------------------+
    | ``ALARM``                     |     ``1`` | ``# 3000``          |
    +-------------------------------+-----------+---------------------+
    | ``T_MS``                      |     ``1`` | ``# 3001``          |
    +-------------------------------+-----------+---------------------+
    | ``T_HR``                      |     ``1`` | ``# 3002``          |
    +-------------------------------+-----------+---------------------+
    | ``SINGLE_BLOCK_OFF``          |     ``1`` | ``# 3003``          |
    +-------------------------------+-----------+---------------------+
    | ``FEED_HOLD_OFF``             |     ``1`` | ``# 3004``          |
    +-------------------------------+-----------+---------------------+
    | ``MESSAGE``                   |     ``1`` | ``# 3006``          |
    +-------------------------------+-----------+---------------------+
    | ``YEAR_MONTH_DAY``            |     ``1`` | ``# 3011``          |
    +-------------------------------+-----------+---------------------+
    | ``HOUR_MINUTE_SECOND``        |     ``1`` | ``# 3012``          |
    +-------------------------------+-----------+---------------------+
    | ``POWER_ON_TIME``             |     ``1`` | ``# 3020``          |
    +-------------------------------+-----------+---------------------+
    | ``CYCLE_START_TIME``          |     ``1`` | ``# 3021``          |
    +-------------------------------+-----------+---------------------+
    | ``FEED_TIMER``                |     ``1`` | ``# 3022``          |
    +-------------------------------+-----------+---------------------+
    | ``CUR_PART_TIMER``            |     ``1`` | ``# 3023``          |
    +-------------------------------+-----------+---------------------+
    | ``LAST_COMPLETE_PART_TIMER``  |     ``1`` | ``# 3024``          |
    +-------------------------------+-----------+---------------------+
    | ``LAST_PART_TIMER``           |     ``1`` | ``# 3025``          |
    +-------------------------------+-----------+---------------------+
    | ``TOOL_IN_SPIDLE``            |     ``1`` | ``# 3026``          |
    +-------------------------------+-----------+---------------------+
    | ``SPINDLE_RPM``               |     ``1`` | ``# 3027``          |
    +-------------------------------+-----------+---------------------+
    | ``PALLET_LOADED``             |     ``1`` | ``# 3028``          |
    +-------------------------------+-----------+---------------------+
    | ``SINGLE_BLOCK``              |     ``1`` | ``# 3030``          |
    +-------------------------------+-----------+---------------------+
    | ``AGAP``                      |     ``1`` | ``# 3031``          |
    +-------------------------------+-----------+---------------------+
    | ``BLOCK_DELETE``              |     ``1`` | ``# 3032``          |
    +-------------------------------+-----------+---------------------+
    | ``OPT_STOP``                  |     ``1`` | ``# 3033``          |
    +-------------------------------+-----------+---------------------+
    | ``TIMER_CELL_SAFE``           |     ``1`` | ``# 3196``          |
    +-------------------------------+-----------+---------------------+
    | ``TOOL_TBL_DIAMETER``         |   ``200`` | ``# 3201 … # 3400`` |
    +-------------------------------+-----------+---------------------+
    | ``TOOL_TBL_COOLANT_POSITION`` |   ``200`` | ``# 3401 … # 3600`` |
    +-------------------------------+-----------+---------------------+
    | ``M30_COUNT1``                |     ``1`` | ``# 3901``          |
    +-------------------------------+-----------+---------------------+
    | ``M30_COUNT2``                |     ``1`` | ``# 3902``          |
    +-------------------------------+-----------+---------------------+
    | ``LAST_BLOCK_G``              |    ``21`` | ``# 4001 … # 4021`` |
    +-------------------------------+-----------+---------------------+
    | ``LAST_BLOCK_ADDRESS``        |    ``26`` | ``# 4101 … # 4126`` |
    +-------------------------------+-----------+---------------------+
    | ``LAST_TARGET_POS``           | ``NAXES`` | ``# 5001…``         |
    +-------------------------------+-----------+---------------------+
    | ``MACHINE_POS``               | ``NAXES`` | ``# 5021…``         |
    +-------------------------------+-----------+---------------------+
    | ``MACHINE``                   | ``NAXES`` | ``# 5021…``         |
    +-------------------------------+-----------+---------------------+
    | ``G53``                       | ``NAXES`` | ``# 5021…``         |
    +-------------------------------+-----------+---------------------+
    | ``WORK_POS``                  | ``NAXES`` | ``# 5041…``         |
    +-------------------------------+-----------+---------------------+
    | ``WORK``                      | ``NAXES`` | ``# 5041…``         |
    +-------------------------------+-----------+---------------------+
    | ``SKIP_POS``                  | ``NAXES`` | ``# 5061…``         |
    +-------------------------------+-----------+---------------------+
    | ``PROBE``                     | ``NAXES`` | ``# 5061…``         |
    +-------------------------------+-----------+---------------------+
    | ``TOOL_OFFSET``               |    ``20`` | ``# 5081 … # 5100`` |
    +-------------------------------+-----------+---------------------+
    | ``G52``                       | ``NAXES`` | ``# 5201…``         |
    +-------------------------------+-----------+---------------------+
    | ``G54``                       | ``NAXES`` | ``# 5221…``         |
    +-------------------------------+-----------+---------------------+
    | ``G55``                       | ``NAXES`` | ``# 5241…``         |
    +-------------------------------+-----------+---------------------+
    | ``G56``                       | ``NAXES`` | ``# 5261…``         |
    +-------------------------------+-----------+---------------------+
    | ``G57``                       | ``NAXES`` | ``# 5281…``         |
    +-------------------------------+-----------+---------------------+
    | ``G58``                       | ``NAXES`` | ``# 5301…``         |
    +-------------------------------+-----------+---------------------+
    | ``G59``                       | ``NAXES`` | ``# 5321…``         |
    +-------------------------------+-----------+---------------------+
    | ``TOOL_TBL_FEED_TIMERS``      |   ``100`` | ``# 5401 … # 5500`` |
    +-------------------------------+-----------+---------------------+
    | ``TOOL_TBL_TOTAL_TIMERS``     |   ``100`` | ``# 5501 … # 5600`` |
    +-------------------------------+-----------+---------------------+
    | ``TOOL_TBL_LIFE_LIMITS``      |   ``100`` | ``# 5601 … # 5700`` |
    +-------------------------------+-----------+---------------------+
    | ``TOOL_TBL_LIFE_COUNTERS``    |   ``100`` | ``# 5701 … # 5800`` |
    +-------------------------------+-----------+---------------------+
    | ``TOOL_TBL_LIFE_MAX_LOADS``   |   ``100`` | ``# 5801 … # 5900`` |
    +-------------------------------+-----------+---------------------+
    | ``TOOL_TBL_LIFE_LOAD_LIMITS`` |   ``100`` | ``# 5901 … # 6000`` |
    +-------------------------------+-----------+---------------------+
    | ``NGC_CF``                    |     ``1`` | ``# 6198``          |
    +-------------------------------+-----------+---------------------+
    | ``G154_P1``                   | ``NAXES`` | ``# 7001…``         |
    +-------------------------------+-----------+---------------------+
    | ``G154_P2``                   | ``NAXES`` | ``# 7021…``         |
    +-------------------------------+-----------+---------------------+
    | ``G154_P3``                   | ``NAXES`` | ``# 7041…``         |
    +-------------------------------+-----------+---------------------+
    | ``G154_P4``                   | ``NAXES`` | ``# 7061…``         |
    +-------------------------------+-----------+---------------------+
    | ``G154_P5``                   | ``NAXES`` | ``# 7081…``         |
    +-------------------------------+-----------+---------------------+
    | ``G154_P6``                   | ``NAXES`` | ``# 7101…``         |
    +-------------------------------+-----------+---------------------+
    | ``G154_P7``                   | ``NAXES`` | ``# 7121…``         |
    +-------------------------------+-----------+---------------------+
    | ``G154_P8``                   | ``NAXES`` | ``# 7141…``         |
    +-------------------------------+-----------+---------------------+
    | ``G154_P9``                   | ``NAXES`` | ``# 7161…``         |
    +-------------------------------+-----------+---------------------+
    | ``G154_P10``                  | ``NAXES`` | ``# 7181…``         |
    +-------------------------------+-----------+---------------------+
    | ``G154_P11``                  | ``NAXES`` | ``# 7201…``         |
    +-------------------------------+-----------+---------------------+
    | ``G154_P12``                  | ``NAXES`` | ``# 7221…``         |
    +-------------------------------+-----------+---------------------+
    | ``G154_P13``                  | ``NAXES`` | ``# 7241…``         |
    +-------------------------------+-----------+---------------------+
    | ``G154_P14``                  | ``NAXES`` | ``# 7261…``         |
    +-------------------------------+-----------+---------------------+
    | ``G154_P15``                  | ``NAXES`` | ``# 7281…``         |
    +-------------------------------+-----------+---------------------+
    | ``G154_P16``                  | ``NAXES`` | ``# 7301…``         |
    +-------------------------------+-----------+---------------------+
    | ``G154_P17``                  | ``NAXES`` | ``# 7321…``         |
    +-------------------------------+-----------+---------------------+
    | ``G154_P18``                  | ``NAXES`` | ``# 7341…``         |
    +-------------------------------+-----------+---------------------+
    | ``G154_P19``                  | ``NAXES`` | ``# 7361…``         |
    +-------------------------------+-----------+---------------------+
    | ``G154_P20``                  | ``NAXES`` | ``# 7381…``         |
    +-------------------------------+-----------+---------------------+
    | ``PALLET_PRIORITY``           |   ``100`` | ``# 7501 … # 7600`` |
    +-------------------------------+-----------+---------------------+
    | ``PALLET_STATUS``             |   ``100`` | ``# 7601 … # 7700`` |
    +-------------------------------+-----------+---------------------+
    | ``PALLET_PROGRAM``            |   ``100`` | ``# 7701 … # 7800`` |
    +-------------------------------+-----------+---------------------+
    | ``PALLET_USAGE``              |   ``100`` | ``# 7801 … # 7900`` |
    +-------------------------------+-----------+---------------------+
    | ``ATM_ID``                    |     ``1`` | ``# 8500``          |
    +-------------------------------+-----------+---------------------+
    | ``ATM_PERCENT``               |     ``1`` | ``# 8501``          |
    +-------------------------------+-----------+---------------------+
    | ``ATM_TOTAL_AVL_USAGE``       |     ``1`` | ``# 8502``          |
    +-------------------------------+-----------+---------------------+
    | ``ATM_TOTAL_AVL_HOLE_COUNT``  |     ``1`` | ``# 8503``          |
    +-------------------------------+-----------+---------------------+
    | ``ATM_TOTAL_AVL_FEED_TIME``   |     ``1`` | ``# 8504``          |
    +-------------------------------+-----------+---------------------+
    | ``ATM_TOTAL_AVL_TOTAL_TIME``  |     ``1`` | ``# 8505``          |
    +-------------------------------+-----------+---------------------+
    | ``ATM_NEXT_TOOL_NUMBER``      |     ``1`` | ``# 8510``          |
    +-------------------------------+-----------+---------------------+
    | ``ATM_NEXT_TOOL_LIFE``        |     ``1`` | ``# 8511``          |
    +-------------------------------+-----------+---------------------+
    | ``ATM_NEXT_TOOL_AVL_USAGE``   |     ``1`` | ``# 8512``          |
    +-------------------------------+-----------+---------------------+
    | ``ATM_NEXT_TOOL_HOLE_COUNT``  |     ``1`` | ``# 8513``          |
    +-------------------------------+-----------+---------------------+
    | ``ATM_NEXT_TOOL_FEED_TIME``   |     ``1`` | ``# 8514``          |
    +-------------------------------+-----------+---------------------+
    | ``ATM_NEXT_TOOL_TOTAL_TIME``  |     ``1`` | ``# 8515``          |
    +-------------------------------+-----------+---------------------+
    | ``TOOL_ID``                   |     ``1`` | ``# 8550``          |
    +-------------------------------+-----------+---------------------+
    | ``TOOL_FLUTES``               |     ``1`` | ``# 8551``          |
    +-------------------------------+-----------+---------------------+
    | ``TOOL_MAX_VIBRATION``        |     ``1`` | ``# 8552``          |
    +-------------------------------+-----------+---------------------+
    | ``TOOL_LENGTH_OFFSETS``       |     ``1`` | ``# 8553``          |
    +-------------------------------+-----------+---------------------+
    | ``TOOL_LENGTH_WEAR``          |     ``1`` | ``# 8554``          |
    +-------------------------------+-----------+---------------------+
    | ``TOOL_DIAMETER_OFFSETS``     |     ``1`` | ``# 8555``          |
    +-------------------------------+-----------+---------------------+
    | ``TOOL_DIAMETER_WEAR``        |     ``1`` | ``# 8556``          |
    +-------------------------------+-----------+---------------------+
    | ``TOOL_ACTUAL_DIAMETER``      |     ``1`` | ``# 8557``          |
    +-------------------------------+-----------+---------------------+
    | ``TOOL_COOLANT_POSITION``     |     ``1`` | ``# 8558``          |
    +-------------------------------+-----------+---------------------+
    | ``TOOL_FEED_TIMER``           |     ``1`` | ``# 8559``          |
    +-------------------------------+-----------+---------------------+
    | ``TOOL_TOTAL_TIMER``          |     ``1`` | ``# 8560``          |
    +-------------------------------+-----------+---------------------+
    | ``TOOL_LIFE_LIMIT``           |     ``1`` | ``# 8561``          |
    +-------------------------------+-----------+---------------------+
    | ``TOOL_LIFE_COUNTER``         |     ``1`` | ``# 8562``          |
    +-------------------------------+-----------+---------------------+
    | ``TOOL_LIFE_MAX_LOAD``        |     ``1`` | ``# 8563``          |
    +-------------------------------+-----------+---------------------+
    | ``TOOL_LIFE_LOAD_LIMIT``      |     ``1`` | ``# 8564``          |
    +-------------------------------+-----------+---------------------+
    | ``THERMAL_COMP_ACC``          |     ``1`` | ``# 9000``          |
    +-------------------------------+-----------+---------------------+
    | ``THERMAL_SPINDLE_COMP_ACC``  |     ``1`` | ``# 9016``          |
    +-------------------------------+-----------+---------------------+
    | ``GVARIABLES3``               |  ``1000`` | ``#10000 … #10999`` |
    +-------------------------------+-----------+---------------------+
    | ``INPUTS1``                   |   ``256`` | ``#11000 … #11255`` |
    +-------------------------------+-----------+---------------------+
    | ``OUTPUT1``                   |   ``256`` | ``#12000 … #12255`` |
    +-------------------------------+-----------+---------------------+
    | ``FILTERED_ANALOG1``          |    ``13`` | ``#13000 … #13012`` |
    +-------------------------------+-----------+---------------------+
    | ``COOLANT_LEVEL``             |     ``1`` | ``#13013``          |
    +-------------------------------+-----------+---------------------+
    | ``FILTERED_ANALOG2``          |    ``50`` | ``#13014 … #13063`` |
    +-------------------------------+-----------+---------------------+
    | ``SETTING``                   | ``10000`` | ``#20000 … #29999`` |
    +-------------------------------+-----------+---------------------+
    | ``PARAMETER``                 | ``10000`` | ``#30000 … #39999`` |
    +-------------------------------+-----------+---------------------+
    | ``TOOL_TYP``                  |   ``200`` | ``#50001 … #50200`` |
    +-------------------------------+-----------+---------------------+
    | ``TOOL_MATERIAL``             |   ``200`` | ``#50201 … #50400`` |
    +-------------------------------+-----------+---------------------+
    | ``CURRENT_OFFSET``            |   ``200`` | ``#50601 … #50800`` |
    +-------------------------------+-----------+---------------------+
    | ``CURRENT_OFFSET2``           |   ``200`` | ``#50801 … #51000`` |
    +-------------------------------+-----------+---------------------+
    | ``VPS_TEMPLATE_OFFSET``       |   ``100`` | ``#51301 … #51400`` |
    +-------------------------------+-----------+---------------------+
    | ``WORK_MATERIAL``             |   ``200`` | ``#51401 … #51600`` |
    +-------------------------------+-----------+---------------------+
    | ``VPS_FEEDRATE``              |   ``200`` | ``#51601 … #51800`` |
    +-------------------------------+-----------+---------------------+
    | ``APPROX_LENGTH``             |   ``200`` | ``#51801 … #52000`` |
    +-------------------------------+-----------+---------------------+
    | ``APPROX_DIAMETER``           |   ``200`` | ``#52001 … #52200`` |
    +-------------------------------+-----------+---------------------+
    | ``EDGE_MEASURE_HEIGHT``       |   ``200`` | ``#52201 … #52400`` |
    +-------------------------------+-----------+---------------------+
    | ``TOOL_TOLERANCE``            |   ``200`` | ``#52401 … #52600`` |
    +-------------------------------+-----------+---------------------+
    | ``PROBE_TYPE``                |   ``200`` | ``#52601 … #52800`` |
    +-------------------------------+-----------+---------------------+

13 Why:
-------

Waiting for a replacement stylus **and** tool setter to arrive, I
wondered if were possible to replace the hundreds of inscrutible lines
of Hass WIPS Renishaw G-code with just a few lines of Python?

Maybe.


>>
