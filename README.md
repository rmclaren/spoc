# SPOC
Specific Preprocessing of Observations Configuration

This repository holds template configuration files, supporting scripts,
and other infrastructure needed to convert observations to the JEDI IODA
format offline as well as read them directly in JEDI applications.

## Testing

PyTest based regression tests reside in the `tests/` directory. Sample
BUFR inputs and reference NetCDF outputs are required to execute the
tests. Place the files in `tests/data` and `tests/baseline` and run:

```
pytest -v
```
