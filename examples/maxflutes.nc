O00001 (maxflutes)
  #100= #1601                     ( mx_flutes = Var[haas.TOOL_TBL_FLUTES[0]])
  #101= 1601.                     ( for n_flutes in haas.TOOL_TBL_FLUTES:)
N1000
  IF [#101 GE 1801.] GOTO 1002    ( for n_flutes in haas.TOOL_TBL_FLUTES:)
  IF [#[#101] LE #100] GOTO 1003  (     if n_flutes > mx_flutes:  )
  #100= #[#101]                   (         mx_flutes = n_flutes  )
  GOTO 1004
N1003
N1004
  #101= #101 + 1.
  GOTO 1000
N1002
  #3006= #100                     ( haas.MESSAGE.var = mx_flutes  )
  M30
%