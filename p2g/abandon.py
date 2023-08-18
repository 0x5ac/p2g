import ast
import pathlib
import re
import sys

from p2g import axis
from p2g import err
from p2g import gbl
from p2g import stat
from p2g import symbol
from p2g import VERSION
from p2g import walkfunc


def find_desc(walker, func_name, srcpath):
    try:
        fncdef = walker.ns[func_name]
        desc = fncdef(walkfunc.Marker())
    except KeyError as exn:
        raise err.CompilerError(
            f"No such function '{func_name}' in '{srcpath}'."
        ) from exn
    return desc


def find_defined_funcs(sourcelines):
    for line in sourcelines:
        # find last line with def in it, that's the function we need
        mares = re.match("def (.*?)\\(", line)
        if mares:
            yield mares.group(1)


# make sure any def test_func is after the TESTS BELOW
# comment, or future sedding will make us sad.
def check_test_after_marker(sourcelines, node):
    if not gbl.config.in_pytestwant:
        return

    had_marker = False
    for line in sourcelines:
        if line.startswith("# TESTS BELOW"):
            had_marker = True
        if line.startswith("def test_"):
            if not had_marker:
                err.compiler(f"need TEST BELOW before {line}", node=node)


def find_main_func_name(sourcelines, func_name_arg):
    if func_name_arg != "<last>":
        return func_name_arg

    function_to_call = "no function in file"

    for fname in find_defined_funcs(sourcelines):
        function_to_call = fname

    return function_to_call


def digest_top(walker, func_name, srcpath):
    desc = find_desc(walker, func_name, srcpath)
    stat.add_stat(stat.Lazy(symbol.Table.yield_table()))

    walkfunc.inline(desc)
    stat.codenl(["M30"], comment_txt=stat.CommentGen.NONE)
    for handler in gbl.on_exit:
        handler()

    stat.add_stat(stat.Percent())
    #    stat.codenl(["%"], comment_txt=stat.CommentGen.NONE)
    return desc


@gbl.g2l
def compile2g(func_name_arg, srcfile_name, job_name):

    with stat.Nest() as cursor:
        try:
            axis.NAMES = "xyz"
            gbl.reset()
            symbol.Table.reset()

            src_path = pathlib.Path(srcfile_name)
            src_lines = gbl.get_lines(src_path)

            sys.path.insert(0, str(src_path.parent))

            gbl.log(f"Starting {func_name_arg} {cursor.next_label}")
            func_name = find_main_func_name(src_lines, func_name_arg)

            version = "" if gbl.config.no_id else f": {VERSION}"
            stat.code(
                f"{job_name} ({func_name}{version})",
                comment_txt=stat.CommentGen.NONE,
            )

            node = ast.parse("\n".join(src_lines), filename=srcfile_name)

            for el in ast.walk(node):
                gbl.set_ast_file_name(el, srcfile_name)

            # load everything

            walker = walkfunc.Walk()
            walker.visit_module(node, srcfile_name)

            if node.body:
                funcdef = digest_top(
                    walker,
                    func_name,
                    src_path,
                )

                check_test_after_marker(src_lines, funcdef.node)

            # careful with use of generators, because symbol table may
            # be emitted at the top, yet needs things used last on.
            res = list(cursor.to_full_lines())

            yield from res
        except FileNotFoundError as exn:
            # happens when python can't open file
            togo_node = gbl.make_fake_node(srcfile_name, 0, 0, 0)
            raise err.CompilerError(str(exn), report_line=False, node=togo_node) from exn
        except SyntaxError as exn:
            # comes from inside python when importing file.

            togo_node = gbl.make_fake_node(
                exn.filename, exn.lineno, exn.offset, exn.end_offset
            )
            raise err.CompilerError(exn.msg, node=togo_node) from exn

        except (
            TypeError,
            KeyError,
            ModuleNotFoundError,
            AttributeError,
            IndexError,
        ) as exn:
            raise err.CompilerError(str(exn)) from exn
