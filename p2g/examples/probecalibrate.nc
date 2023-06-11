( MACHINE_ABS_ABOVE_OTS  :  -1.160, -7.500, -7.200 )
( MACHINE_ABS_ABOVE_RING : -16.460, -3.500,-22.700 )
  O0001                           ( PROBECALIBRATE                )

( Calibrate from known length tool,       )
( first macke sure OTS working, move tool )
( to above setter, and runs calibrate     )
( macro.                                  )
  T02 M06                         ( st.load_tool[defs.Tool.KNOWN_LENGTH])
  G65 P9855                       ( st.ots_on[]                   )
  G103 P1
  G01 G90 G53 F65. z0.            ( st.goto.machine[z=0]          )

  (# 3006) = 101 ( touch OTS, must beep )

  G01 G90 G53 F65. x-1.16 y-7.5   ( st.goto.machine.xy_then_z[st.MACHINE_ABS_ABOVE_OTS])
  G01 G90 G53 F65. z-7.2
  G65 P9023 A20. K5. S0.5 D-2.    ( st.ots_calibrate[]            )

( Calibrate the spindle probe.            )
( load spindle probe, makes sure the      )
( battery isn't flat, checks it over the  )
( tool setter, and then in the fixed ring )
  T01 M06                         ( st.load_tool[defs.Tool.PROBE] )
  G65                             ( st.spindle_probe_on[]         )
  P9832

  (# 3006) = 101 ( touch probe, must beep )


( test spindle probe with OTS )
  G01 G90 G53 F65. z0.            ( st.goto.machine[z=0]          )
  G01 G90 G53 F65. x-1.16 y-7.5   ( st.goto.machine.xy_then_z[st.MACHINE_ABS_ABOVE_OTS_FOR_PROBE])
  G01 G90 G53 F65. z-6.2
  G65 P9023 A21. T1.              ( st.spindle_probe_find_height[])

( test spindle probe with ring. )
  G01 G90 G53 F65. z0.            ( st.goto.machine[z=0]          )
  G01 G90 G53 F65. x-16.46 y-3.5  ( st.goto.machine.xy_then_z[st.MACHINE_ABS_ABOVE_RING])
  G01 G90 G53 F65. z-22.7
  G65 P9023 A10.0 D0.7            ( st.spindle_probe_find_radius[])
  G01 G90 G53 F65. z0.            ( st.goto.machine[z=0]          )
  M30
