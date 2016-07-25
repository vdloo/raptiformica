from logging import getLogger

from raptiformica.shell.execute import run_command_print_ready, raise_failure_factory

log = getLogger(__name__)


def verify_ssh_agent_running():
    log.info("Verifying SSH agent is running on the local machine")
    verify_agent_command = ['ssh-add', '-l']
    exit_code, standard_out, _ = run_command_print_ready(
        verify_agent_command,
        failure_callback=raise_failure_factory(
            "There is no SSH agent running on the host or there are no keys in this agent.\n"
            "Please load your ssh agent by running: "
            "eval $(ssh-agent -s); ssh-add ~/.ssh/some_key"
        )
    )
    return exit_code
