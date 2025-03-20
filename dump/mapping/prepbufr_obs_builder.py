#!/usr/bin/env python3

import os
import re
import numpy as np
from pathlib import Path

from datetime import datetime

import bufr
from bufr.obs_builder import ObsBuilder

def map_path(map_file_name):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, map_file_name)

class PrepbufrObsBuilder(ObsBuilder):
    def __init__(self, mapping_path, log_name=os.path.basename(__file__)):
        super().__init__(mapping_path, log_name=log_name)

    def _get_reference_time(self, input_path) -> np.datetime64:
        path_components = Path(input_path).parts
        m = re.match(r'\w+\.(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d{2})', path_components[-4])

        # raise error if pattern not found
        if not m.groups():
            self.log.warning(f'Input file path {input_path} does not contain date information, using the default')
            ref_time = datetime(year=1970, month=1, day=1)
        else:
            ref_time = datetime(year=int(m.group('year')),
                                month=int(m.group('month')),
                                day=int(m.group('day')),
                                hour=int(path_components[-3]))

        return np.datetime64(ref_time)

    def _add_timestamp(self, container: bufr.DataContainer, reference_time: np.datetime64) -> np.array:
        cycle_times = np.array([3600 * t for t in container.get('obsTimeMinusCycleTime')]).astype('timedelta64[s]')
        time = (reference_time + cycle_times).astype('datetime64[s]').astype('int64')
        container.add('timestamp', time, ['*'])
