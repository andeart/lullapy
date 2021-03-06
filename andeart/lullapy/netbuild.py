import argparse
import os
import platform

from andeart.lullapy.easypath import EasyPath
from andeart.lullapy.processrun import ProcessRunner
from andeart.lullapy.shyprint import LogLevel, Logger


class NetBuilder:

    # noinspection SpellCheckingInspection
    def __init__(self, silent = False):
        print("NetBuilder.")

        # Initialize shyprint
        self.__logger = Logger(self)
        self.__logger.silent = silent

        # Parse CLI args
        parser = argparse.ArgumentParser(description = "Build VS solution along with project tests.")
        parser.add_argument("--slnpath", "-s", type = str, metavar = "SolutionPath", default = None,
                            help = "The path to the solution to build.")
        parser.add_argument("--config", "-c", choices = ["Release", "Debug"], type = str, metavar = "ConfigurationName",
                            default = "Debug", help = "The ConfigurationName to be used with MSBuild.")
        args = parser.parse_args()
        self.__sln_path = args.slnpath
        self.__config_name = args.config

        self.__logger.log(f"Solution path: {self.__sln_path}" + f"\nConfiguration: {self.__config_name}",
                          LogLevel.WARNING)

        if self.__sln_path is None:
            self.__exit_with_error(1, "Solution path was not provided for build.", parser.format_help())

        if not EasyPath.is_file(self.__sln_path):
            self.__exit_with_error(1, "Solution path is not a valid file.", parser.format_help())

        # Initialize processrun
        self.__process_run = ProcessRunner(self.__logger.silent)


    def build(self):

        result = self.__run_msbuild(self.__sln_path, self.__config_name)
        if result.status != 0:
            self.__exit_with_error(result.status, "MSBuild failed to run successfully on solution.")

        self.__logger.log("Build was successful.", LogLevel.SUCCESS)


    def __run_msbuild(self, sln_path, config_name):
        self.__logger.log_linebreaks(2)
        self.__logger.log("Building solution...", LogLevel.WARNING)
        msbuild_path = self.__locate_msbuild()
        cmd_line = f"{msbuild_path} {sln_path} -p:Configuration={config_name}"
        return self.__process_run.run_line(cmd_line)


    def __locate_vs_installation(self):
        vswhere_path = self.__locate_vs_where("ProgramFiles")
        if vswhere_path is None:
            # Try (x86) directory...
            vswhere_path = self.__locate_vs_where("ProgramFiles(x86)")
            if vswhere_path is None:
                return None

        vswhere_cmd = f"{vswhere_path} -latest -requires Microsoft.Component.MSBuild"
        final_path = None

        result = self.__process_run.run_line(vswhere_cmd)
        for item in result.output.splitlines():
            split_item = item.split(":", 1)
            if split_item[0] == "installationPath":
                final_path = split_item[1].strip()
                self.__logger.log(f"VS Installation was found at: {final_path}", LogLevel.SUCCESS)
                self.__logger.log_linebreaks(2)

        return final_path

    def __locate_vs_where(self, program_files_var):
        vswhere_sub_path = "/Microsoft Visual Studio/Installer/vswhere.exe"
        program_files_location = os.environ.get(program_files_var)
        if program_files_location is None:
            self.__logger.log(f"No {program_files_location} variable was found in environment.", LogLevel.WARNING)
            return None
        vswhere_path = program_files_location + vswhere_sub_path
        if not EasyPath.is_file(vswhere_path):
            self.__logger.log(f"No executable found at {vswhere_path}", LogLevel.WARNING)
            return None
        return vswhere_path



    def __locate_msbuild(self):
        if platform.system() != "Windows":
            self.__logger.log("Not on Windows- MSBuild is usually available on PATH here.", LogLevel.WARNING)
            return "msbuild"

        self.__logger.log("On Windows OS. Locating MSBuild via vswhere...")
        vs_installation_path = self.__locate_vs_installation()
        if vs_installation_path is None:
            self.__logger.log("VS Installation was not found.", LogLevel.ERROR)
            return None

        vs_msbuild_pattern = "MSBuild/*/Bin/MSBuild.exe"
        locations = EasyPath.glob(vs_installation_path, vs_msbuild_pattern)
        for location in sorted(locations, reverse = True):
            if EasyPath.is_file(location):
                return location

        return None


    def __exit_with_error(self, error_code, error_msg, usage_info = None):
        self.__logger.log(f"ERROR! Exiting...\nError code: {str(error_code)}\nError message: {error_msg}",
                          LogLevel.ERROR)
        if usage_info is not None:
            self.__logger.log(usage_info, LogLevel.WARNING)
        exit(error_code)


if __name__ == "__main__":
    builder = NetBuilder(False)
    builder.build()
