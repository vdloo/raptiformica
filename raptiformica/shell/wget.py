from raptiformica.shell.execute import run_critical_unbuffered_command_print_ready
from raptiformica.utils import retry

WGET_TIMEOUT = 15


@retry(attempts=3, expect=(TimeoutError,))
def wget(url, host=None, port=22, failure_message='Failed retrieving file'):
    """
    Download a file on the remote host
    The wget command use --no-clobber so it is idempotent
    :param url: the url to wget
    :param str host: hostname or ip of the remote machine, or None for the local machine
    :param int port: port to use to connect to the remote machine over ssh
    :param str failure_message: Message to error out with if file could not
    be retrieved
    :return None:
    """
    run_critical_unbuffered_command_print_ready(
        ['wget', '-4', '-nc', url], host=host, port=port,
        failure_message=failure_message, timeout=WGET_TIMEOUT
    )
