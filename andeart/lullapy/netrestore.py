import argparse

from andeart.lullapy.easypath import EasyPath
from andeart.lullapy.processrun import ProcessRunner
from andeart.lullapy.shyprint import LogLevel, Logger


class NetRestore:

    # noinspection SpellCheckingInspection
    def __init__(self, silent = False):
        print("NetRestore.")

        # Initialize shyprint
        self.__logger = Logger(self)
        self.__logger.silent = silent

        # Parse CLI args
        parser = argparse.ArgumentParser(description = "Restore dependencies in VS solution.")
        parser.add_argument("--slnpath", "-s", type = str, metavar = "SolutionPath", default = None,
                            help = "The path to the solution to restore.")
        args = parser.parse_args()
        self.__sln_path = args.slnpath

        self.__logger.log(f"Solution path: {self.__sln_path}", LogLevel.WARNING)

        if self.__sln_path is None:
            self.__exit_with_error(1, "Solution path was not provided for build.", parser.format_help())

        if not EasyPath.is_file(self.__sln_path):
            self.__exit_with_error(1, "Solution path is not a valid file.", parser.format_help())

        # Initialize processrun
        self.__process_run = ProcessRunner(self.__logger.silent)


    def restore(self):
        result = self.__run_nuget_restore(self.__sln_path)
        if result.status != 0:
            self.__exit_with_error(result.status, "NuGet packages for solution were not restored correctly.")

        self.__logger.log("NuGet packages for solution were restored successfully.", LogLevel.SUCCESS)


    def __run_nuget_restore(self, sln_path):
        self.__logger.log_linebreaks(2)
        self.__logger.log("Running nuget restore...", LogLevel.WARNING)
        return self.__process_run.run_line(f"nuget restore {sln_path}")


    def __exit_with_error(self, error_code, error_msg, usage_info = None):
        self.__logger.log(f"ERROR! Exiting...\nError code: {str(error_code)}\nError message: {error_msg}",
                          LogLevel.ERROR)
        if usage_info is not None:
            self.__logger.log(usage_info, LogLevel.WARNING)
        exit(error_code)


if __name__ == "__main__":
    restore = NetRestore(False)
    restore.restore()
