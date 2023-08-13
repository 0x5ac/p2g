import ast
import pathlib

from p2g import gbl


def code_context_node(node: ast.AST):

    file_name = gbl.ast_file_name(node)
    file_path = pathlib.Path(file_name).absolute()
    reportable_line = node.lineno

    # if testing try and shrink filename and make
    # line numbers relative to start of function.

    if gbl.config.first_line >= 0:
        reportable_line -= gbl.config.first_line
    if gbl.config.short_filenames:
        file_name = str(file_path.name)
    else:
        file_name = str(file_path)

    col_offset = node.col_offset
    assert isinstance(node.end_col_offset, int)
    assert isinstance(node.col_offset, int)
    assert node.end_col_offset is not None

    col_width = node.end_col_offset - col_offset
    pfx = ":".join(
        [
            file_name,
            str(reportable_line),
            str(node.col_offset),
            str(node.end_col_offset),
            " ",
        ]
    )
    return pfx, " " * (len(pfx) + col_offset) + "^" * col_width


def source_from_node(node: ast.AST):
    source_lines = gbl.get_lines(gbl.ast_file_name(node))
    return source_lines[node.lineno - 1]


class CompilerError(Exception):

    node: ast.AST
    message: str
    report_line: bool

    def __init__(self, message, report_line=True, node=gbl.astnone):
        super().__init__()

        if gbl.config.bp_on_error:
            breakpoint()  # no cover

        self.report_line = report_line
        self.message = message
        self.node = gbl.iface.last_node if node is gbl.astnone else node

    def get_report_lines(self):

        node = self.node
        message = self.message

        line_prefix, source_context = code_context_node(node)

        if not self.report_line:
            return [source_context, message]

        source_line = source_from_node(node)
        # if error messaeg text will fit into context
        # line without trashing anything then put it there.
        message_len = len(message)
        gap_to_start = len(source_context) - len(source_context.lstrip())

        space_between = gap_to_start - message_len
        if space_between > 1:
            source_context = message + " " * space_between + source_context[gap_to_start:]
            return [line_prefix + source_line, source_context]

        return [line_prefix + source_line, source_context, message]


def compiler(message: str = "", node=gbl.astnone, exn=None):

    raise CompilerError(message, node=node) from exn
