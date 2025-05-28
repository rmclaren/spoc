#!/usr/bin/env python3
import json
import netCDF4 as nc
import os

import bufr
from bufr.obs_builder import ObsBuilder, add_main_functions, map_path

YAML_NORMAL = False  # current as normal need remap for path2/1bama
INVALID = 1000.0
AMUA_1B = '1bamua'
AMUA_ES = 'esamua'

# Cosmic background temperature. Taken from Mather,J.C. et. al., 1999, "Calibrator Design for the COBE
# Far-Infrared Absolute Spectrophotometer (FIRAS)"Astrophysical Journal, vol 512, pp 511-520
COSMIC_BACKGROUND_TEMP = 2.7253

nc_dir = './aux'


AMUA_1B_MAPPING = map_path('bufr_amsua_1bamua.yaml')
AMUA_ES_MAPPING = map_path('bufr_amsua_esamua.yaml')


class ACCoeff:
    """
    Loads and manages AMSU-A antenna correction coefficients for a specified satellite.

    This class reads correction coefficients from a NetCDF file corresponding to the given
    satellite ID. The coefficients are used for antenna correction in satellite brightness
    temperature processing.

    Attributes:
        n_fovs (int): Number of fields of view (FOVs) in the instrument.
        n_channels (int): Number of instrument channels.
        a_earth (ndarray): Earth-view antenna correction coefficients.
        a_platform (ndarray): Platform-view antenna correction coefficients.
        a_space (ndarray): Space-view antenna correction coefficients.
        a_ep (ndarray): Combined Earth and platform correction coefficients.
        a_sp (ndarray): Space correction coefficients scaled by the cosmic background temperature.

    Args:
        ac_dir (str): Directory containing ACCoeff NetCDF files.
        sat_id (str, optional): Satellite ID string (default 'n19').

    Example:
        ac = ACCoeff('/path/to/ac/files', sat_id='n19')
        print(ac.a_ep.shape)
    """
    def __init__(self, ac_dir, sat_id='n19'):
        file_name = os.path.join(ac_dir, 'amsua_' + sat_id + '.ACCoeff.nc')
        nc_file = nc.Dataset(file_name)
        self.n_fovs = len(nc_file.dimensions['n_FOVs'])
        self.n_channels = len(nc_file.dimensions['n_Channels'])
        self.a_earth = nc_file.variables['A_earth'][:]
        self.a_platform = nc_file.variables['A_platform'][:]
        self.a_space = nc_file.variables['A_space'][:]
        self.a_ep = self.a_earth + self.a_platform
        self.a_sp = self.a_space * COSMIC_BACKGROUND_TEMP


class AmsuaObsBuilder(ObsBuilder):
    """
        ObsBuilder subclass for AMSU-A satellite data.

        Handles mapping, parsing, correction, and merging of AMSU-A 1B and ESA data
        using their respective mapping files.
        """

    def __init__(self):
        """
        Initialize the AmsuaObsBuilder.

        Sets up mapping dictionaries for 1B and ESA data types.
        """

        map_dict = {AMUA_1B: AMUA_1B_MAPPING,
                    AMUA_ES: AMUA_ES_MAPPING}

        super().__init__(map_dict, log_name=os.path.basename(__file__))

    def make_obs(self, comm, input_path):
        """
        Create observation container by parsing and merging 1B and ESA files.

        Parameters
        ----------
        comm : object
            MPI communicator.
        input_path : dict or str
            Dictionary (or JSON string) with keys '1bamua' and 'esamua' specifying file paths.

        Returns
        -------
        container : object
            Combined data container with merged and remapped variables.

        Raises
        ------
        ValueError
            If input_path is not a dictionary with the required keys.
        """

        if isinstance(input_path, str):
            input_path = json.loads(input_path)
        if not (isinstance(input_path, dict) and len(self.map_dict) == 2):
            raise ValueError('The input must be a dict with two items!')

        self.log.info(f'input files: {input_path["esamua"]}, {input_path["1bamua"]}')
        self.log.info(f'maping files: {self.map_dict["esamua"]}, {self.map_dict["1bamua"]}')
        container_es = bufr.Parser(input_path[AMUA_ES], self.map_dict[AMUA_ES]).parse(comm)
        container_1b = bufr.Parser(input_path[AMUA_1B], self.map_dict[AMUA_1B]).parse(comm)

        container = container_es
        self._re_map_variable(container_1b)
        container.append(container_1b)
        return container

    def _remove_ant_corr(self, i, ac, ifov, t):
        """
        Remove antenna correction from brightness temperature.

        Parameters
        ----------
        i : int
            Index of the field of view.
        ac : array-like
            Antenna correction coefficients.
        ifov : array-like
            Field of view numbers.
        t : array-like
            Brightness temperature array.

        Returns
        -------
        array-like
            Brightness temperature with antenna correction removed.
        """

        t = ac.a_ep[i, ifov] * t + ac.a_sp[i, ifov]
        t[(ifov < 1) | (ifov > ac.n_fovs)] = [INVALID]
        return t

    def _apply_ant_corr(self, i, ac, ifov, t):
        # t:              on input, this argument contains the antenna temperatures for the sensor channels.
        t = (t - ac.a_sp[i, ifov]) / ac.a_ep[i, ifov]
        t[(ifov < 1) | (ifov > ac.n_fovs)] = [INVALID]
        return t

    def _apply_corr(self, sat_id, ta, ifov):
        """
        Apply antenna correction to brightness temperature.

        Parameters
        ----------
        sat_id : str
            Satellite ID.
        ta : array-like
            Brightness temperature array.
        ifov : array-like
            Field of view numbers.

        Returns
        -------
        array-like
            Corrected brightness temperature.
        """

        ac = ACCoeff(nc_dir, sat_id=sat_id)
        if sat_id not in ['n15', 'n16']:
            # Convert antenna temperature to brightness temperature
            ifov = ifov.astype(int) - 1
            for i in range(ta.shape[1]):
                self.log.debug(f'inside loop for allpy ta to tb: i = {i}')
                x = ta[:, i]
                if YAML_NORMAL:
                    x = self._apply_ant_corr(i, ac, ifov, x)
                else:
                    x = self._remove_ant_corr(i, ac, ifov, x)
                x[x >= INVALID] = INVALID
                ta[:, i] = x
        return ta

    def _re_map_variable(self, container):
        """
        Remap variables in the data container after parsing.

        Parameters
        ----------
        container : object
            Data container to be remapped.

        Returns
        -------
        None
        """

        # read_bufrtovs.f90
        # antcorr_application.f90
        # search the keyword “ta2tb” for details
        sat_ids = container.all_sub_categories()
        for sat_id in sat_ids:
            self.log.info(f'Converting for {sat_id[0]}, ...')
            ta = container.get('variables/brightnessTemperature', sat_id)
            if ta.shape[0]:
                ifov = container.get('variables/fieldOfViewNumber', sat_id)
                tb = self._apply_corr(sat_id[0], ta, ifov)
                container.replace('variables/brightnessTemperature', tb, sat_id)

                
add_main_functions(AmsuaObsBuilder)
