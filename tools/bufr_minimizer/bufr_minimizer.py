#!/usr/bin/env python3
"""Minimize BUFR files by limiting subsets per subset type.

This script reads an input BUFR file and writes a reduced BUFR file
containing at most a configurable number of subsets for each subset
message type. The script relies on the python interface of the
``nceplibs-bufr`` library which provides ``BUFRFile`` and ``BUFRMessage``
classes for manipulating BUFR data.
"""

import argparse
from collections import defaultdict

import nceplibs.bufr as bufr


def minimize_bufr(in_path: str, out_path: str, max_subsets: int = 1000) -> None:
    """Create a reduced BUFR file keeping only a limited number of subsets.

    Parameters
    ----------
    in_path : str
        Path to the input BUFR file.
    out_path : str
        Path where the minimized BUFR file will be written.
    max_subsets : int, optional
        Maximum number of subsets to retain for each subset type. ``1000`` by
        default.
    """

    subset_counts = defaultdict(int)

    with bufr.BUFRFile(in_path, "r") as infile, bufr.BUFRFile(out_path, "w") as outfile:
        for msg in infile:
            subset_name = msg.subset
            count = subset_counts[subset_name]

            if count >= max_subsets:
                continue

            allowed = max_subsets - count

            if msg.n_subsets > allowed:
                msg = msg.slice(stop=allowed)

            outfile.write(msg)
            subset_counts[subset_name] += msg.n_subsets


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reduce the size of a BUFR file by limiting subsets")
    parser.add_argument("input", help="Path to the input BUFR file")
    parser.add_argument("output", help="Path to the minimized BUFR file")
    parser.add_argument("--max-subsets", type=int, default=1000, help="Maximum number of subsets per subset type (default: 1000)")

    args = parser.parse_args()

    minimize_bufr(args.input, args.output, args.max_subsets)
