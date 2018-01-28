from contextlib import suppress
from time import sleep
from logging import getLogger

from raptiformica.actions.mesh import attempt_join_meshnet
from raptiformica.shell.execute import check_nonzero_exit

log = getLogger(__name__)


def loop_rejoin():
    """
    Run the agent to ensure the machine stays in the cluster
    and rejoins it after interruptions
    :return None:
    """
    while True:
        with suppress(Exception):
            attempt_join_meshnet()
        sleep(10)


def _get_program_name():
    """
    Return the program name. This is in a function so it can be
    mocked in the tests.
    :return None:
    """
    return __name__


def agent_already_running():
    """
    Check if the raptiformica agent is already running
    :return None:
    """
    agent_program_name = 'raptiformica.actions.agent'
    allowed_procs = 1 if _get_program_name() == agent_program_name else 0
    check_running = "ps aux | grep 'bin/[r]aptiformica_agent.py' | " \
                    "grep -v screen -i | grep python3 | grep -v 'sh -c' | " \
                    "awk '{{print $2}}' | xargs --no-run-if-empty -I {{}} " \
                    "sh -c \"grep -q docker /proc/{{}}/cgroup 2> /dev/null " \
                    "&& ! grep -q name=systemd:/docker /proc/1/cgroup || echo {{}}\" | " \
                    "wc -l | {{ read li; test $li -gt {}; }}" \
                    "".format(allowed_procs)
    return check_nonzero_exit(check_running)


def run_agent():
    """
    Run the raptiformica agent loop if it is not already running.
    If it is already running exit with zero exit code.
    :return None:
    """
    if agent_already_running():
        log.info("Raptiformica agent already running, not starting a new one")
    else:
        log.info("No raptiformica agent running yet, starting new rejoin loop")
        loop_rejoin()
