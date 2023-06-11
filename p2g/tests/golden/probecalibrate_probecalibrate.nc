( MACHINE_ABS_ABOVE_OTS  :  -1.160, -7.500, -7.200 )
( MACHINE_ABS_ABOVE_RING : -16.460, -3.500,-22.700 )

( Calibrate from known length tool,       )
( first macke sure OTS working, move tool )
( to above setter, and runs calibrate     )
( macro.                                  )
( st.load_tool[defs.Tool.KNOWN_LENGTH])
  T02 M06
( st.ots_on[]                   )
  G65 P9855
  G103 P1
( st.goto.machine[z=0]          )
  G01 G90 G53 F65. z0.

  (# 3006) = 101 ( touch OTS, must beep )

( st.goto.machine.xy_then_z[st.MACHINE_ABS_ABOVE_OTS])
  G01 G90 G53 F65. x-1.16 y-7.5
  G01 G90 G53 F65. z-7.2
( st.ots_calibrate[]            )
  G65 P9023 A20. K5. S0.5 D-2.

( Calibrate the spindle probe.            )
( load spindle probe, makes sure the      )
( battery isn't flat, checks it over the  )
( tool setter, and then in the fixed ring )
( st.load_tool[defs.Tool.PROBE] )
  T01 M06
( st.spindle_probe_on[]         )
  G65
  P9832

  (# 3006) = 101 ( touch probe, must beep )


( test spindle probe with OTS )
( st.goto.machine[z=0]          )
  G01 G90 G53 F65. z0.
( st.goto.machine.xy_then_z[st.MACHINE_ABS_ABOVE_OTS_FOR_PROBE])
  G01 G90 G53 F65. x-1.16 y-7.5
  G01 G90 G53 F65. z-6.2
( st.spindle_probe_find_height[])
  G65 P9023 A21. T1.

( test spindle probe with ring. )
( st.goto.machine[z=0]          )
  G01 G90 G53 F65. z0.
( st.goto.machine.xy_then_z[st.MACHINE_ABS_ABOVE_RING])
  G01 G90 G53 F65. x-16.46 y-3.5
  G01 G90 G53 F65. z-22.7
( st.spindle_probe_find_radius[])
  G65 P9023 A10.0 D0.7
( st.goto.machine[z=0]          )
  G01 G90 G53 F65. z0.