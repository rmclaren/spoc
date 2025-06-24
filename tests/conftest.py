import os
import tarfile
import urllib.request
import io
import shutil
import pytest

DATA_URL = "https://ftp.emc.ncep.noaa.gov/static_files/public/spoc/spoc-0.0.0.tgz"

@pytest.fixture(scope="session", autouse=True)
def download_test_data():
    """Download and extract required test data."""
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    if os.path.isdir(data_dir) and os.listdir(data_dir):
        # Data already present
        return data_dir

    os.makedirs(data_dir, exist_ok=True)
    try:
        with urllib.request.urlopen(DATA_URL) as response:
            archive_data = response.read()
        with tarfile.open(fileobj=io.BytesIO(archive_data), mode="r:gz") as tar:
            tar.extractall(path=data_dir)
    except Exception as exc:
        shutil.rmtree(data_dir, ignore_errors=True)
        pytest.skip(f"Could not download test data: {exc}")
    return data_dir
