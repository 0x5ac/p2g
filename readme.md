# P2G

<img src="/docs/pytest.svg" alt=""><img src="/docs/mit.svg" alt=""><img src="/docs/coverage.svg" alt="">


## Demo.

<a href="https://youtu.be/PX818-iRb1Q">
<img src="https://github.com/0x5ac/p2g/blob/main/docs/png/vicecenter1.png" alt="link to youtube.">
</a>


## Introduction


### Version 0.3.10

P2G makes it simple to ensure that parts are in fixtures correctly, coordinate systems are adjusted to deal with stock placement and cope with movement and rotation of workpieces through multiple operations.

P2G is a compiler; it takes Python code, some definitions of machine specific variables, a little glue and makes G-code, so far, Haas ideomatic.

Thanks to magic it can do surprising things with python data structures, anything reasonably calculated statically during compilation can be used in the source, classes, dicts, and so on.

It comes with a set of macro variable definitions for a Haas mill with NCD. And a few example settings for my own VF-3SSYT.


## Install


### From pypi

```

$ pip install p2g

```


### From github

1.  fetch dependencies, rebuild and install with pip

    ```
    $ git clone https://github.com/0x5ac/attempt1 p2g
    $ cd p2g
    $ make install
    ```

2.  fetch dependencies and rebuild

    ```
    $ git clone https://github.com/0x5ac/attempt1 p2g
    $ cd p2g
    $ make
    ```


## Usage

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


## Examples

for a show:

```
$ p2g examples dstdir
```

---


### Simple demo

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


### Find largest number of flutes in tool table

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


### Less trivial example

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


# Table of contents


## TOC

-   [Introduction](https://github.com/0x5ac/p2g/blob/main/docs/howto.md#introduction)
-   [Video](https://github.com/0x5ac/p2g/blob/main/docs/howto.md#demo)
-   [Install](https://github.com/0x5ac/p2g/blob/main/docs/howto.md#install)
-   [Usage](https://github.com/0x5ac/p2g/blob/main/docs/howto.md#usage)
-   [Examples](https://github.com/0x5ac/p2g/blob/main/docs/howto.md#examples)
-   [Variables](https://github.com/0x5ac/p2g/blob/main/docs/howto.md#variables)
-   [Coordinates](https://github.com/0x5ac/p2g/blob/main/docs/howto.md#coordinates)
-   [Expressions](https://github.com/0x5ac/p2g/blob/main/docs/howto.md#expressions)
-   [Goto](https://github.com/0x5ac/p2g/blob/main/docs/howto.md#goto)
-   [Axes](https://github.com/0x5ac/p2g/blob/main/docs/howto.md#axes)
-   [When](https://github.com/0x5ac/p2g/blob/main/docs/howto.md#when)
-   [DPRNT](https://github.com/0x5ac/p2g/blob/main/docs/howto.md#dprnt)
-   [Notes](https://github.com/0x5ac/p2g/blob/main/docs/howto.md#notes)
-   [Authors](https://github.com/0x5ac/p2g/blob/main/docs/howto.md#authors)
-   [Thanks](https://github.com/0x5ac/p2g/blob/main/docs/howto.md#thanks)

-   Copyright © 2023 Steve Chamberlain