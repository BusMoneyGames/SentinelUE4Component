# coding=utf-8
import subprocess
import os
import logging
import pathlib

import ue4_constants

if __package__ is None or __package__ == '':
    import editorutilities as editorUtilities
else:
    from . import editorutilities as editorUtilities


L = logging.getLogger(__name__)


class BaseUE4Commandlet:

    """
    Base class that handles calling engine commandlets and gathering / moving the logs and output to the correct
    location
    """

    def __init__(self, run_config, commandlet_name, log_file_name="", files=[], platform="Win64"):

        self.run_config = run_config
        self.commandlet_name = commandlet_name
        self.environment_config = self.run_config[ue4_constants.ENVIRONMENT_CATEGORY]
        self.sentinel_structure_config = self.run_config[ue4_constants.SENTINEL_PROJECT_STRUCTURE]
        self.files = files
        self.platform = platform

        self.editor_util = editorUtilities.UE4EditorUtilities(run_config, self.platform)

        if log_file_name:
            self.log_file_name = log_file_name
        else:
            self.log_file_name = self.commandlet_name + ".log"

        commandlet_settings_config = self.run_config[ue4_constants.COMMANDLET_SETTINGS]

        self.commandlet_settings = commandlet_settings_config[self.commandlet_name]

        # Getting paths and making them absolute
        self.project_root_path = pathlib.Path(self.environment_config[ue4_constants.UNREAL_PROJECT_ROOT]).resolve()

        L.debug("Project Root Path: %s", self.project_root_path)
        self.engine_root_path = pathlib.Path(self.environment_config[ue4_constants.ENGINE_ROOT_PATH]).resolve()

        self.raw_log_path = self.project_root_path.joinpath(self.environment_config[
                                                                ue4_constants.SENTINEL_ARTIFACTS_ROOT_PATH])

        self.raw_log_path = self.raw_log_path.resolve()

        # Information about the relative structure of ue4
        self.ue_structure = self.run_config[ue4_constants.UNREAL_ENGINE_STRUCTURE]

    def get_commandlet_settings(self):

        commandlet_name = self.commandlet_settings["command"]
        commandlet_prefix = "-run=" + commandlet_name
        # special flags that is used for extracting data from the engine for parsing

        return commandlet_prefix

    def get_command(self):
        """
        Constructs the command that runs the commandlet
        :return:
        """
        commandlet_prefix = self.get_commandlet_settings()

        # special flags that is used for extracting data from the engine for parsing
        commandlet_flags = self.get_commandlet_flags()

        flags_cmd = ""
        if commandlet_flags:
            flags_cmd = "-" + " -".join(commandlet_flags)

        args_list = []
        args_list.append(commandlet_prefix)

        if self.files:
            path_string = self._get_file_list_as_strings()
            args_list.append(path_string)
        if flags_cmd:
            args_list.append(flags_cmd)

        new_args = " ".join(args_list)

        engine_executable = self.editor_util.get_editor_executable_path().as_posix()
        project_file_path = self.editor_util.get_project_file_path().as_posix()

        cmd = engine_executable + " " + project_file_path + " " + new_args + " -LOG=" + self.log_file_name + " -UNATTENDED"
        L.info(cmd)

        return cmd

    def _get_file_list_as_strings(self):

        path_string = ""
        for each_file_to_extract in self.files:

            path_string = path_string + " " + str(each_file_to_extract)

        return path_string

    def get_commandlet_flags(self):

        """
        Search for the the flags in the for the package extract and returns the default one if we find one
        :return:
        """

        commandlet_flags = self.commandlet_settings["flags"]
        return commandlet_flags

    def run(self):
        """
        Runs the command
        :return:
        """

        commandlet_command = self.get_command()

        L.info("Running commandlet: %s", commandlet_command)

        temp_dump_file = os.path.join(self.raw_log_path, self.log_file_name)

        if not os.path.exists(os.path.dirname(temp_dump_file)):
            os.mkdir(os.path.dirname(temp_dump_file))

        popen = subprocess.Popen(commandlet_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        with open(temp_dump_file, "w", encoding='utf-8') as fp:
            for line in popen.stdout:
                line = line.decode('utf-8').rstrip()
                print(line, flush=True)
                print(line, file=fp, flush=True)

        # Waiting for the process to close
        popen.wait()

        # quiting and returning with the correct return code
        if popen.returncode == 0:
            L.info("Command ran successfully")
        else:
            import sys
            L.warning("Process exit with exit code: %s", popen.returncode)
            sys.exit(popen.returncode)

    def get_target_log_file(self):
        """
        Get the path to the log file where it is stored for processing
        :return:  extracted log file
        """

        return os.path.join(self.raw_log_path, self.log_file_name)


def get_commandlet_class(run_config, commandlet_name):
    """
    return a commandlet class if an overwrite exitst
    :param commandlet_name:
    :return:
    """

    return BaseUE4Commandlet(run_config, commandlet_name)
