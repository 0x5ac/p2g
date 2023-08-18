import p2g

# stop with alarm code showing largest
# flute count in table.


def maxflutes():

    mx_flutes = p2g.Var(p2g.haas.TOOL_TBL_FLUTES[0])
    for n_flutes in p2g.haas.TOOL_TBL_FLUTES[1:]:
        if n_flutes > mx_flutes:
            mx_flutes = n_flutes

    p2g.haas.MESSAGE.var = mx_flutes
