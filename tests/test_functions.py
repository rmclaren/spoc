import os
import sys
import importlib
import shutil
import subprocess
import pytest

from .test_cases import TEST_CASES

# Paths relative to this file
TEST_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(TEST_DIR, 'data')

# Add the mapping directory to the python path
sys.path.insert(0, os.path.join(TEST_DIR, '../dump/mapping'))

TEST_IDS = [cfg['map'] for cfg in TEST_CASES]

@pytest.mark.parametrize('cfg', TEST_CASES, ids=TEST_IDS)
def test_create_obs_file(cfg):
    pytest.importorskip('bufr')

    module = importlib.import_module(cfg['map'])
    args = cfg['args']
    cmp_path = os.path.join(DATA_DIR, cfg['cmp'])
    result_path = os.path.join(DATA_DIR, cfg['result'])

    module.create_obs_file(**args)

    nccmp_bin = shutil.which('nccmp')
    if not nccmp_bin:
        pytest.skip('nccmp not available')

    result = subprocess.run([nccmp_bin, '-d', cmp_path, result_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    assert result.returncode == 0, result.stderr.decode()


@pytest.mark.parametrize('cfg', TEST_CASES, ids=TEST_IDS)
def test_create_obs_group(cfg):
    pytest.importorskip('pyioda')

    module = importlib.import_module(cfg['map'])

    args = cfg['args']
    args['env'] = {'comm_name': 'world'}

    obs = module.create_obs_group(**args)

    assert obs is not None
