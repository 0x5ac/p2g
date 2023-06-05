( Start with fixed height probe,   )
( make sure probe stickout <2.25in )
( MACHINE_ABS_ABOVE_OTS       : -1.16,-7.5,-8.    )
( MACHINE_ABS_ABOVE_RING      : -16.46,-3.5,-22.7 )
( MACHINE_ABS_CLOSE_ABOVE_OTS : -1.16,-7.5,-7.6   )
( goto                        :   work xyz  650.0 )
( st.load_tool[defs.Tool.KNOWN_LENGTH])
  T02 M06
( st.ots_on[]                   )
  M59 P2
  G04 P1.0
  M59 P3
( st.[z=0]                      )
  G01 G90 F650. z0.
( touch OTS, must beep          )
  #3006= 101.
( st..machine.xy_then_z[st.MACHINE_ABS_ABOVE_OTS])
  G01 G90 G53 F650. x-1.16 y-7.5
  G01 G90 G53 F650. z-8.
( Make sure tool position looks safe.)
  #3006= 101.
( st..machine[z=st.MACHINE_ABS_CLOSE_ABOVE_OTS.z])
  G01 G90 G53 F650. z-7.6
( st.ots_calibrate[]            )
  G65 P9023 A20. K5. S0.5 D-2.
( Calibrate spindle probe. )
( st.load_tool[defs.Tool.PROBE] )
  T01 M06
( st.spindle_probe_on[]         )
  P9832
( touch probe, must beep        )
  #3006= 101.
( test spindle probe with OTS. )
( st..machine[z=0]              )
  G01 G90 G53 F650. z0.
( st..machine.xy_then_z[st.MACHINE_ABS_ABOVE_OTS])
  G01 G90 G53 F650. x-1.16 y-7.5
  G01 G90 G53 F650. z-8.
( st.spindle_probe_find_height[])
  G65 P9023 A21. T1.
( test spindle probe with ring. )
( st..machine[z=0]              )
  G01 G90 G53 F650. z0.
( st..machine.xy_then_z[st.MACHINE_ABS_ABOVE_RING])
  G01 G90 G53 F650. x-16.46 y-3.5
  G01 G90 G53 F650. z-22.7
( st.spindle_probe_find_radius[])
  G65 P9023 A10.0 D0.7
( st..machine[z=0]              )
  G01 G90 G53 F650. z0.