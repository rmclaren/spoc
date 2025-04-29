import os
import json
import subprocess
# from make_config_yaml import create_config_file
# import make_config_yaml
import sys 
import importlib.util


from dataclasses import dataclass


from oldmake_config_yaml import create_config_file





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




marine_profile_instruments = [
    "argo",
    "bathy",
    "glider",
    "tesac",
    "tropical",
    "xbtctd"
]
marine_surface_instruments = [
    "altkob",
    "cstgd",
    "drifter",
    "lcman",
    "shipsu",
    "trkob"
]

all_instruments = marine_profile_instruments + marine_surface_instruments


b2i_test_names = {}
for instrument in all_instruments:
    b2i_test_names[instrument] = "b2i_test_" + instrument


b2i_converters = {}
for instrument in marine_profile_instruments:
    b2i_converters[instrument] = "bufr_marine_insitu_profile_" + instrument + ".py"
for instrument in marine_surface_instruments:
    b2i_converters[instrument] = "bufr_marine_insitu_surface_" + instrument + ".py"

# print(json.dumps(b2i_converters, indent=4))


cycle_datetime = '2019010700'
cycle = "00"
# cycle_datetime = "2021063006"
# cycle = "06"


b2i_configs = {}
for instrument in marine_profile_instruments:
    b2i_configs[instrument] = "bufr2ioda_insitu_profile_" + instrument + "_" + cycle_datetime + ".yaml"
for instrument in marine_surface_instruments:
    b2i_configs[instrument] = "bufr2ioda_insitu_surface_" + instrument + "_" + cycle_datetime + ".yaml"


# print(json.dumps(b2i_configs, indent=4))



@dataclass
class ConfigTestData:
    data_format: str
    subsets: str
    data_type: str
    data_description: str


# data_format, subsets, data_type
CONFIG_TEST_DATA = [
    ConfigTestData("subpfl", "SUBPFL", "argo", 
        '6-hrly in-situ ARGO profiles from subpfl: temperature and salinity'),
    ConfigTestData("bathy", "BATHY", "bathy", 
        '6-hrly in-situ profiles from BATHYthermal temperature'),
    ConfigTestData("subpfl", "SUBPFL", "glider", 
        '6-hrly in-situ Glider profiles from subpfl: temperature and salinity'),
    ConfigTestData("tesac", "TESAC", "tesac", 
        '6-hrly in-situ profiles from TESAC: temperature and salinity'),
    ConfigTestData("dbuoy", "DBUOY", "tropical", 
        '6-hrly in-situ tropical mooring profiles from dbuoy: temperature and salinity'),
    ConfigTestData("xbtctd", "XBTCTD", "xbtctd",  
        '6-hrly in-situ profiles from XBT/CTD: temperature and salinity'),
    ConfigTestData("altkob", "ALTKOB", "altkob", 
        '6-hrly in-situ surface obs from altkob: temperature and salinity'),
    ConfigTestData("cstgd", "CSTGD", "cstgd", 
        "6-hrly in-situ sea surface temperature obs from cstgd"),
    # ConfigTestData("dbuoy", "DBUOY", "drifter", 
        # "6-hrly in-situ Lagrangian drifter drogue profiles from dbuy: temperature"),
    ConfigTestData("dbuoyb", "DBUOYB", "drifter", 
        "6-hrly in-situ Lagrangian drifter drogue profiles from dbuoyb: temperature"),
    ConfigTestData("lcman", "LCMAN", "lcman", 
        '6-hrly in-situ surface temperature obs from LCMAN'),
    ConfigTestData("shipsu", "SHIPSU", "shipsu", 
        "6-hrly in-situ temperature obs from shipsu"),
    ConfigTestData("trkob", "TRACKOB", "trkob",  
        '6-hrly in-situ surface obs from TRACKOB: temperature and salinity')
]


def create_test_config_files(config_dir):

    # config = import_bufr2ioda_config(B2I_SCRIPT_DIR, B2I_CONFIG_CLASS_FILE, B2I_CONFIG_CLASS_NAME)
    # assert hasattr(config, 'create_config_file'), "Config class missing create_config_file"

    for test in CONFIG_TEST_DATA:
        i = test.data_type
        config_path = os.path.join(config_dir, b2i_configs[i])
        print(f'create_test_config_files: {config_path}')
        # print(f'creating {test}')
        # print(f'creating {test.data_format}')

        create_config_file(
            data_format=test.data_format,
            subsets=test.subsets,
            data_type=test.data_type,
            data_description=test.data_description,
            cycle_type="gdas",
            cycle_datetime=cycle_datetime,
            dump_dir=TESTDATA_DIR,
            ioda_dir=TESTRESULT_DIR,
            ocean_basin=OCEAN_BASIN_FILE,
            output_path=config_path
        )



