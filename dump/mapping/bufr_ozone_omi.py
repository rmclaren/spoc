#!/usr/bin/env python3
import os
import numpy as np
import numpy.ma as ma

import bufr
from bufr.obs_builder import ObsBuilder, add_main_functions, add_dummy_variable, map_path


MAPPING_PATH = map_path('bufr_ozone_omi.yaml')


class BufrOzoneOmiObsBuilder(ObsBuilder):
    """
    Class for building observations from omi BUFR data.

    This class extends `ObsBuilder` to include specific logic for processing
    Level-2 retrived total ozone data from OMI Aura

    :param mapping_path: Path to the mapping file.
    :type mapping_path: str
    """

    def __init__(self):
        super().__init__(MAPPING_PATH, log_name=os.path.basename(__file__))

    def make_obs(self, comm, input_path):

        # Get container from mapping file first
        self.log.info('Get container from bufr')
        container = super().make_obs(comm, input_path)

        self.log.debug(f'container list (original): {container.list()}')
        self.log.debug(f'all_sub_categories =  {container.all_sub_categories()}')
        self.log.debug(f'category map =  {container.get_category_map()}')

        # Add new/derived data into container
        for cat in container.all_sub_categories():

            self.log.debug(f'category = {cat}')

            satId = container.get('satelliteId', cat)
            if not np.any(satId):
                self.log.warning(f'category {cat[0]} does not exist in input file')

            self._add_pressures(container, cat)

        # Check
        self.log.debug(f'container list (updated): {container.list()}')
        self.log.debug(f'all_sub_categories {container.all_sub_categories()}')

        return container

    def _make_description(self):
        description = super()._make_description()
        self._add_new_variable_descriptions(description)

        return description

    def _add_new_variable_descriptions(self, description):
        description.add_variables([
            {
                'name': 'MetaData/pressure',
                'source': 'pressure',
                'units': 'Pa',
                'longName': 'Pressure',
            }])

    def _add_pressures(self, container, cat):

        # Add new MetaData variables: MetaData/pressure
        satId = container.get('satelliteId', cat)
        if not satId.size:
            self.log.warning(f'category {cat[0]} does not exist in input file')
            add_dummy_variable(container, 'pressure', cat, 'latitude')
            return

        latitude = container.get('latitude', cat)
        paths = container.get_paths('latitude', cat)

        pressure = np.full_like(latitude, 0)
        container.add('pressure', pressure, paths, cat)


# Add main functions create_obs_file or create_obs_group
add_main_functions(BufrOzoneOmiObsBuilder)
