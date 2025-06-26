#!/usr/bin/env python3
"""Minimize BUFR files by limiting subsets per subset type.

This script reads an input BUFR file via the ``ncepbufr`` interface and
writes a reduced BUFR file containing at most a configurable number of
subsets for each message type found in the input.
"""

import argparse
from collections import defaultdict

import ncepbufr


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

    bufr_in = ncepbufr.open(in_path)
    bufr_out = ncepbufr.open(out_path, "w", table=bufr_in)

    try:
        while bufr_in.advance() == 0:
            msg_type = bufr_in.msg_type
            remaining = max_subsets - subset_counts[msg_type]

            if remaining <= 0:
                while bufr_in.load_subset() == 0:
                    pass
                continue

            if bufr_in.receipt_time and bufr_in.receipt_time > 0:
                bufr_out.open_message(
                    msg_type,
                    bufr_in.msg_date,
                    bufr_in.receipt_time,
                )
            else:
                bufr_out.open_message(msg_type, bufr_in.msg_date)

            copied = 0
            while bufr_in.load_subset() == 0:
                if copied < remaining:
                    bufr_out.copy_subset(bufr_in)
                    copied += 1
            bufr_out.close_message()
            subset_counts[msg_type] += copied
    finally:
        bufr_in.close()
        bufr_out.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reduce the size of a BUFR file by limiting subsets")
    parser.add_argument("input", help="Path to the input BUFR file")
    parser.add_argument("output", help="Path to the minimized BUFR file")
    parser.add_argument("--max-subsets", type=int, default=1000, help="Maximum number of subsets per subset type (default: 1000)")

    args = parser.parse_args()

    minimize_bufr(args.input, args.output, args.max_subsets)
