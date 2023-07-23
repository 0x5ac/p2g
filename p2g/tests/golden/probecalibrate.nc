( MACHINE_ABS_ABOVE_OTS       :  -1.160, -7.500, -7.500 )
( MACHINE_ABS_ABOVE_RING      : -16.460, -3.500,-22.700 )
( MACHINE_ABS_CLOSE_ABOVE_OTS :  -1.160, -7.500, -7.800 )

( Start with fixed height probe,   )
( make sure probe stickout <2.25in )
( st.load_tool[defs.Tool.KNOWN_LENGTH])
  T02 M06
( st.ots_on[]                   )
  M59 P2
  G04 P1.0
  M59 P3
( st.goto.machine[z=0]          )
  G01 G90 G53 F65. z0.

  (# 3006) = 101 ( touch OTS, must beep )

( st.goto.machine.xy_then_z[st.MACHINE_ABS_ABOVE_OTS])
  G01 G90 G53 F65. x-1.16 y-7.5
  G01 G90 G53 F65. z-7.5

  (# 3006) = 101 ( Make sure tool position looks safe. )

( st.goto.machine[z=st.MACHINE_ABS_CLOSE_ABOVE_OTS.z])
  G01 G90 G53 F65. z-7.8
( st.ots_calibrate[]            )
  G65 P9023 A20. K5. S0.5 D-2.

( Calibrate spindle probe. )
( st.load_tool[defs.Tool.PROBE] )
  T01 M06
( st.spindle_probe_on[]         )
  P9832

  (# 3006) = 101 ( touch probe, must beep )


( test spindle probe with OTS. )
( st.goto.machine[z=0]          )
  G01 G90 G53 F65. z0.
( st.goto.machine.xy_then_z[st.MACHINE_ABS_ABOVE_OTS])
  G01 G90 G53 F65. x-1.16 y-7.5
  G01 G90 G53 F65. z-7.5
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