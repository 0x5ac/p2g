  O0001                           ( VICECENTER                    )
( Find center of plate in vice, )
(  result in [#5241]            )
( Search Constraints:           )
( start:                        )
(   -28.0, -13.0, -16.0         )
( boundary:                     )
(   x= [-7.0..-3.5]..[3.5..7.0] )
(   y= [-4.0..-2.0]..[2.0..4.0] )
(   z= [-3.0..5.0]              )
( indent:                       )
(   1.4, 0.8, 0.3               )
( delta:                        )
(   0.75, 0.4                   )
( MACHINE_ABS_ABOVE_VICE : -28.,-10.,-16.            )
( slow_probe             : probe M79 work xyz  10.0  )
( fast_probe             : probe M79 work xyz  100.0 )
( goto                   :   work xyz  650.0         )
( WCS                    : #5241.x                   )
( tlc                    :                           )
( brc                    :                           )
( cursor                 :  #104.x  #105.y           )
( error                  :                           )
  T01 M06                         ( st.setup_probing[]            )
  G65 P9832
  G103 P1
  G04 P1
  G04 P1
  G04 P1
  G55                             ( set_wcs[st.WCS]               )
  G01 G90 G53 F650. z0.           ( st..machine[z=0]              )
  G01 G90 G53 F650. x-28. y-13.   ( st..machine.xy_then_z[sch.above])
  G01 G90 G53 F650. z-16.
( find top z roughly set [#5241].z. )
  #5241= #5021                    ( st.WCS.xyz = MACHINE_POS.xyz  )
  #5242= #5022
  #5243= #5023
  G01 G90 G31 M79 F100. z-5.      ( st.fast_probe[z=sch.amin.z]   )
  #5243= #5023                    ( st.WCS.z = MACHINE_POS.z      )
  #3006= 101.                     ( check g55                     )
( now work.z should be 0 at surface )
( and work.xy roughly middle        )
  G01 G90 F650. z0.3              ( st.[z=sch.skim_distance]      )
  #104= 0.                        ( st.cursor = Var[2][0, 0]      )
  #105= 0.
(                                      )
( quickly move probe to find left edge )
  #106= 5.6667                    (     [abs[stop_search - start_search] / sch.delta][di.cur_axis] + 1,)
  #104= -3.5                      ( cursor[di.cur_axis] = start_search[di.cur_axis])
L2000                             ( while its > 0:                )
  IF [#106 LE 0.] GOTO 2002
  G01 G90 F650. x#104 y#105       (     st.[cursor]               )
  G01 G90 G31 M79 F100. z-0.1     (     st.fast_probe[z=sch.search_depth])
  IF [#5063 LT -0.075] GOTO 2001  (     if SKIP_POS.z < sch.search_depth + sch.iota:)
  #104= #104 - 0.75               (     cursor.xy += delta        )
  #106= #106 - 1.                 (     its -= 1                  )
  GOTO 2000
L2002
  #3000= 101.                     ( search for left failed        )
L2001                             (     st.alarm[f"search for {di.name} failed"])
( back off a bit to the left, then slowly probe  )
( rightwards for precise measurement.            )
  #104= #104 - 0.1                ( cursor.xy += sch.backoff * di.dxdy)
  G01 G90 F650. x#104 y#105       ( st.[cursor.xy]                )
  G01 G90 G31 M79 F10. x0. y0.    ( st.slow_probe[[0, 0]]         )
  #100= #5061 - #556              ( output[di.cur_axis] = [SKIP_POS + PROBE_R * di.dxdy][di.cur_axis])
( reposition above surface skim height, )
( just inside left edge                 )
  G01 G91 F650. x-0.1 y0.         ( st..relative[sch.backoff.xy * di.dxdy])
  G01 G90 F650. z0.3              ( st.[z=sch.skim_distance]      )
  #104= #104 + 1.4                ( cursor.xy += -sch.indent.xy * di.dxdy)
  G01 G90 F650. x#104 y#105       ( st.[cursor]                   )
(                                      )
( quickly move probe to find near edge )
  #106= 6.                        (     [abs[stop_search - start_search] / sch.delta][di.cur_axis] + 1,)
  #105= -2.                       ( cursor[di.cur_axis] = start_search[di.cur_axis])
L2003                             ( while its > 0:                )
  IF [#106 LE 0.] GOTO 2005
  G01 G90 F650. x#104 y#105       (     st.[cursor]               )
  G01 G90 G31 M79 F100. z-0.1     (     st.fast_probe[z=sch.search_depth])
  IF [#5063 LT -0.075] GOTO 2004  (     if SKIP_POS.z < sch.search_depth + sch.iota:)
  #105= #105 - 0.4                (     cursor.xy += delta        )
  #106= #106 - 1.                 (     its -= 1                  )
  GOTO 2003
L2005
  #3000= 101.                     ( search for near failed        )
L2004                             (     st.alarm[f"search for {di.name} failed"])
( back off a bit to the near, then slowly probe  )
( farwards for precise measurement.              )
  #105= #105 - 0.1                ( cursor.xy += sch.backoff * di.dxdy)
  G01 G90 F650. x#104 y#105       ( st.[cursor.xy]                )
  G01 G90 G31 M79 F10. x0. y0.    ( st.slow_probe[[0, 0]]         )
  #103= #5062 - #557              ( output[di.cur_axis] = [SKIP_POS + PROBE_R * di.dxdy][di.cur_axis])
( reposition above surface skim height, )
( just inside near edge                 )
  G01 G91 F650. x0. y-0.1         ( st..relative[sch.backoff.xy * di.dxdy])
  G01 G90 F650. z0.3              ( st.[z=sch.skim_distance]      )
  #105= #105 + 0.8                ( cursor.xy += -sch.indent.xy * di.dxdy)
  G01 G90 F650. x#104 y#105       ( st.[cursor]                   )
(                                     )
( quickly move probe to find far edge )
  #106= 6.                        (     [abs[stop_search - start_search] / sch.delta][di.cur_axis] + 1,)
  #105= 2.                        ( cursor[di.cur_axis] = start_search[di.cur_axis])
L2006                             ( while its > 0:                )
  IF [#106 LE 0.] GOTO 2008
  G01 G90 F650. x#104 y#105       (     st.[cursor]               )
  G01 G90 G31 M79 F100. z-0.1     (     st.fast_probe[z=sch.search_depth])
  IF [#5063 LT -0.075] GOTO 2007  (     if SKIP_POS.z < sch.search_depth + sch.iota:)
  #105= #105 + 0.4                (     cursor.xy += delta        )
  #106= #106 - 1.                 (     its -= 1                  )
  GOTO 2006
L2008
  #3000= 101.                     ( search for far failed         )
L2007                             (     st.alarm[f"search for {di.name} failed"])
( back off a bit to the far, then slowly probe  )
( nearwards for precise measurement.            )
  #105= #105 + 0.1                ( cursor.xy += sch.backoff * di.dxdy)
  G01 G90 F650. x#104 y#105       ( st.[cursor.xy]                )
  G01 G90 G31 M79 F10. x0. y0.    ( st.slow_probe[[0, 0]]         )
  #101= #5062 + #557              ( output[di.cur_axis] = [SKIP_POS + PROBE_R * di.dxdy][di.cur_axis])
( reposition above surface skim height, )
( just inside far edge                  )
  G01 G91 F650. x0. y0.1          ( st..relative[sch.backoff.xy * di.dxdy])
  G01 G90 F650. z0.3              ( st.[z=sch.skim_distance]      )
  #105= #105 - 0.8                ( cursor.xy += -sch.indent.xy * di.dxdy)
  G01 G90 F650. x#104 y#105       ( st.[cursor]                   )
  G01 G90 F650. x0. y0.           ( st.[0, 0]                     )
(                                       )
( quickly move probe to find right edge )
  #106= 5.6667                    (     [abs[stop_search - start_search] / sch.delta][di.cur_axis] + 1,)
  #104= 3.5                       ( cursor[di.cur_axis] = start_search[di.cur_axis])
L2009                             ( while its > 0:                )
  IF [#106 LE 0.] GOTO 2011
  G01 G90 F650. x#104 y#105       (     st.[cursor]               )
  G01 G90 G31 M79 F100. z-0.1     (     st.fast_probe[z=sch.search_depth])
  IF [#5063 LT -0.075] GOTO 2010  (     if SKIP_POS.z < sch.search_depth + sch.iota:)
  #104= #104 + 0.75               (     cursor.xy += delta        )
  #106= #106 - 1.                 (     its -= 1                  )
  GOTO 2009
L2011
  #3000= 101.                     ( search for right failed       )
L2010                             (     st.alarm[f"search for {di.name} failed"])
( back off a bit to the right, then slowly probe  )
( leftwards for precise measurement.              )
  #104= #104 + 0.1                ( cursor.xy += sch.backoff * di.dxdy)
  G01 G90 F650. x#104 y#105       ( st.[cursor.xy]                )
  G01 G90 G31 M79 F10. x0. y0.    ( st.slow_probe[[0, 0]]         )
  #102= #5061 + #556              ( output[di.cur_axis] = [SKIP_POS + PROBE_R * di.dxdy][di.cur_axis])
( reposition above surface skim height, )
( just inside right edge                )
  G01 G91 F650. x0.1 y0.          ( st..relative[sch.backoff.xy * di.dxdy])
  G01 G90 F650. z0.3              ( st.[z=sch.skim_distance]      )
  #104= #104 - 1.4                ( cursor.xy += -sch.indent.xy * di.dxdy)
  G01 G90 F650. x#104 y#105       ( st.[cursor]                   )
(  the 'error' between 0,0 and where we )
(  calculate the center to be gets      )
(  added to cos and voila.              )
  #106= [#100 + #102] / 2.        ( st.error = Var[2][[st.tlc + st.brc] / 2.0])
  #107= [#101 + #103] / 2.
  #5241= #5241 + #106             ( st.WCS.xy += st.error.xy      )
  #5242= #5242 + #107
  G01 G90 F650. x0. y0.           ( st.[0, 0]                     )
(  final slow probe to find the surface z )
  G01 G90 G31 M79 F10. z-0.1      ( st.slow_probe[z=sch.search_depth])
  #5243= #5063                    ( st.WCS.z = SKIP_POS.z         )
  G01 G90 G53 F650. z-16.         ( st..machine[z=sch.above.z]    )
  #3000= 103.                     (  what changed                 )
  M30                             ( st.alarm[" what changed", 103])
