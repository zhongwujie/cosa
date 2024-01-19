import pathlib
import shutil

import cosa.utils as utils
from cosa.parse_workload import *

logger = utils.logger

def run_config(mapspace, spatial_config, perm_config, factor_config, status_dict=dict(), run_gen_map=True,
               run_gen_tc=False, run_sim_test=False, output_path='output_dir', spatial_configs=None, exe='sim_test',
               valid_check=False, nb_sim=False, outer_loopcount_limit=256, delete_invalid=False):
    mapspace.reset_mapspace(spatial_config, spatial_configs)
    mapspace.update_mapspace(perm_config, factor_config)

    # if it does not pass the check skip it
    if valid_check:
        valid_mapping, _, _, _, _ = mapspace.valid_check()
        if not valid_mapping:
            status_dict = {'run_status': [0]}
            return status_dict
            # raise ValueError()

    # get the config_space_str as key to the status_dict
    # status_dict_key = mapspace.config_space_str(spatial_config, perm_config, factor_config)
    key_strs = [mapspace.arch.config_str(), mapspace.prob.config_str(), mapspace.config_str()[0],
                mapspace.config_str()[1]]

    status_dict_key = '+'.join(key_strs)
    status_dict_val = status_dict.get(status_dict_key)

    if status_dict_val:
        finish_run = True
        if run_gen_map:
            if status_dict_val['run_status'][0] == -1:
                finish_run = False
        if run_gen_tc:
            if status_dict_val['run_status'][1] == -1:
                finish_run = False
        if run_sim_test:
            if status_dict_val['run_status'][2] == -1:
                finish_run = False
        if finish_run:
            logger.info("status_dict: {}".format(status_dict[status_dict_key]))
            # return
            return status_dict_val
    else:
        idx = 0
        # idx can go out of index
        # idx = mapspace.get_idx_from_factor_config(factor_config)
        status_dict_val = {}
        status_dict_val['run_status'] = [-1, -1, -1]
        status_dict_val['cycle_results'] = [-1] * 6  # un-initialized
        status_dict_val['utilized_capacity'] = []
        status_dict[status_dict_key] = status_dict_val

    mapping = mapspace.generate_mapping()

    output_base = pathlib.Path(output_path).resolve()
    # print(output_dir)

    status_dict[status_dict_key]['output_dir'] = str(output_base)

    map_path = output_base / 'map_16.yaml'

    utils.store_yaml(map_path, mapping)
    
    return status_dict[status_dict_key]


def get_perm_size(mapspace, spatial_config, perm_config, factor_config, status_dict, output_path='output_dir',
                  spatial_configs=None, exe='sim_test', valid_check=False, outer_loopcount_limit=None):
    status_dict = run_config(mapspace, spatial_config, perm_config, factor_config, status_dict, run_gen_map=True,
                             run_gen_tc=True, run_sim_test=False, output_path=output_path,
                             spatial_configs=spatial_configs, exe=exe, valid_check=valid_check,
                             outer_loopcount_limit=outer_loopcount_limit)
    sizes = []
    for var in ['Weights', 'Inputs', 'Outputs']:
        sizes.append(status_dict['cost']['{}_milp'.format(var)])
    return sizes


def get_spatial_size(mapspace, spatial_config, perm_config, factor_config, status_dict, output_path='output_dir',
                     spatial_configs=None, exe='sim_test', valid_check=False, outer_loopcount_limit=None):
    status_dict = run_config(mapspace, spatial_config, perm_config, factor_config, status_dict, run_gen_map=True,
                             run_gen_tc=True, run_sim_test=False, output_path=output_path,
                             spatial_configs=spatial_configs, exe=exe, valid_check=valid_check,
                             outer_loopcount_limit=outer_loopcount_limit)
    sizes = []
    for var in ['Weights', 'Inputs', 'Outputs']:
        sizes.append(status_dict['cost']['{}_milp_spatial'.format(var)])
    return sizes
