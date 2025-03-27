#!/usr/bin/env python3
import os
import numpy as np
import numpy.ma as ma

import bufr
from bufr.obs_builder import ObsBuilder, add_main_functions


MAPPING_PATH = map_path('bufr_mtiasi.yaml')

class BufrMtiasiObsBuilder(ObsBuilder):
    def __init__(self):
        super().__init__(MAPPING_PATH, log_name=os.path.basename(__file__))
        
    
    def make_obs(self, comm, input_path):
        # Get container from mapping file first
        self.log.info('Get container from bufr')
        container = bufr.Parser(input_path, mapping_path).parse(comm)
    
        self.log.debug(f'container list (original): {container.list()}')
        self.log.debug(f'all_sub_categories =  {container.all_sub_categories()}')
        self.log.debug(f'category map =  {container.get_category_map()}')
    
        # Add new/derived data into container
        for cat in container.all_sub_categories():
    
            self.log.debug(f'category = {cat}')
    
            satid = container.get('variables/satelliteId', cat)
            if satid.size == 0:
                logging(comm, 'WARNING', f'category {cat[0]} does not exist in input file')
    
        # Check
        self.log.debug(f'container list (updated): {container.list()}')
        self.log.debug(f'all_sub_categories {container.all_sub_categories()}')
    
        return container

add_main_functions(BufrMtiasiObsBuilder, uses_categories=True, uses_cache=True)