#! /bin/env python3
import argparse
import pathlib
import re

import semver


# yet another grab version from project and update tool. Takes from
# the known truth and puts it everywhere else by string replace.  If
# that changes something you don't want, well, you shouldn't have made
# it look like the previous version number.


def dig_out_semver(txt):
    semver_found = re.match(
        '^(\\d*\\.\\d*\\.\\d*[$"]?.*)', txt, re.DOTALL | re.IGNORECASE
    )
    if semver_found:
        return semver_found.group(1)
    return None


# look for things which look like version numbers, break them
# apart and return <prev_text> <version number> <date-code> <post_text>


def find_before_version_after(path) -> tuple[str, str, str]:
    init_lines = path.read_text()

    semverish = "([0-9]+\\.[0-9]+\\.[-+0-9a-z\\.]+)"

    # special case if first line looks like version

    version_found = re.match(
        f"^(){semverish}(.*)",
        init_lines,
        re.DOTALL | re.IGNORECASE,
    )

    # matches my doc, the toml and the stuff in init.

    if not version_found:
        version_found = re.match(
            f"(.*?Version[^0-9]*){semverish}(.*)",
            init_lines,
            re.DOTALL | re.IGNORECASE,
        )

    if not version_found:
        raise SystemExit(f"No existing version found in {path}.")

    seen_semver = dig_out_semver(version_found.group(2))

    if not seen_semver:
        raise SystemExit(f"Can't parse version in '{path}' '{version_found.group(2)}'.")

    return version_found.group(1), seen_semver, version_found.group(3)


def main_worker():
    parser = argparse.ArgumentParser(
        prog="version",
        description="yet another way for single point pyproject.toml etc version mods.",
    )

    parser.add_argument(
        "--truth",
        required=False,
        help="source file for truth",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="talk a lot",
    )

    parser.add_argument(
        "--force",
        required=False,
        help="force truth version",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="emit version directly to stdout.",
    )

    parser.add_argument(
        "--victims", nargs="*", help="file names to modify", metavar="FILENAME", type=str
    )

    args = parser.parse_args()

    new_truth = ""
    if args.truth:
        path = pathlib.Path(args.truth)
        _, new_truth, _ = find_before_version_after(path)
        if args.verbose:
            print(f"Found {new_truth} in {path}")

    if args.force:
        new_truth = args.force
        if args.verbose:
            print(f"Found {new_truth} from --force.")

    before_text = ""
    after_text = ""

    if args.stdout:
        print(new_truth)

    semver.Version.parse(new_truth)

    for src_name in args.victims:
        target_path = pathlib.Path(src_name)
        before_text, was, after_text = find_before_version_after(target_path)

        if was == new_truth:
            print(f"{src_name} version {new_truth} doesn't need to change")
        else:
            target_path.write_text(before_text + new_truth + after_text, encoding="utf-8")

        if args.verbose:
            print(f"Changed version {was} to {new_truth} in {target_path}")


def main():
    try:
        main_worker()
    except (ValueError, SystemExit, FileNotFoundError) as err:
        print(f"** FAIL: {err}")
        raise SystemExit(1) from err


main()