def create_tests():
    # config_dir = "/work/noaa/da/edwardg/spoc/test/testconfig"
    config_dir = "/work/noaa/da/edwardg/spoc/test/remote_data/testconfig"
    create_test_config_files(config_dir)

    TESTS = []
    # i = "bathy"
    # TESTS.append((b2i_test_names[i], b2i_converters[i], b2i_configs[i]))
    for i in all_instruments:
        print(f'creating test {b2i_test_names[i]}')
        TESTS.append((b2i_test_names[i], b2i_converters[i], b2i_configs[i]))
    print(f'created {len(TESTS)} tests')
    return TESTS


# TESTS = create_tests()


'''finds and returns an instance of Bufr2iodaConfig'''
def import_bufr2ioda_config(B2I_SCRIPT_DIR, B2I_CONFIG_CLASS_FILE, B2I_CONFIG_CLASS_NAME):
    file_path = os.path.join(B2I_SCRIPT_DIR, B2I_CONFIG_CLASS_FILE)
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"{B2I_CONFIG_CLASS_FILE} not found in {B2I_SCRIPT_DIR}")

    module_name = os.path.splitext(os.path.basename(file_path))[0]

    # Add B2I_SCRIPT_DIR to sys.path to allow importing
    sys.path.append(os.path.abspath(B2I_SCRIPT_DIR))

    try:
        # Load the module dynamically
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec is None:
            raise ImportError(f"Failed to create module spec for {file_path}")

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        # Access the Config class
        if hasattr(module, B2I_CONFIG_CLASS_NAME):
            ConfigClass = getattr(module, B2I_CONFIG_CLASS_NAME)
            if not isinstance(ConfigClass, type):
                    raise ImportError(f"{B2I_CONFIG_CLASS_NAME} in {file_path} is not a class")
            # Now you can use Config inside the function
            config = ConfigClass() 
            # print(f"Imported and instantiated {B2I_CONFIG_CLASS_NAME}: {config}")
            return config
        else:
            raise ImportError(f"Config class not found in {file_path}")

    except Exception as e:
        raise ImportError(f"Failed to import Config from {file_path}: {str(e)}")

    finally:
        # Clean up:
        sys.path.remove(os.path.abspath(B2I_SCRIPT_DIR))


###################################################

if __name__ == "__main__":

    ioda_output_dir = '/work/noaa/da/edwardg/spoc/test'
    bufr_data_dir_orion = '/work/noaa/da/marineda/gfs-marine/data/obs/ci/bufr'

    ocean_basin_file_orion = '/work/noaa/global/glopara/fix/gdas/soca/20240802/common/RECCAP2_region_masks_all_v20221025.nc'


    config_dir = "/work/noaa/da/edwardg/spoc/test/testconfig"
    config_path = os.path.join(config_dir, b2i_configs[i])

    create_config_file(
        data_format="bathy",
        subsets="BATHY",
        data_type="bathy",
        cycle_type="gdas",
        cycle_datetime="2021063006",
        # cycle_datetime=cycle_datetime,
        dump_dir=bufr_data_dir_orion,
        ioda_dir=ioda_output_dir,
        ocean_basin=ocean_basin_file_orion,
        output_path=config_path
    )




    script_dir = "/work/noaa/da/edwardg/spoc/dump/mapping"
    script_file = os.path.join(script_dir, b2i_converters[i])



    cmd = ["python3", script_file, "-c", config_path]
    print(f"executing {cmd}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    print("STDOUT:\n", result.stdout)
    print("STDERR:\n", result.stderr)
    assert result.returncode == 0, f"Script failed: {result.stderr}"


    result_file_name = "gdas.t06z.bathy.tm00.nc"
    result_path = os.path.join(ioda_output_dir, result_file_name)
    TESTOUTPUT_DIR = "/work/noaa/da/edwardg/spoc/test/junk"
    reference_path = os.path.join(TESTOUTPUT_DIR, result_file_name)

    result = subprocess.Popen(f'nccmp -d -m -g -f -S {result_path} {reference_path}', shell=True).wait()
    assert result == 0, f"Comparison failed for {result_path} and {reference_path}."




'''
def create_test_yamls():
    for test_name, script_path, config_name in TESTS:
        config_path = os.path.join(TESTCONFIG_DIR, config_name)
        create_config_file(
            data_format="bathy",
            subsets="BATHY",
            data_type="bathy",
            cycle_type="gdas",
            cycle_datetime="2021063006",
            dump_dir=TESTDATA_DIR,
            ioda_dir=TESTRESULT_DIR,
            ocean_basin=OCEAN_BASIN_FILE,
            output_path=config_path
        )   
        print(f"Created config: {config_path}")
'''
