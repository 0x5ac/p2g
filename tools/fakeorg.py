#! /usr/bin/env python

# pretend to be emacs's org eval, but faster.

import io
import pathlib
import re
import subprocess
import sys
import threading


def execute(execstr, src):
    as_words = execstr.split()
    execr = [word for word in as_words if word]

    if execr[0] == "poetry" and execr[1] == "run" and execr[2] == "p2g":
        execr = ["python", "-m", "p2g"] + execr[3:]

    res = subprocess.run(
        execr,
        check=True,
        capture_output=True,
        input="".join(src).encode(),
    )

    return io.StringIO(res.stdout.decode()).readlines()


def chew_func():
    eval_src: list[str] = []
    eval_results: list[str] = []
    line = None
    while True:
        line = yield [line]
        if eval_results and line.startswith("#+begin_example"):
            line = yield [line]
            while not line.startswith("#+end_example"):
                line = yield []
            line = yield eval_results + [line]
            eval_results = []
            continue

        found = re.match(
            "#\\+begin_src\\s+python\\s+-i\\s+:results"
            "\\s+output\\s+:exports both\\s+:python (.*)",
            line,
        )
        if found:
            while not line.startswith("#+end_src"):
                line = yield [line]
                eval_src.append(line)

            eval_results = execute(found.group(1), eval_src)
            continue


def write_list(file, srclist):
    with pathlib.Path(file).open("w", encoding="utf-8") as outf:
        outf.writelines(srclist)


def process_one_file(src_file):
    with src_file.open(encoding="utf-8") as infile:
        src_lines = infile.readlines()

        finished = []

        chewer = chew_func()

        next(chewer)
        for line in src_lines:
            finished += chewer.send(line)

        chewer.close()
        finished_len = len(finished)
        original_len = len(src_lines)

        print(
            f"{finished_len / original_len * 100.0 : 5.2f} "
            f"{original_len:4} -> {finished_len:4}  {src_file} "
        )
        if finished_len < 0.8 * original_len:
            emergency_file = src_file.with_suffix(".emergency")
            print(
                f"File seems to have shrunk a lot. saving {src_file} to {emergency_file}"
            )
            write_list(emergency_file, src_lines)

        if finished != src_lines:
            backup_file = src_file.with_suffix(".backup")
            print(f"{src_file} backed up into -> {backup_file}")
            write_list(backup_file, src_lines)
            write_list(src_file, finished)


def main():
    all_targets = pathlib.Path(sys.argv[1]).glob("*.org")

    threads = [
        threading.Thread(
            target=process_one_file,
            args=(file,),
        )
        for file in all_targets
    ]

    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()


main()
