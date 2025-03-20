#!/usr/bin/env python3
import calendar
import os
import numpy as np
import numpy.ma as ma

import bufr
from bufr.obs_builder import add_main_functions
from prepbufr_obs_builder import PrepbufrObsBuilder, map_path


MAPPING_PATH = map_path('bufr_sfcshp_prepbufr_mapping.yaml')

class SfcshpPrepbufrObsBuilder(PrepbufrObsBuilder):
    def __init__(self):
        super().__init__(MAPPING_PATH, log_name=os.path.basename(__file__))

    def _make_description(self):
        description = super._make_description()

        description.add_variables([
            {
                'name': "MetaData/dateTime",
                'source': 'timestamp',
                'units': "seconds since 1970-01-01T00:00:00Z",
                'longName': "Observation Time"
            },
            {
                'name': 'MetaData/sequenceNumber',
                'source': 'sequenceNumber',
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
        container = self.super().make_obs(comm, input_path)

        self.log.debug(f'container list (original): {container.list()}')
        self.log.debug(f'Change longitude range from [0,360] to [-180,180]')
        lon = container.get('longitude')
        lon_paths = container.get_paths('longitude')
        lon[lon > 180] -= 360
        lon = ma.round(lon, decimals=2)
        self.log.debug(f'longitude new max/min: ${lon.max()}, ${lon.min()}')

        self.log.debug(f'Do DateTime calculation')
        self._add_timestamp(container, self._get_reference_time(input_path))

        self.log.debug(f'Do sequenceNumber (Obs SubType) calculation')
        typ = container.get('observationType')
        typ_paths = container.get_paths('observationType')
        t29 = container.get('obssubtype')
        t29_paths = container.get_paths('obssubtype')
        seqNum = self._compute_sequence_number(typ, t29)
        self.log.debug(f' sequenceNum min/max =  {seqNum.min()} {seqNum.max()}')

        self.log.debug(f'Do tsen and tv calculation')
        tpc = container.get('temperatureEventCode')
        tob = container.get('airTemperatureObsValue')
        tob_paths = container.get_paths('airTemperatureObsValue')
        tsen = np.full(tob.shape[0], tob.fill_value)
        tsen = np.where(((tpc >= 1) & (tpc < 8)), tob, tsen)
        tvo = np.full(tob.shape[0], tob.fill_value)
        tvo = np.where((tpc == 8), tob, tvo)

        self.log.debug( f'Do tsen and tv QM calculations')
        tobqm = container.get('airTemperatureQualityMarker')
        tsenqm = np.full(tobqm.shape[0], tobqm.fill_value)
        tsenqm = np.where(((tpc >= 1) & (tpc < 8)), tobqm, tsenqm)
        tvoqm = np.full(tobqm.shape[0], tobqm.fill_value)
        tvoqm = np.where((tpc == 8), tobqm, tvoqm)

        self.log.debug(f'Do tsen and tv ObsError calculations')
        toboe = container.get('airTemperatureObsError')
        tsenoe = np.full(toboe.shape[0], toboe.fill_value)
        tsenoe = np.where(((tpc >= 1) & (tpc < 8)), toboe, tsenoe)
        tvooe = np.full(toboe.shape[0], toboe.fill_value)
        tvooe = np.where((tpc == 8), toboe, tvooe)

        self.log.debug(f'Update variables in container')
        container.replace('longitude', lon)
        container.replace('airTemperatureObsValue', tsen)
        container.replace('airTemperatureQualityMarker', tsenqm)
        container.replace('airTemperatureObsError', tsenoe)
        container.replace('virtualTemperatureObsValue', tvo)
        container.replace('virtualTemperatureQualityMarker', tvoqm)
        container.replace('virtualTemperatureObsError', tvooe)

        self.log.debug('DEBUG', f'Add variables to container')
        container.add('sequenceNumber', seqNum, typ_paths)

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
