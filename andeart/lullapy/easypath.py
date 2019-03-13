from pathlib import Path


class EasyPath:

    @staticmethod
    def is_dir(location):
        return Path(location).is_dir()


    @staticmethod
    def is_file(location):
        return Path(location).is_file()


    @staticmethod
    def combine(path1, path2):
        return Path(path1).joinpath(path2)

    @staticmethod
    def get_absolute_path(location):
        strong_path = Path(location);
        strong_path = strong_path.absolute()
        return strong_path


    @staticmethod
    def get_file_path(directory, name, extension):
        full_name = f"{name}.{extension}"
        full_file_path = EasyPath.combine(directory, full_name)
        return full_file_path


    @staticmethod
    def get_directory(location):
        strong_path = Path(location)
        if strong_path.is_file():
            return strong_path.parent
        if strong_path.is_dir():
            return strong_path
        return None


    @staticmethod
    def glob(root_location, file_pattern):
        return Path(root_location).glob(file_pattern)


    @staticmethod
    def glob_cwd(file_pattern):
        return Path.cwd().glob(str(file_pattern))
