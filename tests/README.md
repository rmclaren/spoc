The `tests` directory contains regression tests for SPOC mapping modules
using the `pytest` framework.

Sample BUFR inputs and reference NetCDF outputs are not provided in the
repository. They must be placed under `tests/data` and `tests/baseline`
respectively before the tests can be executed. The tests will be skipped
if the required files are not found or if the necessary dependencies
(e.g. `numpy`, `bufr`, `pyioda`, and the `nccmp` utility) are missing.

Run all tests with:

```
pytest -v
```
