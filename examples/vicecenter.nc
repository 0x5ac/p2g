O0001 (vicecenter: 0.2.103)
( Symbol Table )

 ( MABS_ABOVE_VICE      : -27.500,-13.000,-17.500 )
 ( above                : -27.500,-13.000,-17.500 )
 ( amax                 :  16.000,  9.000,  3.000 )
 ( amin                 :   8.000,  4.000,  1.000 )
 ( backoff              :   0.100,  0.100,  0.100 )
 ( delta                :   1.000,  1.000         )
 ( delta                :   1.000,<none>          )
 ( delta                :  -1.000,<none>          )
 ( delta                : <none>,  1.000          )
 ( delta                : <none>, -1.000          )
 ( indent               :   1.600,  0.900,  0.300 )
 ( initial_search_depth :  -1.000                 )
 ( search_depth         :  -0.100                 )
 ( skim                 :   0.150                 )
 ( start_search         :   4.000,<none>          )
 ( start_search         :  -4.000,<none>          )
 ( start_search         : <none>,  2.000          )
 ( start_search         : <none>, -2.000          )
 ( stop_search          :   8.000,<none>          )
 ( stop_search          :  -8.000,<none>          )
 ( stop_search          : <none>,  4.500          )
 ( stop_search          : <none>, -4.500          )

 ( G55                  : #5241.x #5242.y #5243.z )
 ( SKIP_POS             : #5061.x #5062.y #5063.z )
 ( error                :  #101.x  #102.y         )
 ( its                  :  #103.x                 )
 ( wcs                  : #5241.x #5242.y #5243.z )


( Find center of plate in vice, )
( Search Constraints:           )
( start:                        )
(   -27.5, -13.0, -17.5         )
( boundary:                     )
(   x= [-8.0..-4.0]..[4.0..8.0] )
(   y= [-4.5..-2.0]..[2.0..4.5] )
(   z= [-3.0..-1.0]             )
( indent:                       )
(   1.6, 0.9, 0.3               )
( delta:                        )
(   1.0, 1.0                    )
  #100= #4014                     (     WCS[haas.G55] as wcs,     )
  G55
  T01 M06
  G65 P9832                       ( Probe on.                     )
  #5241= 0.                       (     haas.G55.xyz = [0, 0, 0]  )
  #5242= 0.
  #5243= 0.
  #101= 0.                        (     error = Var[2][0, 0]      )
  #102= 0.

( find top z roughly. )
  G90 G01 G55 F200. z0.           ( defs.goto[z=0]                )

( just above workpiece surface. )
  G90 G01 G55 F200. x-27.5 y-13.  ( defs.goto_down[sch.above]     )
  G90 G01 G55 F200. z-17.5
  G90 G31 G55 F40. z-18.5         ( defs.fast_work_probe[z=sch.above.z + sch.initial_search_depth])
( make wcs become ~0,0,0 at tdc )
  #5241= #5061                    ( wcs.xyz = +haas.SKIP_POS      )
  #5242= #5062
  #5243= #5063
  G90 G01 G55 F200. z0.15         ( defs.goto[z=sch.skim]         )

( now work.xyz should be 0, with z at skim )
( distance, physically roughly tdc         )

( Save bss at 103 )
  #103= 5.                        ( its = Var[abs[number_bumps] + 1])

( Fast find left edge:                     )
(  Starting from min possible dimension,   )
(  move probe leftwards by                 )
(  calculated delta. If surface not found, )
(  then done.                              )


/   #3006 = 101 (top of left)


  G90 G01 G55 F200. z0.15         ( defs.goto_up[sch.amin.xy * di.dxdy * 0.5, z=sch.skim])
  G90 G01 G55 F200. x-4.
N1000
  IF [#103 LE 0.] GOTO 1002       ( while its > 0:                )
  G91 G01 G55 F200. x-1.          (     defs.goto_rel[delta.xy]   )
  G90 G31 G55 F40. z-0.1          (     defs.fast_work_probe.all[z=sch.search_depth])
  IF [#5063 LT -0.08] GOTO 1001   (     if haas.SKIP_POS.z < sch.found_if_below:)
  G90 G01 G55 F200. z0.15         (     defs.goto[z=sch.skim]     )
  #103= #103 - 1.                 (     its -= 1                  )
  GOTO 1000
N1002
  #3000 = 101 (search for left failed)
N1001

( Accurately find left edge:      )
(  Back off a bit leftwards.      )
(  Move to search height.         )
(  Slowly probe towards the right )
(  edge.                          )
  G90 G01 G55 F200. z-0.1         ( defs.goto[z=sch.search_depth] )
  G91 G01 G55 F200. x-0.1         ( defs.goto_rel[sch.backoff.xy * di.dxdy])
  G91 G31 G55 M79 F10. x1.6       ( defs.slow_rel_probe[-sch.indent.xy * di.dxdy])
  #101= #101 + #5061              ( error[di.cur_axis] += haas.SKIP_POS[di.cur_axis])

( Above surface and in:                     )
(  Back off left edge, up to skim distance. )
(  Move towards center.                     )
  G91 G01 G55 F200. x-0.1         ( defs.goto_rel[sch.backoff.xy * di.dxdy])
  G90 G01 G55 F200. z0.15         ( defs.goto[z=sch.skim]         )
  G91 G01 G55 F200. x1.6          ( defs.goto_rel[-sch.indent.xy * di.dxdy])

( Restore bss to 103 )

( Save bss at 103 )
  #103= 3.5                       ( its = Var[abs[number_bumps] + 1])

( Fast find near edge:                     )
(  Starting from min possible dimension,   )
(  move probe nearwards by                 )
(  calculated delta. If surface not found, )
(  then done.                              )


/   #3006 = 101 (top of near)


  G90 G01 G55 F200. z0.15         ( defs.goto_up[sch.amin.xy * di.dxdy * 0.5, z=sch.skim])
  G90 G01 G55 F200. y-2.
N1003
  IF [#103 LE 0.] GOTO 1005       ( while its > 0:                )
  G91 G01 G55 F200. y-1.          (     defs.goto_rel[delta.xy]   )
  G90 G31 G55 F40. z-0.1          (     defs.fast_work_probe.all[z=sch.search_depth])
  IF [#5063 LT -0.08] GOTO 1004   (     if haas.SKIP_POS.z < sch.found_if_below:)
  G90 G01 G55 F200. z0.15         (     defs.goto[z=sch.skim]     )
  #103= #103 - 1.                 (     its -= 1                  )
  GOTO 1003
N1005
  #3000 = 101 (search for near failed)
N1004

( Accurately find near edge:    )
(  Back off a bit nearwards.    )
(  Move to search height.       )
(  Slowly probe towards the far )
(  edge.                        )
  G90 G01 G55 F200. z-0.1         ( defs.goto[z=sch.search_depth] )
  G91 G01 G55 F200. y-0.1         ( defs.goto_rel[sch.backoff.xy * di.dxdy])
  G91 G31 G55 M79 F10. y0.9       ( defs.slow_rel_probe[-sch.indent.xy * di.dxdy])
  #102= #102 + #5062              ( error[di.cur_axis] += haas.SKIP_POS[di.cur_axis])

( Above surface and in:                     )
(  Back off near edge, up to skim distance. )
(  Move towards center.                     )
  G91 G01 G55 F200. y-0.1         ( defs.goto_rel[sch.backoff.xy * di.dxdy])
  G90 G01 G55 F200. z0.15         ( defs.goto[z=sch.skim]         )
  G91 G01 G55 F200. y0.9          ( defs.goto_rel[-sch.indent.xy * di.dxdy])

( Restore bss to 103 )

( Save bss at 103 )
  #103= 3.5                       ( its = Var[abs[number_bumps] + 1])

( Fast find far edge:                      )
(  Starting from min possible dimension,   )
(  move probe farwards by                  )
(  calculated delta. If surface not found, )
(  then done.                              )


/   #3006 = 101 (top of far)


  G90 G01 G55 F200. z0.15         ( defs.goto_up[sch.amin.xy * di.dxdy * 0.5, z=sch.skim])
  G90 G01 G55 F200. y2.
N1006
  IF [#103 LE 0.] GOTO 1008       ( while its > 0:                )
  G91 G01 G55 F200. y1.           (     defs.goto_rel[delta.xy]   )
  G90 G31 G55 F40. z-0.1          (     defs.fast_work_probe.all[z=sch.search_depth])
  IF [#5063 LT -0.08] GOTO 1007   (     if haas.SKIP_POS.z < sch.found_if_below:)
  G90 G01 G55 F200. z0.15         (     defs.goto[z=sch.skim]     )
  #103= #103 - 1.                 (     its -= 1                  )
  GOTO 1006
N1008
  #3000 = 101 (search for far failed)
N1007

( Accurately find far edge:      )
(  Back off a bit farwards.      )
(  Move to search height.        )
(  Slowly probe towards the near )
(  edge.                         )
  G90 G01 G55 F200. z-0.1         ( defs.goto[z=sch.search_depth] )
  G91 G01 G55 F200. y0.1          ( defs.goto_rel[sch.backoff.xy * di.dxdy])
  G91 G31 G55 M79 F10. y-0.9      ( defs.slow_rel_probe[-sch.indent.xy * di.dxdy])
  #102= #102 + #5062              ( error[di.cur_axis] += haas.SKIP_POS[di.cur_axis])

( Above surface and in:                    )
(  Back off far edge, up to skim distance. )
(  Move towards center.                    )
  G91 G01 G55 F200. y0.1          ( defs.goto_rel[sch.backoff.xy * di.dxdy])
  G90 G01 G55 F200. z0.15         ( defs.goto[z=sch.skim]         )
  G91 G01 G55 F200. y-0.9         ( defs.goto_rel[-sch.indent.xy * di.dxdy])

( Restore bss to 103 )
  G90 G01 G55 F200. x0. y0.       ( defs.goto[0, 0]               )

( Save bss at 103 )
  #103= 5.                        ( its = Var[abs[number_bumps] + 1])

( Fast find right edge:                    )
(  Starting from min possible dimension,   )
(  move probe rightwards by                )
(  calculated delta. If surface not found, )
(  then done.                              )


/   #3006 = 101 (top of right)


  G90 G01 G55 F200. z0.15         ( defs.goto_up[sch.amin.xy * di.dxdy * 0.5, z=sch.skim])
  G90 G01 G55 F200. x4.
N1009
  IF [#103 LE 0.] GOTO 1011       ( while its > 0:                )
  G91 G01 G55 F200. x1.           (     defs.goto_rel[delta.xy]   )
  G90 G31 G55 F40. z-0.1          (     defs.fast_work_probe.all[z=sch.search_depth])
  IF [#5063 LT -0.08] GOTO 1010   (     if haas.SKIP_POS.z < sch.found_if_below:)
  G90 G01 G55 F200. z0.15         (     defs.goto[z=sch.skim]     )
  #103= #103 - 1.                 (     its -= 1                  )
  GOTO 1009
N1011
  #3000 = 101 (search for right failed)
N1010

( Accurately find right edge:    )
(  Back off a bit rightwards.    )
(  Move to search height.        )
(  Slowly probe towards the left )
(  edge.                         )
  G90 G01 G55 F200. z-0.1         ( defs.goto[z=sch.search_depth] )
  G91 G01 G55 F200. x0.1          ( defs.goto_rel[sch.backoff.xy * di.dxdy])
  G91 G31 G55 M79 F10. x-1.6      ( defs.slow_rel_probe[-sch.indent.xy * di.dxdy])
  #101= #101 + #5061              ( error[di.cur_axis] += haas.SKIP_POS[di.cur_axis])

( Above surface and in:                      )
(  Back off right edge, up to skim distance. )
(  Move towards center.                      )
  G91 G01 G55 F200. x0.1          ( defs.goto_rel[sch.backoff.xy * di.dxdy])
  G90 G01 G55 F200. z0.15         ( defs.goto[z=sch.skim]         )
  G91 G01 G55 F200. x-1.6         ( defs.goto_rel[-sch.indent.xy * di.dxdy])

( Restore bss to 103 )

( The x coordinates of the left and right  )
( edge have been summed and put into       )
( error[0]. That value is double the error )
( of the first guess, since every bit of   )
( error shifts the apparent locations of   )
( the left and right side [if the          )
( workpiece was exactly placed under the   )
( first approximation, the left and right  )
( coordinats would have been equal and     )
( opposite, so the sum would be zero. The  )
( same is true for error[1], for far and   )
( near.                                    )
  #5241= #5241 + #101 / 2.        ( wcs.xy += error.xy / 2.0      )
  #5242= #5242 + #102 / 2.
  G90 G01 G55 F200. x0. y0.       ( defs.goto[0, 0]               )

(  final slow probe to find the surface z )
  G91 G31 G55 M79 F10. z-0.1      ( defs.slow_rel_probe[z=sch.search_depth])
  #5243= #5243 + #5063            ( wcs.z += haas.SKIP_POS.z      )
  G90 G01 G55 F200. z1.           ( defs.goto[z=1]                )

  #3006 = 101 ( what changed)


( find top z roughly. )
  G90 G01 G55 F200. z0.           ( defs.goto[z=0]                )

( just above workpiece surface. )
  G90 G01 G55 F200. x-27.5 y-13.  ( defs.goto_down[sch.above]     )
  G90 G01 G55 F200. z-17.5
  G90 G31 G55 F40. z-18.5         ( defs.fast_work_probe[z=sch.above.z + sch.initial_search_depth])
( make wcs become ~0,0,0 at tdc )
  #5241= #5061                    ( wcs.xyz = +haas.SKIP_POS      )
  #5242= #5062
  #5243= #5063
  G90 G01 G55 F200. z0.15         ( defs.goto[z=sch.skim]         )

( now work.xyz should be 0, with z at skim )
( distance, physically roughly tdc         )

( Save bss at 103 )
  #103= 5.                        ( its = Var[abs[number_bumps] + 1])

( Fast find left edge:                     )
(  Starting from min possible dimension,   )
(  move probe leftwards by                 )
(  calculated delta. If surface not found, )
(  then done.                              )


/   #3006 = 101 (top of left)


  G90 G01 G55 F200. z0.15         ( defs.goto_up[sch.amin.xy * di.dxdy * 0.5, z=sch.skim])
  G90 G01 G55 F200. x-4.
N1012
  IF [#103 LE 0.] GOTO 1014       ( while its > 0:                )
  G91 G01 G55 F200. x-1.          (     defs.goto_rel[delta.xy]   )
  G90 G31 G55 F40. z-0.1          (     defs.fast_work_probe.all[z=sch.search_depth])
  IF [#5063 LT -0.08] GOTO 1013   (     if haas.SKIP_POS.z < sch.found_if_below:)
  G90 G01 G55 F200. z0.15         (     defs.goto[z=sch.skim]     )
  #103= #103 - 1.                 (     its -= 1                  )
  GOTO 1012
N1014
  #3000 = 101 (search for left failed)
N1013

( Accurately find left edge:      )
(  Back off a bit leftwards.      )
(  Move to search height.         )
(  Slowly probe towards the right )
(  edge.                          )
  G90 G01 G55 F200. z-0.1         ( defs.goto[z=sch.search_depth] )
  G91 G01 G55 F200. x-0.1         ( defs.goto_rel[sch.backoff.xy * di.dxdy])
  G91 G31 G55 M79 F10. x1.6       ( defs.slow_rel_probe[-sch.indent.xy * di.dxdy])
  #101= #101 + #5061              ( error[di.cur_axis] += haas.SKIP_POS[di.cur_axis])

( Above surface and in:                     )
(  Back off left edge, up to skim distance. )
(  Move towards center.                     )
  G91 G01 G55 F200. x-0.1         ( defs.goto_rel[sch.backoff.xy * di.dxdy])
  G90 G01 G55 F200. z0.15         ( defs.goto[z=sch.skim]         )
  G91 G01 G55 F200. x1.6          ( defs.goto_rel[-sch.indent.xy * di.dxdy])

( Restore bss to 103 )

( Save bss at 103 )
  #103= 3.5                       ( its = Var[abs[number_bumps] + 1])

( Fast find near edge:                     )
(  Starting from min possible dimension,   )
(  move probe nearwards by                 )
(  calculated delta. If surface not found, )
(  then done.                              )


/   #3006 = 101 (top of near)


  G90 G01 G55 F200. z0.15         ( defs.goto_up[sch.amin.xy * di.dxdy * 0.5, z=sch.skim])
  G90 G01 G55 F200. y-2.
N1015
  IF [#103 LE 0.] GOTO 1017       ( while its > 0:                )
  G91 G01 G55 F200. y-1.          (     defs.goto_rel[delta.xy]   )
  G90 G31 G55 F40. z-0.1          (     defs.fast_work_probe.all[z=sch.search_depth])
  IF [#5063 LT -0.08] GOTO 1016   (     if haas.SKIP_POS.z < sch.found_if_below:)
  G90 G01 G55 F200. z0.15         (     defs.goto[z=sch.skim]     )
  #103= #103 - 1.                 (     its -= 1                  )
  GOTO 1015
N1017
  #3000 = 101 (search for near failed)
N1016

( Accurately find near edge:    )
(  Back off a bit nearwards.    )
(  Move to search height.       )
(  Slowly probe towards the far )
(  edge.                        )
  G90 G01 G55 F200. z-0.1         ( defs.goto[z=sch.search_depth] )
  G91 G01 G55 F200. y-0.1         ( defs.goto_rel[sch.backoff.xy * di.dxdy])
  G91 G31 G55 M79 F10. y0.9       ( defs.slow_rel_probe[-sch.indent.xy * di.dxdy])
  #102= #102 + #5062              ( error[di.cur_axis] += haas.SKIP_POS[di.cur_axis])

( Above surface and in:                     )
(  Back off near edge, up to skim distance. )
(  Move towards center.                     )
  G91 G01 G55 F200. y-0.1         ( defs.goto_rel[sch.backoff.xy * di.dxdy])
  G90 G01 G55 F200. z0.15         ( defs.goto[z=sch.skim]         )
  G91 G01 G55 F200. y0.9          ( defs.goto_rel[-sch.indent.xy * di.dxdy])

( Restore bss to 103 )

( Save bss at 103 )
  #103= 3.5                       ( its = Var[abs[number_bumps] + 1])

( Fast find far edge:                      )
(  Starting from min possible dimension,   )
(  move probe farwards by                  )
(  calculated delta. If surface not found, )
(  then done.                              )


/   #3006 = 101 (top of far)


  G90 G01 G55 F200. z0.15         ( defs.goto_up[sch.amin.xy * di.dxdy * 0.5, z=sch.skim])
  G90 G01 G55 F200. y2.
N1018
  IF [#103 LE 0.] GOTO 1020       ( while its > 0:                )
  G91 G01 G55 F200. y1.           (     defs.goto_rel[delta.xy]   )
  G90 G31 G55 F40. z-0.1          (     defs.fast_work_probe.all[z=sch.search_depth])
  IF [#5063 LT -0.08] GOTO 1019   (     if haas.SKIP_POS.z < sch.found_if_below:)
  G90 G01 G55 F200. z0.15         (     defs.goto[z=sch.skim]     )
  #103= #103 - 1.                 (     its -= 1                  )
  GOTO 1018
N1020
  #3000 = 101 (search for far failed)
N1019

( Accurately find far edge:      )
(  Back off a bit farwards.      )
(  Move to search height.        )
(  Slowly probe towards the near )
(  edge.                         )
  G90 G01 G55 F200. z-0.1         ( defs.goto[z=sch.search_depth] )
  G91 G01 G55 F200. y0.1          ( defs.goto_rel[sch.backoff.xy * di.dxdy])
  G91 G31 G55 M79 F10. y-0.9      ( defs.slow_rel_probe[-sch.indent.xy * di.dxdy])
  #102= #102 + #5062              ( error[di.cur_axis] += haas.SKIP_POS[di.cur_axis])

( Above surface and in:                    )
(  Back off far edge, up to skim distance. )
(  Move towards center.                    )
  G91 G01 G55 F200. y0.1          ( defs.goto_rel[sch.backoff.xy * di.dxdy])
  G90 G01 G55 F200. z0.15         ( defs.goto[z=sch.skim]         )
  G91 G01 G55 F200. y-0.9         ( defs.goto_rel[-sch.indent.xy * di.dxdy])

( Restore bss to 103 )
  G90 G01 G55 F200. x0. y0.       ( defs.goto[0, 0]               )

( Save bss at 103 )
  #103= 5.                        ( its = Var[abs[number_bumps] + 1])

( Fast find right edge:                    )
(  Starting from min possible dimension,   )
(  move probe rightwards by                )
(  calculated delta. If surface not found, )
(  then done.                              )


/   #3006 = 101 (top of right)


  G90 G01 G55 F200. z0.15         ( defs.goto_up[sch.amin.xy * di.dxdy * 0.5, z=sch.skim])
  G90 G01 G55 F200. x4.
N1021
  IF [#103 LE 0.] GOTO 1023       ( while its > 0:                )
  G91 G01 G55 F200. x1.           (     defs.goto_rel[delta.xy]   )
  G90 G31 G55 F40. z-0.1          (     defs.fast_work_probe.all[z=sch.search_depth])
  IF [#5063 LT -0.08] GOTO 1022   (     if haas.SKIP_POS.z < sch.found_if_below:)
  G90 G01 G55 F200. z0.15         (     defs.goto[z=sch.skim]     )
  #103= #103 - 1.                 (     its -= 1                  )
  GOTO 1021
N1023
  #3000 = 101 (search for right failed)
N1022

( Accurately find right edge:    )
(  Back off a bit rightwards.    )
(  Move to search height.        )
(  Slowly probe towards the left )
(  edge.                         )
  G90 G01 G55 F200. z-0.1         ( defs.goto[z=sch.search_depth] )
  G91 G01 G55 F200. x0.1          ( defs.goto_rel[sch.backoff.xy * di.dxdy])
  G91 G31 G55 M79 F10. x-1.6      ( defs.slow_rel_probe[-sch.indent.xy * di.dxdy])
  #101= #101 + #5061              ( error[di.cur_axis] += haas.SKIP_POS[di.cur_axis])

( Above surface and in:                      )
(  Back off right edge, up to skim distance. )
(  Move towards center.                      )
  G91 G01 G55 F200. x0.1          ( defs.goto_rel[sch.backoff.xy * di.dxdy])
  G90 G01 G55 F200. z0.15         ( defs.goto[z=sch.skim]         )
  G91 G01 G55 F200. x-1.6         ( defs.goto_rel[-sch.indent.xy * di.dxdy])

( Restore bss to 103 )

( The x coordinates of the left and right  )
( edge have been summed and put into       )
( error[0]. That value is double the error )
( of the first guess, since every bit of   )
( error shifts the apparent locations of   )
( the left and right side [if the          )
( workpiece was exactly placed under the   )
( first approximation, the left and right  )
( coordinats would have been equal and     )
( opposite, so the sum would be zero. The  )
( same is true for error[1], for far and   )
( near.                                    )
  #5241= #5241 + #101 / 2.        ( wcs.xy += error.xy / 2.0      )
  #5242= #5242 + #102 / 2.
  G90 G01 G55 F200. x0. y0.       ( defs.goto[0, 0]               )

(  final slow probe to find the surface z )
  G91 G31 G55 M79 F10. z-0.1      ( defs.slow_rel_probe[z=sch.search_depth])
  #5243= #5243 + #5063            ( wcs.z += haas.SKIP_POS.z      )
  G90 G01 G55 F200. z1.           ( defs.goto[z=1]                )

  #3006 = 101 ( what changed)

  G65 P9833                       ( Probe off.                    )
  G[# 100]                        ( Restore wcs                   )
  M30
%
