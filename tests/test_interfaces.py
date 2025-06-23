import importlib
import os
import subprocess
import shutil
import pytest

# Define mapping specifications: module path, input BUFR, mapping yaml, baseline NetCDF
MAPPING_SPECS = [
    {
        'module': 'dump.mapping.bufr_adpupa_prepbufr',
        'input': os.path.join('tests', 'data', 'adpupa.bufr'),
        'mapping': os.path.join('dump', 'mapping', 'bufr_adpupa_prepbufr_mapping.yaml'),
        'baseline': os.path.join('tests', 'baseline', 'adpupa.nc'),
        'cycle': '2021010100',
    },
]

required_packages = ['numpy', 'bufr', 'pyioda']


def require_dependencies():
    """Skip tests if required packages or tools are missing."""
    for pkg in required_packages:
        pytest.importorskip(pkg)
    if shutil.which('nccmp') is None:
        pytest.skip('nccmp utility not available')


@pytest.mark.parametrize('spec', MAPPING_SPECS, ids=[spec['module'] for spec in MAPPING_SPECS])
def test_create_obs_file(spec, tmp_path):
    require_dependencies()
    if not os.path.exists(spec['input']) or not os.path.exists(spec['baseline']):
        pytest.skip('Sample data not available')

    mod = importlib.import_module(spec['module'])
    output = tmp_path / 'out.nc'

    mod.create_obs_file(spec['input'], spec['mapping'], str(output), spec['cycle'])
    result = subprocess.run(['nccmp', '-d', str(output), spec['baseline']])
    assert result.returncode == 0


@pytest.mark.parametrize('spec', MAPPING_SPECS, ids=[spec['module'] for spec in MAPPING_SPECS])
def test_create_obs_group(spec):
    require_dependencies()
    if not os.path.exists(spec['input']):
        pytest.skip('Sample data not available')

    mod = importlib.import_module(spec['module'])
    env = {'comm_name': 'world'}
    group = mod.create_obs_group(spec['input'], spec['mapping'], spec['cycle'], env)
    assert group is not None
