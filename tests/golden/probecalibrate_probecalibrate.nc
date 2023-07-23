O00001 (probecalibrate)
( Symbol Table )

 ( KNOWNLEN_OFF     :   0.000,  0.000, -0.250 )
 ( MABS_ABOVE_OTS   :  -1.167, -7.560, -7.540 )
 ( MABS_INSIDE_RING : -16.420, -3.420,-22.600 )


( Start with fixed height probe,   )
( make sure probe stickout <2.25in )
( defs.goto_home[]              )
  G90 G53 G01 G55 F200. z0.
  G90 G53 G01 G55 F200. x0. y0.
( with defs.OTS[]:              )
  T02 M06
( OTS On.                       )
  M59 P2
  G04 P1.0
  M59 P3

  #3006 = 101 (touch OTS, must beep)

(     defs.goto_down[defs.MABS_ABOVE_OTS + defs.KNOWNLEN_OFF])
  G90 G01 G55 F200. x-1.167 y-7.56
  G90 G01 G55 F200. z-7.79
(     defs.ots_calibrate[]      )
  G65 P9023 A20. K5. S0.5 D-2.
( OTS Off.                      )
  M69 P2
  M68 P3
( with defs.Probe[]:            )
  T01 M06
( Probe on.                     )
  G65 P9832

( Calibrate spindle probe. )

  #3006 = 101 (touch probe, must beep)

(     defs.goto_home[]          )
  G90 G53 G01 G55 F200. z0.
  G90 G53 G01 G55 F200. x0. y0.
(     defs.goto_down[defs.MABS_ABOVE_OTS])
  G90 G01 G55 F200. x-1.167 y-7.56
  G90 G01 G55 F200. z-7.54
(     defs.spindle_probe_find_height[])
  G65 P9023 A21. T1.

( test spindle probe with ring. )
(     defs.goto_home[]          )
  G90 G53 G01 G55 F200. z0.
  G90 G53 G01 G55 F200. x0. y0.
(     defs.goto_down[defs.MABS_INSIDE_RING])
  G90 G01 G55 F200. x-16.42 y-3.42
  G90 G01 G55 F200. z-22.6
(     defs.spindle_probe_find_radius[defs.PROBE_RING_DIAMETER])
  G65 P9023 A10.0 D0.7
(     defs.goto_home[]          )
  G90 G53 G01 G55 F200. z0.
  G90 G53 G01 G55 F200. x0. y0.
( Probe off.                    )
  G65 P9833
  M30
%