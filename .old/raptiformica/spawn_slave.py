from raptiformica.slave_machine import slave_machine
from raptiformica.spawn_machine import spawn_machine


def spawn_slave():
    new_machine_directory = spawn_machine()
    slave_machine(new_machine_directory)

spawn_slave()