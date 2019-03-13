from argparse import ArgumentParser

from andeart.lullapy.easypath import EasyPath
from andeart.lullapy.shyprint import LogLevel, Logger


class PlainExist:

    def __init__(self, silent = False):
        print("PlainExist.")

        # Initialize shyprint
        self.__logger = Logger(self)
        self.__logger.silent = silent

        # Parse CLI args
        parser = ArgumentParser(description = "A simple check to see if files or directories exist.")
        parser.add_argument("--files", "-f", type = str, metavar = "FilePaths", default = None,
                            help = "A semicolon-separated list of paths to the files to check. Use at least one of "
                                   "this or -d for directories.")
        parser.add_argument("--dirs", "-d", type = str, metavar = "DirectoryPaths", default = None,
                            help = "A semicolon-separated list of paths to the directories to check. Use at least one "
                                   "of this or -f for files.")
        args = parser.parse_args()
        self.__file_paths = args.files
        self.__dir_paths = args.dirs

        if self.__file_paths is None and self.__dir_paths is None:
            self.__exit_with_error(1, "Neither file nor directory paths were provided for check.", parser.format_help())

        if self.__file_paths is not None:
            self.__file_paths = self.__file_paths.split(";")
        if self.__dir_paths is not None:
            self.__dir_paths = self.__dir_paths.split(";")
        self.__logger.log(f"Parsed file paths: {self.__file_paths}" + f"\nParsed directory paths: {self.__dir_paths}",
                          LogLevel.WARNING)


    def verify(self):
        self.__verify_files()
        self.__verify_dirs()
        self.__logger.log("All files and directories were successfully verified.", LogLevel.SUCCESS)


    def __verify_files(self):
        if self.__file_paths is None:
            return
        for file_path in self.__file_paths:
            if EasyPath.is_file(file_path):
                self.__logger.log(f"File was successfully found at: {file_path}")
            else:
                self.__exit_with_error(1, f"File was not successfully found at: {file_path}")


    def __verify_dirs(self):
        if self.__dir_paths is None:
            return
        for dir_path in self.__dir_paths:
            if EasyPath.is_dir(dir_path):
                self.__logger.log(f"Directory was successfully found at: {dir_path}")
            else:
                self.__exit_with_error(1, f"Directory was not successfully found at: {dir_path}")


    def __exit_with_error(self, error_code, error_msg, usage_info = None):
        self.__logger.log(f"ERROR! Exiting...\nError code: {str(error_code)}\nError message: {error_msg}",
                          LogLevel.ERROR)
        if usage_info is not None:
            self.__logger.log(usage_info, LogLevel.WARNING)
        exit(error_code)


if __name__ == "__main__":
    check = PlainExist(False)
    check.verify()
