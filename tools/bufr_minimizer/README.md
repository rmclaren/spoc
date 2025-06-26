# BUFR Minimizer

This utility reduces the size of an existing BUFR file by limiting the number
of subsets kept for each subset type.  It can be useful when generating small
sample BUFR files for unit tests or debugging.

## Usage

```bash
python bufr_minimizer.py INPUT_FILE OUTPUT_FILE [--max-subsets N]
```

- `INPUT_FILE` – path to the original BUFR file.
- `OUTPUT_FILE` – location where the minimized BUFR file will be written.
- `--max-subsets` – optional maximum number of subsets to keep for each subset
  type.  Defaults to `1000` if not provided.

The script requires the python interface of the `nceplibs-bufr` library.
