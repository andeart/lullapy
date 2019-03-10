import argparse
from xml.etree import ElementTree

from andeart.lullapy.easypath import EasyPath
from andeart.lullapy.processrun import ProcessRunner
from andeart.lullapy.shyprint import LogLevel, Logger


class FodyCleaner:

    # noinspection SpellCheckingInspection
    def __init__(self, silent = False):
        print("FodyCleaner.")

        # Initialize shyprint
        self.__logger = Logger(self)
        self.__logger.silent = silent

        # Parse CLI args
        parser = argparse.ArgumentParser(
            description = "Clean Fody references from all projects in VS solution directory.")
        parser.add_argument("--slnpath", "-s", type = str, metavar = "SolutionPath", default = None,
                            help = "The path to the solution whose directory (or the path to that directory itself) "
                                   "contains all the targeted projects.")
        args = parser.parse_args()
        sln_path = args.slnpath

        if sln_path is None:
            self.__exit_with_error(1, "Solution path is not provided for build.", parser.format_help())

        self.__dir_path = EasyPath.get_directory(sln_path)

        # Initialize processrun
        self.__process_run = ProcessRunner(self.__logger.silent)


    def clean(self):
        exit_code = self.__clean_refs(self.__dir_path)
        if exit_code != 0:
            self.__exit_with_error(exit_code, "Fody references in projects were not removed successfully.")

        self.__logger.log("All existing Fody references were removed successfully.", LogLevel.SUCCESS)


    def __clean_refs(self, dir_path):
        self.__logger.log_linebreaks(2)
        self.__logger.log(f"Cleaning Fody references...", LogLevel.WARNING)

        packages_path_format = dir_path + "*/*/packages.config"
        file_paths = EasyPath.glob_cwd(packages_path_format)
        package_keys = [".//package[@id=\"Costura.Fody\"]", ".//package[@id=\"Fody\"]"]
        for file_path in file_paths:
            self.__logger.log(f"Searching for Fody references in {file_path}.")
            file = ElementTree.parse(file_path)
            file_root = file.getroot()
            was_ref_found = False
            for package in package_keys:
                elem = file_root.find(package)
                if elem is not None:
                    file_root.remove(elem)
                    was_ref_found = True
            if was_ref_found:
                file.write(file_path, encoding = "utf-8", xml_declaration = True)
                self.__logger.log(f"Cleaned Fody refs in {file_path}.", LogLevel.WARNING)
        return 0


    def __exit_with_error(self, error_code, error_msg, usage_info = None):
        self.__logger.log("ERROR! Exiting..." + f"\nError code: {str(error_code)}" + f"\nError message: {error_msg}",
                          LogLevel.ERROR)
        if usage_info is not None:
            self.__logger.log(usage_info, LogLevel.WARNING)
        exit(error_code)


if __name__ == "__main__":
    cleaner = FodyCleaner(False)
    cleaner.clean()
