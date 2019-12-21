import collections
import shlex
import subprocess

from andeart.lullapy.shyprint import Logger


class ProcessRunner:

    def __init__(self, silent = False):
        self.__logger = Logger(self)
        self.__logger.silent = silent
        self.__logger.log("ProcessRunner initialised.")


    def run_line(self, cmd_line):        
        self.__logger.log("Running command: " + cmd_line)
        args = shlex.split(cmd_line, posix=False)
        return self.run_args(args)


    def run_args(self, args):
        process = subprocess.Popen(args, stdout = subprocess.PIPE, shell = False)
        (output, error) = process.communicate()
        return_code = process.wait()
        output = str(output.decode("utf-8"))
        self.__logger.log("Command output:\n" + output + "\n" + "Command exit-status/return-code: " + str(return_code))
        result = SubprocessOutputStatus(output, return_code)
        return result


SubprocessOutputStatus = collections.namedtuple("SubprocessOutputStatus", ["output", "status"])
