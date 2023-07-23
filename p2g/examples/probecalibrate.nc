( MACHINE_ABS_ABOVE_OTS       :  -1.160, -7.500, -7.500 )
( MACHINE_ABS_ABOVE_RING      : -16.460, -3.500,-22.700 )
( MACHINE_ABS_CLOSE_ABOVE_OTS :  -1.160, -7.500, -7.800 )
( goto                        :   work xyz  65.0        )
( machine                     :   machine xyz  65.0     )
  O0001                           ( PROBECALIBRATE                )

( Start with fixed height probe,   )
( make sure probe stickout <2.25in )
  T02 M06                         ( st.load_tool[defs.Tool.KNOWN_LENGTH])
  M59 P2                          ( st.ots_on[]                   )
  G04 P1.0
  M59 P3
  G01 G90 G53 F65. z0.            ( st.goto.machine[z=0]          )

  (# 3006) = 101 ( touch OTS, must beep )

  G01 G90 G53 F65. x-1.16 y-7.5   ( st.goto.machine.xy_then_z[st.MACHINE_ABS_ABOVE_OTS])
  G01 G90 G53 F65. z-7.5

  (# 3006) = 101 ( Make sure tool position looks safe. )

  G01 G90 G53 F65. z-7.8          ( st.goto.machine[z=st.MACHINE_ABS_CLOSE_ABOVE_OTS.z])
  G65 P9023 A20. K5. S0.5 D-2.    ( st.ots_calibrate[]            )

( Calibrate spindle probe. )
  T01 M06                         ( st.load_tool[defs.Tool.PROBE] )
  P9832                           ( st.spindle_probe_on[]         )

  (# 3006) = 101 ( touch probe, must beep )


( test spindle probe with OTS. )
  G01 G90 G53 F65. z0.            ( st.goto.machine[z=0]          )
  G01 G90 G53 F65. x-1.16 y-7.5   ( st.goto.machine.xy_then_z[st.MACHINE_ABS_ABOVE_OTS])
  G01 G90 G53 F65. z-7.5
  G65 P9023 A21. T1.              ( st.spindle_probe_find_height[])

( test spindle probe with ring. )
  G01 G90 G53 F65. z0.            ( st.goto.machine[z=0]          )
  G01 G90 G53 F65. x-16.46 y-3.5  ( st.goto.machine.xy_then_z[st.MACHINE_ABS_ABOVE_RING])
  G01 G90 G53 F65. z-22.7
  G65 P9023 A10.0 D0.7            ( st.spindle_probe_find_radius[])
  G01 G90 G53 F65. z0.            ( st.goto.machine[z=0]          )
  M30
