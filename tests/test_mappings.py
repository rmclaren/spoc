import os
import sys
import importlib
import shutil
import subprocess
import pytest

# Paths relative to this file
TEST_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(TEST_DIR, 'data')

# Add the mapping directory to the python path
sys.path.insert(0, os.path.join(TEST_DIR, '../dump/mapping'))

# Each entry defines a mapping module and required files
# Add additional mappings as needed
TEST_CASES = [
    {
        'mapping': 'bufr_satwnd_amv_abi',
        'input_file': 'testdata/2025040100-gdas.t00z.satwnd.tm00.bufr_d',
        'output_file': 'testoutput/bufr_satwnd_amv_abi_goes-16.nc'
    }
]

@pytest.mark.parametrize('cfg', TEST_CASES)
def test_create_obs_file(tmp_path, cfg):
    pytest.importorskip('bufr')

    module = importlib.import_module(cfg['mapping'])

    data_path = os.path.join(DATA_DIR, cfg['input_file'])
    output_path = os.path.join(DATA_DIR, cfg['output_file'])

    print ("@@@@ ", data_path)

    if not (os.path.exists(data_path) and os.path.exists(output_path)):
        pytest.skip('Required test files are missing')

    out_file = tmp_path / 'out.nc'
    module.create_obs_file(data_path, output_path)

    nccmp_bin = shutil.which('nccmp')
    if not nccmp_bin:
        pytest.skip('nccmp not available')

    result = subprocess.run([nccmp_bin, '-d', str(expected_nc), str(out_file)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert result.returncode == 0, result.stderr.decode()


@pytest.mark.parametrize('cfg', TEST_CASES)
def test_create_obs_group(cfg):
    pytest.importorskip('pyioda')

    module = importlib.import_module(cfg['module'])

    bufr_path = os.path.join(DATA_DIR, cfg['bufr_file'])
    map_path = os.path.join(DATA_DIR, cfg['mapping_file'])

    if not (os.path.exists(bufr_path) and os.path.exists(map_path)):
        pytest.skip('Required test files are missing')

    env = {'comm_name': 'world'}
    obs = module.create_obs_group(bufr_path, map_path, cfg['cycle_time'], env)

    assert obs is not None
