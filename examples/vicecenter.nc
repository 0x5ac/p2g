( brc                    :  #102.x  #103.y             )
( cursor                 :  #104.x  #105.y             )
( error                  :  #106.x  #107.y             )
( G55                    : #5241.x #5242.y #5243.z     )
( its                    :  #106.x                     )
( MACHINE_POS            : #5021.x #5022.y #5023.z     )
( output                 :  #100.x  #101.y             )
( output                 :  #102.x  #103.y             )
( PROBE_R                :  #556.x  #557.y             )
( SKIP_POS               : #5061.x #5062.y #5063.z     )
( tlc                    :  #100.x  #101.y             )
( WCS                    : #5241.x #5242.y #5243.z     )
( amax                   :  14.000,  8.000,  3.000     )
( amin                   :   7.000,  4.000, -5.000     )
( backoff                :   0.100,  0.100,  0.100     )
( delta                  :   0.750,  0.400             )
( iota                   :   0.025,  0.025,  0.025     )
( MACHINE_ABS_ABOVE_VICE : -28.000,-10.000,-16.000     )
( start_search           :   0.000, -2.000             )
( start_search           :  -3.500,  0.000             )
( start_search           :   3.500,  0.000             )
( start_search           :   0.000,  2.000             )
( stop_search            :  -7.000,  0.000             )
( stop_search            :   0.000, -4.000             )
( stop_search            :   0.000,  4.000             )
( stop_search            :   7.000,  0.000             )
( fast_mabs_probe        : 10.0 M79 machine xyz probe  )
( slow_probe             : 10.0 M79 work xyz probe     )
  O0001                           ( vicecenter                    )

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
  T01 M06                         ( st.setup_probing[]            )
  G65 P9832
  G103 P1
  G04 P1
  G04 P1
  G04 P1
  G55                             ( set_wcs[st.WCS]               )
  G01 G53 G90 F65. z0.            ( st.goto.machine[z=0]          )
  G01 G53 G90 F65. x-28. y-13.    ( st.goto.machine.xy_then_z[sch.above])
  G01 G53 G90 F65. z-16.

( find top z roughly set [#5241].z. )
  #5241= #5021                    ( st.WCS.xyz = MACHINE_POS.xyz  )
  #5242= #5022
  #5243= #5023
  G01 G53 G90 G31 M79 F10. z-5.   ( st.fast_mabs_probe[z=sch.amin.z])
  #5243= #5023                    ( st.WCS.z = MACHINE_POS.z      )


  (# 3006) = 101 (check g55)



( now work.z should be 0 at surface )
( and work.xy roughly middle        )
  G01 G90 F65. z0.3               ( st.goto[z=sch.skim_distance]  )
  #104= 0.                        ( st.cursor = Var[2][0, 0]      )
  #105= 0.


( quickly move probe to find left edge )
  #106= 5.6667                    (     [abs[stop_search - start_search] / sch.delta][di.cur_axis] + 1,)
  #104= -3.5                      ( cursor[di.cur_axis] = start_search[di.cur_axis])
  G01 G90 F65. x#104 y#105        ( st.goto.xy_then_z[cursor]     )
N1000                             ( while its > 0:                )
  IF [#106 LE 0.] GOTO 1002
  G01 G90 F65. x#104 y#105        (     st.goto.z_then_xy[cursor] )
  G01 G53 G90 G31 M79 F10. z-0.1  (     st.fast_mabs_probe[z=sch.search_depth])
  IF [#5063 LT -0.075] GOTO 1001  (     if SKIP_POS.z < sch.search_depth + sch.iota:)
  #104= #104 - 0.75               (     cursor.xy += delta        )
  #106= #106 - 1.                 (     its -= 1                  )
  GOTO 1000
N1002


  (# 3000) = 101 (search for left failed)


N1001                             (     st.alarm[f"search for {di.name} failed"])

( back off a bit to the left, then slowly probe  )
( rightwards for precise measurement.            )
  #104= #104 - 0.1                ( cursor.xy += sch.backoff * di.dxdy)
  G01 G90 F65. x#104 y#105        ( st.goto[cursor.xy]            )
  G01 G53 G90 G31 M79 F10. x0. y0.( st.slow_mabs_probe[[0, 0]]    )
  #100= #5061 - #556              ( output[di.cur_axis] = [SKIP_POS + PROBE_R * di.dxdy][di.cur_axis])

( reposition above surface skim height, )
( just inside left edge                 )
  G01 G91 F65. x-0.1 y0.          ( st.goto.relative[sch.backoff.xy * di.dxdy])
  G01 G90 F65. z0.3               ( st.goto[z=sch.skim_distance]  )
  #104= #104 + 1.4                ( cursor.xy += -sch.indent.xy * di.dxdy)
  G01 G90 F65. x#104 y#105        ( st.goto[cursor]               )


( quickly move probe to find near edge )
  #106= 6.                        (     [abs[stop_search - start_search] / sch.delta][di.cur_axis] + 1,)
  #105= -2.                       ( cursor[di.cur_axis] = start_search[di.cur_axis])
  G01 G90 F65. x#104 y#105        ( st.goto.xy_then_z[cursor]     )
N1003                             ( while its > 0:                )
  IF [#106 LE 0.] GOTO 1005
  G01 G90 F65. x#104 y#105        (     st.goto.z_then_xy[cursor] )
  G01 G53 G90 G31 M79 F10. z-0.1  (     st.fast_mabs_probe[z=sch.search_depth])
  IF [#5063 LT -0.075] GOTO 1004  (     if SKIP_POS.z < sch.search_depth + sch.iota:)
  #105= #105 - 0.4                (     cursor.xy += delta        )
  #106= #106 - 1.                 (     its -= 1                  )
  GOTO 1003
N1005


  (# 3000) = 101 (search for near failed)


N1004                             (     st.alarm[f"search for {di.name} failed"])

( back off a bit to the near, then slowly probe  )
( farwards for precise measurement.              )
  #105= #105 - 0.1                ( cursor.xy += sch.backoff * di.dxdy)
  G01 G90 F65. x#104 y#105        ( st.goto[cursor.xy]            )
  G01 G53 G90 G31 M79 F10. x0. y0.( st.slow_mabs_probe[[0, 0]]    )
  #103= #5062 - #557              ( output[di.cur_axis] = [SKIP_POS + PROBE_R * di.dxdy][di.cur_axis])

( reposition above surface skim height, )
( just inside near edge                 )
  G01 G91 F65. x0. y-0.1          ( st.goto.relative[sch.backoff.xy * di.dxdy])
  G01 G90 F65. z0.3               ( st.goto[z=sch.skim_distance]  )
  #105= #105 + 0.8                ( cursor.xy += -sch.indent.xy * di.dxdy)
  G01 G90 F65. x#104 y#105        ( st.goto[cursor]               )


( quickly move probe to find far edge )
  #106= 6.                        (     [abs[stop_search - start_search] / sch.delta][di.cur_axis] + 1,)
  #105= 2.                        ( cursor[di.cur_axis] = start_search[di.cur_axis])
  G01 G90 F65. x#104 y#105        ( st.goto.xy_then_z[cursor]     )
N1006                             ( while its > 0:                )
  IF [#106 LE 0.] GOTO 1008
  G01 G90 F65. x#104 y#105        (     st.goto.z_then_xy[cursor] )
  G01 G53 G90 G31 M79 F10. z-0.1  (     st.fast_mabs_probe[z=sch.search_depth])
  IF [#5063 LT -0.075] GOTO 1007  (     if SKIP_POS.z < sch.search_depth + sch.iota:)
  #105= #105 + 0.4                (     cursor.xy += delta        )
  #106= #106 - 1.                 (     its -= 1                  )
  GOTO 1006
N1008


  (# 3000) = 101 (search for far failed)


N1007                             (     st.alarm[f"search for {di.name} failed"])

( back off a bit to the far, then slowly probe  )
( nearwards for precise measurement.            )
  #105= #105 + 0.1                ( cursor.xy += sch.backoff * di.dxdy)
  G01 G90 F65. x#104 y#105        ( st.goto[cursor.xy]            )
  G01 G53 G90 G31 M79 F10. x0. y0.( st.slow_mabs_probe[[0, 0]]    )
  #101= #5062 + #557              ( output[di.cur_axis] = [SKIP_POS + PROBE_R * di.dxdy][di.cur_axis])

( reposition above surface skim height, )
( just inside far edge                  )
  G01 G91 F65. x0. y0.1           ( st.goto.relative[sch.backoff.xy * di.dxdy])
  G01 G90 F65. z0.3               ( st.goto[z=sch.skim_distance]  )
  #105= #105 - 0.8                ( cursor.xy += -sch.indent.xy * di.dxdy)
  G01 G90 F65. x#104 y#105        ( st.goto[cursor]               )
  G01 G90 F65. x0. y0.            ( st.goto[0, 0]                 )


( quickly move probe to find right edge )
  #106= 5.6667                    (     [abs[stop_search - start_search] / sch.delta][di.cur_axis] + 1,)
  #104= 3.5                       ( cursor[di.cur_axis] = start_search[di.cur_axis])
  G01 G90 F65. x#104 y#105        ( st.goto.xy_then_z[cursor]     )
N1009                             ( while its > 0:                )
  IF [#106 LE 0.] GOTO 1011
  G01 G90 F65. x#104 y#105        (     st.goto.z_then_xy[cursor] )
  G01 G53 G90 G31 M79 F10. z-0.1  (     st.fast_mabs_probe[z=sch.search_depth])
  IF [#5063 LT -0.075] GOTO 1010  (     if SKIP_POS.z < sch.search_depth + sch.iota:)
  #104= #104 + 0.75               (     cursor.xy += delta        )
  #106= #106 - 1.                 (     its -= 1                  )
  GOTO 1009
N1011


  (# 3000) = 101 (search for right failed)


N1010                             (     st.alarm[f"search for {di.name} failed"])

( back off a bit to the right, then slowly probe  )
( leftwards for precise measurement.              )
  #104= #104 + 0.1                ( cursor.xy += sch.backoff * di.dxdy)
  G01 G90 F65. x#104 y#105        ( st.goto[cursor.xy]            )
  G01 G53 G90 G31 M79 F10. x0. y0.( st.slow_mabs_probe[[0, 0]]    )
  #102= #5061 + #556              ( output[di.cur_axis] = [SKIP_POS + PROBE_R * di.dxdy][di.cur_axis])

( reposition above surface skim height, )
( just inside right edge                )
  G01 G91 F65. x0.1 y0.           ( st.goto.relative[sch.backoff.xy * di.dxdy])
  G01 G90 F65. z0.3               ( st.goto[z=sch.skim_distance]  )
  #104= #104 - 1.4                ( cursor.xy += -sch.indent.xy * di.dxdy)
  G01 G90 F65. x#104 y#105        ( st.goto[cursor]               )

(  the 'error' between 0,0 and where we )
(  calculate the center to be gets      )
(  added to cos and voila.              )
  #106= [#100 + #102] / 2.        ( st.error = Var[2][[st.tlc + st.brc] / 2.0])
  #107= [#101 + #103] / 2.
  #5241= #5241 + #106             ( st.WCS.xy += st.error.xy      )
  #5242= #5242 + #107
  G01 G90 F65. x0. y0.            ( st.goto[0, 0]                 )

(  final slow probe to find the surface z )
  G01 G90 G31 M79 F10. z-0.1      ( st.slow_probe[z=sch.search_depth])
  #5243= #5063                    ( st.WCS.z = SKIP_POS.z         )
  G01 G53 G90 F65. z-16.          ( st.goto.machine[z=sch.above.z])


  (# 3000) = 101 ( what changed)


  M30
