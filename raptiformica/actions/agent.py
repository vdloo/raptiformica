from time import sleep

from raptiformica.actions.mesh import attempt_join_meshnet


def run_agent():
    """
    Run the agent to ensure the machine stays in the cluster 
    and rejoins it after interruptions
    :return None: 
    """
    while True:
        attempt_join_meshnet()
        sleep(30)
