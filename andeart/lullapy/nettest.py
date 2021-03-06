import argparse

from andeart.lullapy.easypath import EasyPath
from andeart.lullapy.processrun import ProcessRunner
from andeart.lullapy.shyprint import LogLevel, Logger


class NetTester:

    # noinspection SpellCheckingInspection
    def __init__(self, silent = False):
        print("NetTester.")

        # Initialize shyprint
        self.__logger = Logger(self)
        self.__logger.silent = silent

        # Parse CLI args
        parser = argparse.ArgumentParser(description = "Run tests for VS solution.")
        parser.add_argument("--testspath", "-t", type = str, metavar = "TestsPath", default = None,
                            help = "The path to the tests assembly.")
        args = parser.parse_args()
        self.__tests_path = args.testspath

        self.__logger.log(f"Tests path: {self.__tests_path}", LogLevel.WARNING)

        if self.__tests_path is None:
            self.__exit_with_error(1, "Tests path was not provided for running tests.", parser.format_help())

        if not EasyPath.is_file(self.__tests_path):
            self.__exit_with_error(1, "Tests assembly is not a valid file.", parser.format_help())

        # Initialize processrun
        self.__process_run = ProcessRunner(self.__logger.silent)


    def run_tests(self):
        result = self.__run_vstest(self.__tests_path)
        if result.status != 0:
            self.__exit_with_error(result.status, "Tests were not run successfully.")

        self.__logger.log("Tests were run successfully.", LogLevel.SUCCESS)


    def __run_vstest(self, tests_path):
        self.__logger.log_linebreaks(2)
        self.__logger.log("Running .Net Framework tests...", LogLevel.WARNING)
        cmd_line = f"dotnet vstest {tests_path} /Framework:.NETFramework,Version=v4.7.1 /InIsolation /logger:trx"
        return self.__process_run.run_line(cmd_line)


    def __exit_with_error(self, error_code, error_msg, usage_info = None):
        self.__logger.log(f"ERROR! Exiting...\nError code: {str(error_code)}\nError message: {error_msg}",
                          LogLevel.ERROR)
        if usage_info is not None:
            self.__logger.log(usage_info, LogLevel.WARNING)
        exit(error_code)


if __name__ == "__main__":
    tester = NetTester(False)
    tester.run_tests()
