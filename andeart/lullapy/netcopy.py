import argparse
from shutil import copyfile

from andeart.lullapy.easypath import EasyPath
from andeart.lullapy.shyprint import LogLevel, Logger


class NetCopy:

    # noinspection SpellCheckingInspection
    def __init__(self, silent = False):
        print("NetCopy.")

        # Initialize shyprint
        self.__logger = Logger(self)
        self.__logger.silent = silent

        # Parse CLI args
        parser = argparse.ArgumentParser(description = "Copy built assembly to target directories. Best used as a "
                                                       "post-build event on the VS project.")
        parser.add_argument("--asname", "-a", type = str, metavar = "AssemblyName", default = None,
                            help = "The name of the built assembly (without file-extension).\nNetCopy copies the "
                                   "assembly of this name to the target directories.\nThis name may also additionally "
                                   "be used to create subdirectories if needed.")
        parser.add_argument("--asdir", "-d", type = str, metavar = "AssemblyLocation", default = None,
                            help = "The location of the built assembly.")
        parser.add_argument("--astypes", "-e", type = str, metavar = "AssemblyExtensions", default = "dll",
                            help = "A semicolon-separated list of extensions to apply on the AssemblyName and copy "
                                   "from the AssemblyLocation to the target directories. Ex: \"dll;pdb;xml\". Applies "
                                   "\"dll\" by default")
        parser.add_argument("--targetdirs", "-t", type = str, metavar = "TargetDirectories", default = None,
                            help = "A semicolon-separated list of target directory paths to copy the assembly "
                                   "to.\nOptionally, you can also use this to provide the path to a text file "
                                   "containing the target paths, separated by line-breaks.\nDirectory is created if "
                                   "it does not exist.")
        parser.add_argument("--createsubdir", "-c", action = "store_true", default = True,
                            help = "Specify if a sub-directory with the assembly name should be created in the target "
                                   "directories. Use this as a flag, i.e. simply add -c or --createsubdir without "
                                   "additional args")

        args = parser.parse_args()
        self.__as_name = args.asname
        self.__as_dir = args.asdir
        self.__as_types = args.astypes.split(";")
        self.__target_dirs = args.targetdirs
        self.__create_subdir = args.createsubdir

        self.__logger.log(
            f"Assembly name: {self.__as_name}" + f"\nAssembly directory: {self.__as_dir}" + f"\nAssembly extensions: "
            f"{self.__as_types}" + f"\nTarget directories (unparsed): {self.__target_dirs}" + f"\nShould create "
            f"sub-directory?: {self.__create_subdir}", LogLevel.WARNING)

        # self.__logger.log(str(self.__target_dirs)[1:-1])

        if self.__as_name is None:
            self.__exit_with_error(1, "Assembly name was not provided.", parser.format_help())
        if self.__as_dir is None:
            self.__exit_with_error(1, "Assembly directory was not provided.", parser.format_help())
        aspath = EasyPath.get_file_path(self.__as_dir, self.__as_name, self.__as_types[0])
        self.__logger.log(f"Parsed assembly path: {aspath}")
        if not EasyPath.is_file(aspath):
            self.__exit_with_error(1, "Built assembly does not exist.", parser.format_help())

        # If targetdirs is a file, parse the targetdirs list from its contents
        if EasyPath.is_file(self.__target_dirs):
            with open(self.__target_dirs) as targetdirs_file:
                targetdirs_list = targetdirs_file.readlines()
            targetdirs_list = [line.strip() for line in targetdirs_list]
            self.__target_dirs = targetdirs_list
        # else split the string by semicolon for the list
        else:
            self.__target_dirs = self.__target_dirs.split(";")

        self.__logger.log(f"Parsed target directories: {str(self.__target_dirs)[1:-1]}")


    def copy_files(self):
        for target_dir in self.__target_dirs:
            self.__logger.log_linebreaks(1)
            if self.__create_subdir:
                target_dir = EasyPath.combine(target_dir, self.__as_name)
            self.__logger.log(f"Covering target directory: {target_dir}...")

            if not EasyPath.is_dir(target_dir):
                self.__logger.log("Directory does not exist. Creating new directory.")
                target_dir.mkdir(parents = True)

            # Remove any existing files in the target directory.
            for as_type in self.__as_types:
                self.__logger.log_linebreaks(1)
                # Delete existing files. Add * to the extension glob to delete helper files (ex: .meta files)
                file_pattern = EasyPath.get_file_path(target_dir, self.__as_name, as_type + "*")
                file_paths = EasyPath.glob_cwd(file_pattern)
                for file_path in sorted(file_paths):
                    if EasyPath.is_file(file_path):
                        self.__logger.log(f"Deleting {file_path}", LogLevel.WARNING)
                        file_path.unlink()

                # Copy new files
                source_file_path = EasyPath.get_file_path(self.__as_dir, self.__as_name, as_type)
                if not EasyPath.is_file(source_file_path):
                    self.__exit_with_error(1, f"Could not find expected source file at: {source_file_path}")
                target_file_path = EasyPath.get_file_path(target_dir, self.__as_name, as_type)
                self.__logger.log(f"Copying {source_file_path} to {target_file_path}...")
                copyfile(source_file_path, target_file_path)

        self.__logger.log("Successfully copied all targeted files.", LogLevel.SUCCESS)


    def __exit_with_error(self, error_code, error_msg, usage_info = None):
        self.__logger.log(f"ERROR! Exiting...\nError code: {str(error_code)}\nError message: {error_msg}",
                          LogLevel.ERROR)
        if usage_info is not None:
            self.__logger.log(usage_info, LogLevel.WARNING)
        exit(error_code)


if __name__ == "__main__":
    copy = NetCopy(False)
    copy.copy_files()
