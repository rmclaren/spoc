#!/usr/bin/env python3
import os
import numpy as np
import numpy.ma as ma

import bufr
from bufr.obs_builder import add_main_functions
from prepbufr_obs_builder import PrepbufrObsBuilder, map_path


MAPPING_PATH = map_path('bufr_sfcshp_prepbufr_mapping.yaml.yaml')

class SfcshpPrepbufrObsBuilder(PrepbufrObsBuilder):
    def __init__(self):
        super().__init__(MAPPING_PATH, log_name=os.path.basename(__file__))

    def _make_description(self):
        description = super._make_description()

        description.add_variables([
            {
                'name': 'MetaData/sequenceNumber',
                'source': 'variables/sequenceNumber',
                'units': '1',
                'longName': 'Sequence Number (Obs Subtype)',
            }
        ])

        return description

    def make_obs(self, comm, input_path):
        """
        Create the ioda sfcshp prepbufr observations:
        - reads values
        - adds sequenceNum

        Parameters
        ----------
        comm: object
                The communicator object (e.g., MPI)
        input_path: str
                The input bufr file
        mapping_path: str
                The input bufr2ioda mapping file
        cycle_time: str
                The cycle in YYYYMMDDHH format
        """

        # Get container from mapping file first
        self.log.info('Get container from bufr')
        container = bufr.Parser(input_path, mapping_path).parse(comm)

        self.log.debug(f'container list (original): {container.list()}')
        self.log.debug(f'Change longitude range from [0,360] to [-180,180]')
        lon = container.get('variables/longitude')
        lon_paths = container.get_paths('variables/longitude')
        lon[lon > 180] -= 360
        lon = ma.round(lon, decimals=2)
        self.log.debug(f'longitude new max/min: ${lon.max()}, ${lon.min()}')

        self.log.debug(f'Do DateTime calculation')
        otmct = container.get('variables/obsTimeMinusCycleTime')
        otmct_paths = container.get_paths('variables/obsTimeMinusCycleTime')
        otmct2 = np.array(otmct)
        cycleTimeSinceEpoch = np.int64(calendar.timegm(time.strptime(str(int(cycle_time)), '%Y%m%d%H')))
        dateTime = self._compute_datetime(cycleTimeSinceEpoch, otmct2)
        min_dateTime_ge_zero = min(x for x in dateTime if x >= 0)
        self.log.debug(f'dateTime min/max = {min_dateTime_ge_zero} {dateTime.max()}')

        self.log.debug(f'Do sequenceNumber (Obs SubType) calculation')
        typ = container.get('variables/observationType')
        typ_paths = container.get_paths('variables/observationType')
        t29 = container.get('variables/obssubtype')
        t29_paths = container.get_paths('variables/obssubtype')
        seqNum = self._compute_sequence_number(typ, t29)
        self.log.debug(f' sequenceNum min/max =  {seqNum.min()} {seqNum.max()}')

        self.log.debug(f'Do tsen and tv calculation')
        tpc = container.get('variables/temperatureEventCode')
        tob = container.get('variables/airTemperatureObsValue')
        tob_paths = container.get_paths('variables/airTemperatureObsValue')
        tsen = np.full(tob.shape[0], tob.fill_value)
        tsen = np.where(((tpc >= 1) & (tpc < 8)), tob, tsen)
        tvo = np.full(tob.shape[0], tob.fill_value)
        tvo = np.where((tpc == 8), tob, tvo)

        self.log.debug( f'Do tsen and tv QM calculations')
        tobqm = container.get('variables/airTemperatureQualityMarker')
        tsenqm = np.full(tobqm.shape[0], tobqm.fill_value)
        tsenqm = np.where(((tpc >= 1) & (tpc < 8)), tobqm, tsenqm)
        tvoqm = np.full(tobqm.shape[0], tobqm.fill_value)
        tvoqm = np.where((tpc == 8), tobqm, tvoqm)

        self.log.debug(f'Do tsen and tv ObsError calculations')
        toboe = container.get('variables/airTemperatureObsError')
        tsenoe = np.full(toboe.shape[0], toboe.fill_value)
        tsenoe = np.where(((tpc >= 1) & (tpc < 8)), toboe, tsenoe)
        tvooe = np.full(toboe.shape[0], toboe.fill_value)
        tvooe = np.where((tpc == 8), toboe, tvooe)

        self.log.debug(f'Update variables in container')
        container.replace('variables/longitude', lon)
        container.replace('variables/timestamp', dateTime)
        container.replace('variables/airTemperatureObsValue', tsen)
        container.replace('variables/airTemperatureQualityMarker', tsenqm)
        container.replace('variables/airTemperatureObsError', tsenoe)
        container.replace('variables/virtualTemperatureObsValue', tvo)
        container.replace('variables/virtualTemperatureQualityMarker', tvoqm)
        container.replace('variables/virtualTemperatureObsError', tvooe)

        self.log.debug('DEBUG', f'Add variables to container')
        container.add('variables/sequenceNumber', seqNum, typ_paths)

        # Check
        self.log.debug(f'container list (updated): {container.list()}')

        return container

    def _compute_sequence_number(self, typ, t29):
        """
        Compute sequenceNumber

        Parameters:
            typ: observation Type (obsType)
            t29: data dump report type

        Returns:
            Masked array of sequenceNumber values
        """

        sequenceNumber = np.zeros(typ.shape, dtype=np.int32)
        for i in range(len(typ)):
            if (typ[i] == 180 or typ[i] == 280):
                if (t29[i] > 555 and t29[i] < 565):
                    sequenceNumber[i] = 0
                else:
                    sequenceNumber[i] = 1

        return sequenceNumber


    def _compute_datetime(self, cycleTimeSinceEpoch, dhr):
        """
        Compute dateTime using the cycleTimeSinceEpoch and Cycle Time
            minus Cycle Time

        Parameters:
            cycleTimeSinceEpoch: Time of cycle in Epoch Time
            dhr: Observation Time Minus Cycle Time

        Returns:
            Masked array of dateTime values
        """

        int64_fill_value = np.int64(0)

        dateTime = np.zeros(dhr.shape, dtype=np.int64)
        for i in range(len(dateTime)):
            if ma.is_masked(dhr[i]):
                continue
            else:
                dateTime[i] = np.int64(dhr[i]*3600) + cycleTimeSinceEpoch

        dateTime = ma.array(dateTime)
        dateTime = ma.masked_values(dateTime, int64_fill_value)

        return dateTime

add_main_functions(SfcshpPrepbufrObsBuilder)
