#! /usr/bin/env python

# i have a theory that intra file links&anchors must
# have the links in lower case.

# and org exports an extra toc that I can't clean up.

import argparse
import pathlib
import re


def main():
    parser = argparse.ArgumentParser(prog="repairmd", description="experimental fixup.")
    parser.add_argument("--src", action="store", required=True, help="src")
    parser.add_argument("--dst", action="store", required=True, help="dst")

    args = parser.parse_args()
    incoming = pathlib.Path(args.src).read_text()

    def remove_bogus_toc(src):
        ignoring_first_part = True
        for line in src:
            if ignoring_first_part:
                nowhite = line.lstrip()
                if nowhite.startswith("- ["):
                    continue
                # got past the toc, so thing now.
                ignoring_first_part = False
            yield line

    def make_links_digestable(src):
        def fixup(m):
            low = m.group(0).lower()
            low = low.replace(" ", "-")
            return low

        for line in src:
            yield re.sub("\\(#[^)]*", fixup, line)

    def remove_bogus_anchors(src):
        for line in src:
            if line.startswith("<a id"):
                continue
            yield line

    # it looks like an svg file with the
    # svg in a wacky place gets the wrong
    # markup. eg
    # (<https://codc...aph/badge.svg?token=FKR....U1>)
    # should become
    # (![img] (https://codc...aph/badge.svg?token=FKR....U1>))
    def fixup_svg_links(src):
        def svg_worker(inside):
            return f"(![img]({inside.group(1)}))\n"

        for line in src:
            yield re.sub("\\(<(https:.*svg[^>]*)>\\)\s*", svg_worker, line)

    out = remove_bogus_anchors(
        fixup_svg_links(
            make_links_digestable(
                remove_bogus_toc(incoming.split("\n")),
            )
        )
    )

    pathlib.Path(args.dst).write_text("\n".join(out))


main()
