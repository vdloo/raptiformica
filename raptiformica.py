#!/usr/bin/env python3
import sys
from raptiformica.cmdline.main import run_main

if __name__ == '__main__':
    run_main()
else:
    raise RuntimeError("This script is an entry point and can not be imported")



# main()
# import subprocess


# def start_consul_agent():
#     print("starting consul agent")
#     subprocess.Popen("consul agent -data-dir=/tmp/consul --bootstrap-expect=3 -server".split(),
#                      stdout=subprocess.DEVNULL)

    
# def assimilate():
#     # run playbooks
#     print('assimilate')
#     start_consul_agent()



#from sshtunnel import SSHTunnelForwarder
#from time import sleep
#import os
#with SSHTunnelForwarder(
#    ('s1.rickvandeloo.com', 443),
#    ssh_private_key='/home/vdloo/.ssh/id_rsa',
#    ssh_username="vdloo",
#    remote_bind_address=('127.0.0.1', 8001)) as server:
#
#    print(server.local_bind_port)
#        # press Ctrl-C for stopping
#    sleep(5)
#    server.close()
#print('FINISH!')

