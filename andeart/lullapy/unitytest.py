import argparse
import os
from xml.etree import ElementTree

from andeart.lullapy.easypath import EasyPath
from andeart.lullapy.processrun import ProcessRunner
from andeart.lullapy.shyprint import LogLevel, Logger


class UnityTester:
    test_results_file_pattern = "TestResults-*.xml"


    # noinspection SpellCheckingInspection
    def __init__(self, silent = False):
        print("UnityTester.")

        # Initialize shyprint
        self.__logger = Logger(self)
        self.__logger.silent = silent

        # Parse CLI args
        parser = argparse.ArgumentParser(description = "Run Unity tests for Unity project, both edit and play modes.")
        parser.add_argument("--unitypath", "-u", type = str, metavar = "UnityExePath", default = None,
                            help = "The path to the Unity executable.")
        parser.add_argument("--projectpath", "-p", type = str, metavar = "ProjectPath", default = None,
                            help = "The path to the Unity project to run tests in.")
        parser.add_argument("--testmode", "-m", choices = ["editmode", "playmode"], type = str, metavar = "TestMode",
                            default = "editmode", help = "The test-mode of tests to run, i.e. editmode or playmode.")
        parser.add_argument("--resultspath", "-r", type = str, metavar = "TestResultsPath", default = None,
                            help = "The path to the test results output file.")

        args = parser.parse_args()
        self.__unity_path = args.unitypath
        self.__project_path = args.projectpath
        self.__test_mode = args.testmode
        self.__results_path = args.resultspath

        self.__logger.log(
            f"Unity executable path: {self.__unity_path}" + f"\nProject path: {self.__project_path}" + f"\nTest mode: "
            f"{self.__test_mode}" + f"\nResults output path: {self.__results_path}", LogLevel.WARNING)

        if self.__unity_path is None:
            self.__exit_with_error(1, "Unity executable was not provided for running tests.", parser.format_help())

        if self.__project_path is None:
            self.__exit_with_error(1, "Unity project that contains tests was not provided.", parser.format_help())

        if self.__results_path is None:
            self.__logger.log("Explicit test-results output file was not provided. Test results will be saved to the "
                              "default file.",
                              LogLevel.WARNING)

        # Initialize processrun
        self.__process_run = ProcessRunner(self.__logger.silent)


    def run_tests(self):
        result = self.__run_unity_tests(self.__unity_path, self.__project_path, self.__test_mode, self.__results_path)

        if self.__results_path is not None and EasyPath.is_file(self.__results_path):
            self.__log_unity_results(self.__results_path)
        else:
            latest_results = self.__get_latest_test_results(self.__project_path)
            if latest_results is not None:
                self.__log_unity_results(EasyPath.get_absolute_path(latest_results))

        if result.status != 0:
            self.__exit_with_error(result.status, "Unity TestRunner tests were not run successfully.")

        self.__logger.log("Unity TestRunner tests were run successfully.", LogLevel.SUCCESS)


    def __run_unity_tests(self, unity_app_path, project_path, test_mode, results_path):
        self.__logger.log_linebreaks(2)
        self.__logger.log("Running Unity TestRunner tests...", LogLevel.WARNING)

        if not EasyPath.is_file(unity_app_path):
            self.__exit_with_error(1, f"Unity app path: {unity_app_path} : is not an executable.")

        if not EasyPath.is_dir(project_path):
            self.__exit_with_error(1, f"Unity project path: {project_path} : is not a project directory.")

        cmd_line = f"{unity_app_path} -batchmode -runTests -projectPath {project_path} -testPlatform {test_mode}"
        if results_path is not None:
            cmd_line += f" -testResults {results_path}"

        return self.__process_run.run_line(cmd_line)


    def __get_latest_test_results(self, project_path):
        # If we've let Unity auto-generate the TestResults file, we simply select the most recently modified one.
        files = EasyPath.glob(project_path, self.test_results_file_pattern)
        files = sorted(files, key = os.path.getmtime, reverse = True)
        latest_file = next(iter(files), None)
        self.__logger.log("Most recent TestResults file found at: " + str(latest_file), LogLevel.WARNING)
        return latest_file


    def __log_unity_results(self, results_path):
        file = ElementTree.parse(str(results_path))
        file_root = file.getroot()
        # for test_case in file_root.findall("test-case"):
        #     self.__logger.log(test_case)

        for test_case in file.iter("test-case"):
            self.__logger.log_linebreaks(1)
            self.__logger.log("Test case ID: " + test_case.get("id"), LogLevel.WARNING)
            self.__logger.log("Full name: " + test_case.get("fullname"))
            result_status = test_case.get("result")
            self.__logger.log("Status: " + result_status,
                              LogLevel.SUCCESS if result_status == "Passed" else LogLevel.ERROR)
            self.__logger.log_linebreaks(1)


    def __exit_with_error(self, error_code, error_msg, usage_info = None):
        self.__logger.log(f"ERROR! Exiting...\nError code: {str(error_code)}\nError message: {error_msg}",
                          LogLevel.ERROR)
        if usage_info is not None:
            self.__logger.log(usage_info, LogLevel.WARNING)
        exit(error_code)


if __name__ == "__main__":
    tester = UnityTester(False)
    tester.run_tests()
