import ast
# just information about operators.
# pylint: disable=too-many-instance-attributes
import dataclasses
import typing


def opt_null(*_):
    return None


@dataclasses.dataclass(kw_only=True)
class Opinfo:
    astc: typing.Optional[typing.Type] = None
    pyn: str = ""
    mth: str = ""
    lam: typing.Callable = opt_null
    gname: str = ""
    prec: int = 20
    comm: bool = False
    nargs: int = 2
    g_func: bool = False

    opt1: typing.Callable = opt_null
    opt2: typing.Callable = opt_null


const_opinfo = Opinfo(astc=ast.Constant, pyn="konstant", gname="", prec=20)
