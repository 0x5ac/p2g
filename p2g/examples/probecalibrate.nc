  O0001                           ( PROBECALIBRATE                )
( Start with fixed height probe,   )
( make sure probe stickout <2.25in )
( MACHINE_ABS_ABOVE_OTS       : -1.16,-7.5,-8.    )
( MACHINE_ABS_ABOVE_RING      : -16.46,-3.5,-22.7 )
( MACHINE_ABS_CLOSE_ABOVE_OTS : -1.16,-7.5,-7.6   )
( goto                        :   work xyz  650.0 )
  T02 M06                         ( st.load_tool[defs.Tool.KNOWN_LENGTH])
  M59 P2                          ( st.ots_on[]                   )
  G04 P1.0
  M59 P3
  G01 G90 F650. z0.               ( st.[z=0]                      )
  #3006= 101.                     ( touch OTS, must beep          )
  G01 G90 G53 F650. x-1.16 y-7.5  ( st..machine.xy_then_z[st.MACHINE_ABS_ABOVE_OTS])
  G01 G90 G53 F650. z-8.
  #3006= 101.                     ( Make sure tool position looks safe.)
  G01 G90 G53 F650. z-7.6         ( st..machine[z=st.MACHINE_ABS_CLOSE_ABOVE_OTS.z])
  G65 P9023 A20. K5. S0.5 D-2.    ( st.ots_calibrate[]            )
( Calibrate spindle probe. )
  T01 M06                         ( st.load_tool[defs.Tool.PROBE] )
  P9832                           ( st.spindle_probe_on[]         )
  #3006= 101.                     ( touch probe, must beep        )
( test spindle probe with OTS. )
  G01 G90 G53 F650. z0.           ( st..machine[z=0]              )
  G01 G90 G53 F650. x-1.16 y-7.5  ( st..machine.xy_then_z[st.MACHINE_ABS_ABOVE_OTS])
  G01 G90 G53 F650. z-8.
  G65 P9023 A21. T1.              ( st.spindle_probe_find_height[])
( test spindle probe with ring. )
  G01 G90 G53 F650. z0.           ( st..machine[z=0]              )
  G01 G90 G53 F650. x-16.46 y-3.5 ( st..machine.xy_then_z[st.MACHINE_ABS_ABOVE_RING])
  G01 G90 G53 F650. z-22.7
  G65 P9023 A10.0 D0.7            ( st.spindle_probe_find_radius[])
  G01 G90 G53 F650. z0.           ( st..machine[z=0]              )
  M30
