#! /bin/env python3
import argparse
import pathlib
import re
import sys
import typing

# yet another grab version from project and update tool.
# takes from the known truth and puts it everywhere else.


def dig_out_semver(txt) -> typing.Optional[str]:
    semver_found = re.match(
        '^(\\d*\\.\\d*\\.\\d*[$"]?.*)', txt, re.DOTALL | re.IGNORECASE
    )
    if semver_found:
        return semver_found.group(1)
    return None


# look for things which look like version numbers, break them
# apart and return <prev_text> <version number> <date-code> <post_text>
def find_before_version_after(path):
    init_lines = path.read_text()

    semverish = "([0-9]+\\.[0-9]+\\.[-+0-9a-z\\.]+)"

    # special case if first line looks like version
    version_found = re.match(f"^(){semverish}(.*)", init_lines, re.DOTALL | re.IGNORECASE)

    # matches my doc, the toml and the stuff in init.

    if not version_found:
        version_found = re.match(
            f"(.*?Version[^0-9]*){semverish}(.*)",
            init_lines,
            re.DOTALL | re.IGNORECASE,
        )

    if not version_found:
        print(f"No existing version found in {path}.")
        sys.exit(1)

    semver = dig_out_semver(version_found.group(2))

    if not semver:
        print(f"Can't parse version in '{path}' '{version_found.group(2)}'.")
        sys.exit(1)

    return version_found.group(1), semver, version_found.group(3)


def main():
    parser = argparse.ArgumentParser(
        prog="version",
        description="yet another way for single point pyproject.toml etc version mods.",
    )
    parser.add_argument("files", type=str, nargs="+", help="files to check")
    parser.add_argument(
        "--list",
        action="store_true",
        required=False,
        help="show current versions in source",
    )

    parser.add_argument(
        "--truth",
        action="store",
        required=False,
        help="source file for truth",
    )

    parser.add_argument(
        "--force",
        action="store",
        required=False,
        help="force patch version",
    )
    args = parser.parse_args()

    new_truth = None
    if args.truth:
        path = pathlib.Path(args.truth)
        _, new_truth, _ = find_before_version_after(path)

    if args.force:
        new_truth = args.force

    if new_truth:
        for filename in args.files:
            path = pathlib.Path(filename)
            before_text, semver, after_text = find_before_version_after(path)
            path.write_text(before_text + new_truth + after_text, encoding="utf-8")

    if args.list:
        maxlen = max(len(filename) for filename in args.files)
        for filename in args.files:
            path = pathlib.Path(filename)
            before_text, semver, after_text = find_before_version_after(path)
            print(f"{filename.rjust(maxlen)} {semver.rjust(6)}")

    sys.exit(0)


main()
