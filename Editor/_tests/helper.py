import os
import pathlib
import CONSTANTS
import json



def read_config(config_dir):
    config_dir = pathlib.Path(config_dir).resolve()

    if not config_dir.exists():
        print("Unable to find a run config directory at: %", str(config_dir))
    else:
        pass
        # print("Reading Config from directory: ", str(config_dir))

    run_config = {}

    for each_file in config_dir.glob("**/*.json"):

        f = open(str(each_file))
        json_data = json.load(f)
        f.close()

        run_config.update(json_data)

    env_category = run_config[CONSTANTS.ENVIRONMENT_CATEGORY]
    relative_project_path = pathlib.Path(env_category[CONSTANTS.UNREAL_PROJECT_ROOT])
    project_root = config_dir.joinpath(relative_project_path).resolve()

    env_category[CONSTANTS.UNREAL_PROJECT_ROOT] = str(project_root)
    run_config[CONSTANTS.ENVIRONMENT_CATEGORY] = env_category

    return run_config


def get_path_config_for_test():

    # Test config file
    path = pathlib.Path("../../defaultConfig").resolve()

    config = read_config(path)

    return config

