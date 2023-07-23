#! /bin/env python3
import argparse
import pathlib
import re
import subprocess
import sys


# yet another grab version from project and update tool.


# returns what the patch  number would be once we've run
# this and checked in.
def calc_next_git_patch():
    patches = subprocess.run(
        ["git", "rev-list", "--all", "--count"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout

    #    now = datetime.date.today()
    #    res =    f"-{now.strftime('%y%m%d')}.{patches.strip()}"
    res = f"{patches.strip()}"

    return str(int(res) - 1)


# look for things which look like version numbers, break them
# apart and return <prev_text> <version number> <date-code> <post_text>
def find_version_strings(path):
    init_lines = path.read_text()

    # matches my doc, the toml and the stuff in init.

    version_prefix_found = re.match(
        "(.*?Version[^0-9]*)(.*)",
        init_lines,
        re.DOTALL | re.IGNORECASE,
    )

    if not version_prefix_found:
        print(f"No existing version found in {path}.")
        sys.exit(1)
    prefix = version_prefix_found.group(1)
    old_semver_and_rest = version_prefix_found.group(2)
    semver_found = re.match(
        "(\\d+\\.\\d+\\.)([-+.A-Za-z0-9]+)(.*)", old_semver_and_rest, re.DOTALL
    )
    if not semver_found:
        return prefix, "", "", old_semver_and_rest
    major_minor = semver_found.group(1)
    patch = semver_found.group(2)
    rest = semver_found.group(3)
    return prefix, major_minor, patch, rest


def main():
    parser = argparse.ArgumentParser(
        prog="version",
        description="yet another way for single point pyproject.toml etc version mods.",
    )

    parser.add_argument("files", type=str, nargs="+", help="files to check")

    parser.add_argument(
        "--inplace",
        action="store_true",
        required=False,
        help="modify source",
    )
    parser.add_argument(
        "--report",
        action="store_true",
        required=False,
        help="show versions in source",
    )

    parser.add_argument(
        "--show",
        action="store_true",
        required=False,
        help="show current version",
    )

    parser.add_argument(
        "--force",
        action="store",
        required=False,
        help="force patch version",
    )
    parser.add_argument(
        "--git",
        action="store_true",
        required=False,
        help="patch number from git count.",
    )
    args = parser.parse_args()

    next_semver = None

    maxlen = 0
    for filename in args.files:
        path = pathlib.Path(filename)
        before_text, cur_version, cur_patch, after_text = find_version_strings(path)

        maxlen = max(len(filename), maxlen)
        if next_semver is None:
            if args.force:
                cur_patch = args.force
            if args.git:
                cur_patch = calc_next_git_patch()

            next_semver = cur_version + cur_patch

        if args.inplace:
            path.write_text(before_text + next_semver + after_text, encoding="utf-8")

    if args.report:
        for filename in args.files:
            path = pathlib.Path(filename)
            before_text, cur_version, cur_patch, after_text = find_version_strings(path)
            print(
                f"{filename.rjust(maxlen)} {cur_version.rjust(6)} {cur_patch.ljust(5)}  "
            )
        print()
        print(f"Requested semver {next_semver}")

    if args.show:
        print(next_semver)

    sys.exit(0)


main()
