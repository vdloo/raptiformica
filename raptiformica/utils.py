from subprocess import Popen, PIPE


def run_command(command_as_list):
    """
    Run a command locally in the shell and return the exit code, standard out and standard error as a tuple
    :param list command_as_list: The command as a list. I.e. ['/bin/ls', '/root']
    :return tuple (exit code, standard out, standard error):
    """
    process = Popen(command_as_list, stdout=PIPE, stderr=PIPE)
    standard_out, standard_error = process.communicate()
    exit_code = process.returncode
    return exit_code, standard_out, standard_error
