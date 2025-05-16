#!/usr/bin/env python3
import os
import numpy as np
import time
import calendar
from datetime import datetime

import bufr
from bufr.obs_builder import ObsBuilder, add_main_functions, map_path
from prepbufr_obs_builder import PrepbufrObsBuilder

MAPPING_PATH = map_path('prepbufr_adpupa.yaml')


class AdpupaPrepbufrObsBuilder(PrepbufrObsBuilder):
    """
    A builder class to generate ADPUPA observations from ADPUPA prepBUFR input.
    """

    def __init__(self):
        super().__init__(MAPPING_PATH, log_name=os.path.basename(__file__))

    def make_obs(self, comm, input_path):

        # Get container from mapping file first
        self.log.info(f'Get container from bufr')
        container = super().make_obs(comm, input_path)

        self.log.debug(f'container list (original): {container.list()}')

        self.log.debug(f'Perform DateTime calculation')
        hrdr = container.get('obsTimeMinusCycleTime')
        cycle_time = "2021080100"
        cycleTimeSinceEpoch = np.int64(calendar.timegm(time.strptime(str(int(cycle_time)), '%Y%m%d%H')))
        dateTime = self._compute_datetime(cycleTimeSinceEpoch, hrdr)

        self.log.debug(f'Perform stationPressure calculation')
        cat = container.get('prepbufrDataLevelCategory')
        pob = container.get('pressure')
        ps = np.full(pob.shape[0], pob.fill_value)
        ps = np.where(cat == 0, pob, ps)

        self.log.debug(f'Perform stationPressureQM calculation')
        pqm = container.get('pressureQualityMarker')
        psqm = np.full(pqm.shape[0], pqm.fill_value)
        psqm = np.where(cat == 0, pqm, psqm)

        self.log.debug(f'Perform stationPressureError calculation')
        poe = container.get('pressureError')
        psoe = np.full(poe.shape[0], poe.fill_value)
        psoe = np.where(cat == 0, poe, psoe)

        self.log.debug(f'Perform airTemperature and virtualTemperature calculations')
        tpc = container.get('temperatureEventProgramCode')
        tob = container.get('airTemperature')
        tsen = np.full(tob.shape[0], tob.fill_value)
        tsen = np.where(((tpc >= 1) & (tpc < 8)), tob, tsen)
        tvo = np.full(tob.shape[0], tob.fill_value)
        tvo = np.where((tpc == 8), tob, tvo)

        self.log.debug(f'Perform airTemperatureQM and virtualTemperatureQM calculations')
        tobqm = container.get('temperatureQualityMarker')
        tsenqm = np.full(tobqm.shape[0], tobqm.fill_value)
        tsenqm = np.where(((tpc >= 1) & (tpc < 8)), tobqm, tsenqm)
        tvoqm = np.full(tobqm.shape[0], tobqm.fill_value)
        tvoqm = np.where((tpc == 8), tobqm, tvoqm)

        self.log.debug(f'Perform airTemperatureError and virtualTemperatureError calculations')
        toboe = container.get('temperatureError')
        tsenoe = np.full(toboe.shape[0], toboe.fill_value)
        tsenoe = np.where(((tpc >= 1) & (tpc < 8)), toboe, tsenoe)
        tvooe = np.full(toboe.shape[0], toboe.fill_value)
        tvooe = np.where((tpc == 8), toboe, tvooe)

        self.log.debug(f'Update variables into container')
        container.replace('timestamp', dateTime)
        container.replace('airTemperature', tsen)
        container.replace('virtualTemperature', tvo)

        self.log.debug(f'Add new/derived variables into container')
        ydr_paths = container.get_paths('latitude')
        container.add('stationPressure', ps, ydr_paths)
        container.add('stationPressureQualityMarker', psqm, ydr_paths)
        container.add('stationPressureError', psoe, ydr_paths)

        container.add('airTemperatureQualityMarker', tsenqm, ydr_paths)
        container.add('airTemperatureError', tsenoe, ydr_paths)

        container.add('virtualTemperatureQualityMarker', tvoqm, ydr_paths)
        container.add('virtualTemperatureError', tvooe, ydr_paths)

        self.log.debug(f'container list (updated): {container.list()}')

        return container

    def _make_description(self):
        description = super()._make_description()

        description.add_variables([
            {
                'name': 'ObsValue/stationPressure',
                'source': 'stationPressure',
                'units': 'Pa',
                'longName': 'Station Pressure',
            },
            {
                'name': 'QualityMarker/stationPressure',
                'source': 'stationPressureQualityMarker',
                'units': '',
                'longName': 'Station Pressure Quality Marker',
            },
            {
                'name': 'ObsError/stationPressure',
                'source': 'stationPressureError',
                'units': 'Pa',
                'longName': 'Station Pressure Error',
            },
            {
                'name': 'QualityMarker/airTemperature',
                'source': 'airTemperatureQualityMarker',
                'units': '',
                'longName': 'Air Temperature Quality Marker',
            },
            {
                'name': 'ObsError/airTemperature',
                'source': 'airTemperatureError',
                'units': 'K',
                'longName': 'Air Temperature Error',
            },
            {
                'name': 'QualityMarker/virtualTemperature',
                'source': 'virtualTemperatureQualityMarker',
                'units': '',
                'longName': 'Virtual Temperature Quality Marker',
            },
            {
                'name': 'ObsError/virtualTemperature',
                'source': 'virtualTemperatureError',
                'units': 'K',
                'longName': 'Virtual Temperature Error',
            },
        ])

        return description


# Add main functions create_obs_file or create_obs_group
add_main_functions(AdpupaPrepbufrObsBuilder)
