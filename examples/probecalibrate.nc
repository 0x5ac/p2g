O0001 (probecalibrate: 0.2.104)
( Symbol Table )

 ( KNOWNLEN_OFF     :   0.000,  0.000, -0.250 )
 ( MABS_ABOVE_OTS   :  -1.167, -7.560, -7.540 )
 ( MABS_INSIDE_RING : -16.420, -3.420,-22.600 )


( Start with fixed height probe,   )
( make sure probe stickout <2.25in )
  G90 G53 G01 G55 F200. z0.       ( defs.goto_home[]              )
  G90 G53 G01 G55 F200. x0. y0.
  T02 M06                         ( with defs.OTS[]:              )
  M59 P2                          ( OTS On.                       )
  G04 P1.0
  M59 P3

  #3006 = 101 (touch OTS, must beep)

  G90 G01 G55 F200. x-1.167 y-7.56(     defs.goto_down[defs.MABS_ABOVE_OTS + defs.KNOWNLEN_OFF])
  G90 G01 G55 F200. z-7.79
  G65 P9023 A20. K5. S0.5 D-2.    (     defs.ots_calibrate[]      )
  M69 P2                          ( OTS Off.                      )
  M68 P3
  T01 M06                         ( with defs.Probe[]:            )
  G65 P9832                       ( Probe on.                     )

( Calibrate spindle probe. )

  #3006 = 101 (touch probe, must beep)

  G90 G53 G01 G55 F200. z0.       (     defs.goto_home[]          )
  G90 G53 G01 G55 F200. x0. y0.
  G90 G01 G55 F200. x-1.167 y-7.56(     defs.goto_down[defs.MABS_ABOVE_OTS])
  G90 G01 G55 F200. z-7.54
  G65 P9023 A21. T1.              (     defs.spindle_probe_find_height[])

( test spindle probe with ring. )
  G90 G53 G01 G55 F200. z0.       (     defs.goto_home[]          )
  G90 G53 G01 G55 F200. x0. y0.
  G90 G01 G55 F200. x-16.42 y-3.42(     defs.goto_down[defs.MABS_INSIDE_RING])
  G90 G01 G55 F200. z-22.6
  G65 P9023 A10.0 D0.7            (     defs.spindle_probe_find_radius[defs.PROBE_RING_DIAMETER])
  G90 G53 G01 G55 F200. z0.       (     defs.goto_home[]          )
  G90 G53 G01 G55 F200. x0. y0.
  G65 P9833                       ( Probe off.                    )
  M30
%
