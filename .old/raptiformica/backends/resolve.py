from importlib import import_module


def resolve_backend(backend_name, module):
    return import_module('raptiformica.backends.{0}.{1}'.format(backend_name, module))


def resolve_manage_machine(backend_name):
    return resolve_backend(backend_name, 'manage_machine')


def resolve_status(backend_name):
    return resolve_backend(backend_name, 'status')
