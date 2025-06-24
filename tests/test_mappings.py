import importlib
import os
import shutil
import subprocess
import pytest

# Paths relative to this file
TEST_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(TEST_DIR, 'data')

# Each entry defines a mapping module and required files
# Add additional mappings as needed
TEST_CASES = [
    {
        'module': 'bufr_satwnd_amv_abi',
        'mapping_file': 'bufr_satwnd_amv_abi.yaml',
        'bufr_file': 'adpupa.bufr',
        'expected_nc': 'adpupa.nc',
        'cycle_time': '2021080100',
    },
]

@pytest.mark.parametrize('cfg', TEST_CASES)
def test_create_obs_file(tmp_path, cfg):
    pytest.importorskip('bufr')

    module = importlib.import_module(cfg['module'])

    bufr_path = os.path.join(DATA_DIR, cfg['bufr_file'])
    map_path = os.path.join(DATA_DIR, cfg['mapping_file'])
    expected_nc = os.path.join(DATA_DIR, cfg['expected_nc'])

    if not (os.path.exists(bufr_path) and os.path.exists(map_path) and os.path.exists(expected_nc)):
        pytest.skip('Required test files are missing')

    out_file = tmp_path / 'out.nc'
    module.create_obs_file(bufr_path, map_path, str(out_file), cfg['cycle_time'])

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
