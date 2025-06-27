# Each entry defines a mapping module and required files
# Add additional mappings as needed
TEST_CASES = [
    {
        'map': 'bufr_satwnd_amv_abi',
        'args' : {
            'input': 'testdata/2025040100-gdas.t00z.satwnd.tm00.bufr_d',
            'output': 'testrun/bufr_satwnd_amv_abi_{splits/satId}.nc'
        },
        'cmp': 'testoutput/bufr_satwnd_amv_abi_goes-16.nc',
        'result': 'testrun/bufr_satwnd_amv_abi_goes-16.nc'
    },
    {
        'map': 'bufr_satwnd_amv_ahi',
        'args': {
            'input': 'testdata/2025040100-gdas.t00z.satwnd.tm00.bufr_d',
            'output': 'testrun/bufr_satwnd_amv_ahi_{splits/satId}.nc'
        },
        'cmp': 'testoutput/bufr_satwnd_amv_ahi_h9.nc',
        'result': 'testrun/bufr_satwnd_amv_ahi_h9.nc'
    },
    {
        'map': 'bufr_satwnd_amv_avhrr',
        'args': {
            'input': 'testdata/2025040100-gdas.t00z.satwnd.tm00.bufr_d',
            'output': 'testrun/bufr_satwnd_amv_avhrr_{splits/satId}.nc'
        },
        'cmp': 'testoutput/bufr_satwnd_amv_avhrr_n19.nc',
        'result': 'testrun/bufr_satwnd_amv_avhrr_n19.nc'
    },
    {
        'map': 'bufr_satwnd_amv_leogeo',
        'args': {
            'input': 'testdata/2025040100-gdas.t00z.satwnd.tm00.bufr_d',
            'output': 'testrun/bufr_satwnd_amv_leogeo_{splits/satId}.nc'
        },
        'cmp': 'testoutput/bufr_satwnd_amv_leogeo_multi.nc',
        'result': 'testrun/bufr_satwnd_amv_leogeo_multi.nc'
    },
    {
        'map': 'bufr_satwnd_amv_modis',
        'args': {
            'input': 'testdata/2025040100-gdas.t00z.satwnd.tm00.bufr_d',
            'output': 'testrun/bufr_satwnd_amv_modis_{splits/satId}.nc'
        },
        'cmp': 'testoutput/bufr_satwnd_amv_modis_terra.nc',
        'result': 'testrun/bufr_satwnd_amv_modis_terra.nc'
    },
    {
        'map': 'bufr_satwnd_amv_seviri',
        'args': {
            'input': 'testdata/2025040100-gdas.t00z.satwnd.tm00.bufr_d',
            'output': 'testrun/bufr_satwnd_amv_seviri_{splits/satId}.nc'
        },
        'cmp': 'testoutput/bufr_satwnd_amv_seviri_m10.nc',
        'result': 'testrun/bufr_satwnd_amv_seviri_m10.nc'
    },

]