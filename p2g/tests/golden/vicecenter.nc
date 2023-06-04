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
( st.setup_probing[]            )
  T01 M06
  G65 P9832
  G103 P1
  G04 P1
  G04 P1
  G04 P1
( set_wcs[st.WCS]               )
  G55
( st..machine[z=0]              )
  G01 G90 G53 F650. z0.
( st..machine.xy_then_z[sch.above])
  G01 G90 G53 F650. x-28. y-13.
  G01 G90 G53 F650. z-16.
( find top z roughly set [#5241].z. )
( st.WCS.xyz = MACHINE_POS.xyz  )
  #5241= #5021
  #5242= #5022
  #5243= #5023
( st.fast_probe[z=sch.amin.z]   )
  G01 G90 G31 M79 F100. z-5.
( st.WCS.z = MACHINE_POS.z      )
  #5243= #5023
( check g55                     )
  #3006= 101.
( now work.z should be 0 at surface )
( and work.xy roughly middle        )
( st.[z=sch.skim_distance]      )
  G01 G90 F650. z0.3
( st.cursor = Var[2][0, 0]      )
  #104= 0.
  #105= 0.
(                                      )
( quickly move probe to find left edge )
(     [abs[stop_search - start_search] / sch.delta][di.cur_axis] + 1,)
  #106= 5.6667
( cursor[di.cur_axis] = start_search[di.cur_axis])
  #104= -3.5
( while its > 0:                )
L1000
  IF [#106 LE 0.] GOTO 1002
(     st.[cursor]               )
  G01 G90 F650. x#104 y#105
(     st.fast_probe[z=sch.search_depth])
  G01 G90 G31 M79 F100. z-0.1
(     if SKIP_POS.z < sch.search_depth + sch.iota:)
  IF [#5063 LT -0.075] GOTO 1001
(     cursor.xy += delta        )
  #104= #104 - 0.75
(     its -= 1                  )
  #106= #106 - 1.
  GOTO 1000
L1002
( search for left failed        )
  #3000= 101.
(     st.alarm[f"search for {di.name} failed"])
L1001
( back off a bit to the left, then slowly probe  )
( rightwards for precise measurement.            )
( cursor.xy += sch.backoff * di.dxdy)
  #104= #104 - 0.1
( st.[cursor.xy]                )
  G01 G90 F650. x#104 y#105
( st.slow_probe[[0, 0]]         )
  G01 G90 G31 M79 F10. x0. y0.
( output[di.cur_axis] = [SKIP_POS + PROBE_R * di.dxdy][di.cur_axis])
  #100= #5061 - #556
( reposition above surface skim height, )
( just inside left edge                 )
( st..relative[sch.backoff.xy * di.dxdy])
  G01 G91 F650. x-0.1 y0.
( st.[z=sch.skim_distance]      )
  G01 G90 F650. z0.3
( cursor.xy += -sch.indent.xy * di.dxdy)
  #104= #104 + 1.4
( st.[cursor]                   )
  G01 G90 F650. x#104 y#105
(                                      )
( quickly move probe to find near edge )
(     [abs[stop_search - start_search] / sch.delta][di.cur_axis] + 1,)
  #106= 6.
( cursor[di.cur_axis] = start_search[di.cur_axis])
  #105= -2.
( while its > 0:                )
L1003
  IF [#106 LE 0.] GOTO 1005
(     st.[cursor]               )
  G01 G90 F650. x#104 y#105
(     st.fast_probe[z=sch.search_depth])
  G01 G90 G31 M79 F100. z-0.1
(     if SKIP_POS.z < sch.search_depth + sch.iota:)
  IF [#5063 LT -0.075] GOTO 1004
(     cursor.xy += delta        )
  #105= #105 - 0.4
(     its -= 1                  )
  #106= #106 - 1.
  GOTO 1003
L1005
( search for near failed        )
  #3000= 101.
(     st.alarm[f"search for {di.name} failed"])
L1004
( back off a bit to the near, then slowly probe  )
( farwards for precise measurement.              )
( cursor.xy += sch.backoff * di.dxdy)
  #105= #105 - 0.1
( st.[cursor.xy]                )
  G01 G90 F650. x#104 y#105
( st.slow_probe[[0, 0]]         )
  G01 G90 G31 M79 F10. x0. y0.
( output[di.cur_axis] = [SKIP_POS + PROBE_R * di.dxdy][di.cur_axis])
  #103= #5062 - #557
( reposition above surface skim height, )
( just inside near edge                 )
( st..relative[sch.backoff.xy * di.dxdy])
  G01 G91 F650. x0. y-0.1
( st.[z=sch.skim_distance]      )
  G01 G90 F650. z0.3
( cursor.xy += -sch.indent.xy * di.dxdy)
  #105= #105 + 0.8
( st.[cursor]                   )
  G01 G90 F650. x#104 y#105
(                                     )
( quickly move probe to find far edge )
(     [abs[stop_search - start_search] / sch.delta][di.cur_axis] + 1,)
  #106= 6.
( cursor[di.cur_axis] = start_search[di.cur_axis])
  #105= 2.
( while its > 0:                )
L1006
  IF [#106 LE 0.] GOTO 1008
(     st.[cursor]               )
  G01 G90 F650. x#104 y#105
(     st.fast_probe[z=sch.search_depth])
  G01 G90 G31 M79 F100. z-0.1
(     if SKIP_POS.z < sch.search_depth + sch.iota:)
  IF [#5063 LT -0.075] GOTO 1007
(     cursor.xy += delta        )
  #105= #105 + 0.4
(     its -= 1                  )
  #106= #106 - 1.
  GOTO 1006
L1008
( search for far failed         )
  #3000= 101.
(     st.alarm[f"search for {di.name} failed"])
L1007
( back off a bit to the far, then slowly probe  )
( nearwards for precise measurement.            )
( cursor.xy += sch.backoff * di.dxdy)
  #105= #105 + 0.1
( st.[cursor.xy]                )
  G01 G90 F650. x#104 y#105
( st.slow_probe[[0, 0]]         )
  G01 G90 G31 M79 F10. x0. y0.
( output[di.cur_axis] = [SKIP_POS + PROBE_R * di.dxdy][di.cur_axis])
  #101= #5062 + #557
( reposition above surface skim height, )
( just inside far edge                  )
( st..relative[sch.backoff.xy * di.dxdy])
  G01 G91 F650. x0. y0.1
( st.[z=sch.skim_distance]      )
  G01 G90 F650. z0.3
( cursor.xy += -sch.indent.xy * di.dxdy)
  #105= #105 - 0.8
( st.[cursor]                   )
  G01 G90 F650. x#104 y#105
( st.[0, 0]                     )
  G01 G90 F650. x0. y0.
(                                       )
( quickly move probe to find right edge )
(     [abs[stop_search - start_search] / sch.delta][di.cur_axis] + 1,)
  #106= 5.6667
( cursor[di.cur_axis] = start_search[di.cur_axis])
  #104= 3.5
( while its > 0:                )
L1009
  IF [#106 LE 0.] GOTO 1011
(     st.[cursor]               )
  G01 G90 F650. x#104 y#105
(     st.fast_probe[z=sch.search_depth])
  G01 G90 G31 M79 F100. z-0.1
(     if SKIP_POS.z < sch.search_depth + sch.iota:)
  IF [#5063 LT -0.075] GOTO 1010
(     cursor.xy += delta        )
  #104= #104 + 0.75
(     its -= 1                  )
  #106= #106 - 1.
  GOTO 1009
L1011
( search for right failed       )
  #3000= 101.
(     st.alarm[f"search for {di.name} failed"])
L1010
( back off a bit to the right, then slowly probe  )
( leftwards for precise measurement.              )
( cursor.xy += sch.backoff * di.dxdy)
  #104= #104 + 0.1
( st.[cursor.xy]                )
  G01 G90 F650. x#104 y#105
( st.slow_probe[[0, 0]]         )
  G01 G90 G31 M79 F10. x0. y0.
( output[di.cur_axis] = [SKIP_POS + PROBE_R * di.dxdy][di.cur_axis])
  #102= #5061 + #556
( reposition above surface skim height, )
( just inside right edge                )
( st..relative[sch.backoff.xy * di.dxdy])
  G01 G91 F650. x0.1 y0.
( st.[z=sch.skim_distance]      )
  G01 G90 F650. z0.3
( cursor.xy += -sch.indent.xy * di.dxdy)
  #104= #104 - 1.4
( st.[cursor]                   )
  G01 G90 F650. x#104 y#105
(  the 'error' between 0,0 and where we )
(  calculate the center to be gets      )
(  added to cos and voila.              )
( st.error = Var[2][[st.tlc + st.brc] / 2.0])
  #106= [#100 + #102] / 2.
  #107= [#101 + #103] / 2.
( st.WCS.xy += st.error.xy      )
  #5241= #5241 + #106
  #5242= #5242 + #107
( st.[0, 0]                     )
  G01 G90 F650. x0. y0.
(  final slow probe to find the surface z )
( st.slow_probe[z=sch.search_depth])
  G01 G90 G31 M79 F10. z-0.1
( st.WCS.z = SKIP_POS.z         )
  #5243= #5063
( st..machine[z=sch.above.z]    )
  G01 G90 G53 F650. z-16.
(  what changed                 )
  #3000= 103.