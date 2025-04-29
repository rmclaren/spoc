import pytest
import os
import subprocess
import tarfile
import urllib.request
import shutil
import yaml
from run_compare import run_compare
from config import *

import re


'''
B2I_SCRIPT_DIR = "/work/noaa/da/edwardg/spoc/dump/mapping/"
B2I_CONFIG_CLASS_FILE = "bufr_marine_insitu_config.py"
B2I_CONFIG_CLASS_NAME = "Bufr2iodaConfig"
OCEAN_BASIN_FILE = "/work/noaa/global/glopara/fix/gdas/soca/20240802/common/RECCAP2_region_masks_all_v20221025.nc"

SPOC_URL = "https://ftp.emc.ncep.noaa.gov/static_files/public/spoc"
TARBALL_FILE = "spoc-0.0.0.tgz"
TARBALL_URL = SPOC_URL + "/" + TARBALL_FILE
TARBALL_DIR = "/work/noaa/da/edwardg/spoc/test"
REMOTE_DATA_DIR = os.path.join(TARBALL_DIR, "remote_data")
TESTDATA_DIR = os.path.join(REMOTE_DATA_DIR, "testdata")
TESTOUTPUT_DIR = os.path.join(REMOTE_DATA_DIR, "testoutput")
TESTCONFIG_DIR = os.path.join(REMOTE_DATA_DIR, "testconfig")
TESTRESULT_DIR = os.path.join(TARBALL_DIR, "testresult")
'''

TESTS = create_tests()




@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Download tarball, extract, set up testconfig and testresult directories."""
    # Create tarball directory
    os.makedirs(TARBALL_DIR, exist_ok=True)

    # Download tarball
    tarball_path = os.path.join(TARBALL_DIR, TARBALL_FILE)
    print(f"Downloading tarball from {TARBALL_URL}")
    urllib.request.urlretrieve(TARBALL_URL, tarball_path)

    # Extract tarball
    with tarfile.open(tarball_path, "r:gz") as tar:
        tar.extractall(TARBALL_DIR)
    print(f"Extracted tarball to {REMOTE_DATA_DIR}")

    # Create testresult directory
    if os.path.exists(TESTRESULT_DIR):
        print(f"Removing old test results directory:\n {TESTRESULT_DIR}")
        shutil.rmtree(TESTRESULT_DIR)
    print(f"Creating new test results directory:\n {TESTRESULT_DIR}")
    os.makedirs(TESTRESULT_DIR)

    # Check if testconfig exists, create if missing
    if not os.path.exists(TESTCONFIG_DIR):
        os.makedirs(TESTCONFIG_DIR)
        print(f"Created testconfig directory: {TESTCONFIG_DIR}")

        # create_test_yamls()

    # Cleanup tarball
    os.remove(tarball_path)

    yield  # Run tests

    # Cleanup (optional)
    # shutil.rmtree(REMOTE_DATA_DIR)
    # shutil.rmtree(TESTRESULT_DIR)



def extract_descriptor(filename):
    name = os.path.basename(filename)
    pattern = r'^bufr_marine_insitu_(.+)\.py$'
    match = re.match(pattern, name)                               
    if match:
        return match.group(1)  # Return the extracted part (e.g., profile_argo)
    return None





@pytest.mark.parametrize("test_name,script_name,config_name", TESTS)
def test_converter(test_name, script_name, config_name):
    """Run converter script and compare output with expected."""
    descriptor = extract_descriptor(script_name)

    # Ensure script and config exist
    script_path = os.path.join(B2I_SCRIPT_DIR, script_name)
    assert os.path.isfile(script_path), f"Script not found: {script_path}"
    config_path = os.path.join(TESTCONFIG_DIR, config_name)
    assert os.path.isfile(config_path), f"Config not found: {config_path}"

    config = import_bufr2ioda_config(B2I_SCRIPT_DIR, B2I_CONFIG_CLASS_FILE, B2I_CONFIG_CLASS_NAME)
    config.read_config_file(config_path)
    ioda_filename = config.ioda_filename(descriptor)
    print(f"config ioda_filename = {ioda_filename}")

    # Run converter
    cmd = ["python3", script_path, "-c", config_path]
    print(f"Running test {test_name}: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0, f"Test {test_name} failed: {result.stderr}"

    result_file = os.path.join(TESTRESULT_DIR, ioda_filename)
    expected_file = os.path.join(TESTOUTPUT_DIR, ioda_filename)

    # Compare output
    assert os.path.isfile(result_file), f"Result file not found: {result_file}"
    assert os.path.isfile(expected_file), f"Expected file not found: {expected_file}"
    assert run_compare(result_file, expected_file), (
        f"Test {test_name} failed: {result_file} does not match {expected_file}"
    )
    print(f"Test {test_name} passed")
