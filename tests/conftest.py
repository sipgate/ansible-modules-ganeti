import pytest


################################################################################################
# This code is from the ansible documentation:                                                 #
# https://docs.ansible.com/ansible/2.9/dev_guide/testing_units_modules.html#a-complete-example #
################################################################################################

class AnsibleExitJson(Exception):
    """Exception class to be raised by module.exit_json and caught by the test case"""
    pass


class AnsibleFailJson(Exception):
    """Exception class to be raised by module.fail_json and caught by the test case"""
    pass


def exit_json(*args, **kwargs):
    """function to patch over exit_json; package return data into an exception"""
    if 'changed' not in kwargs:
        kwargs['changed'] = False
    raise AnsibleExitJson(kwargs)


def get_bin_path(self, arg, required=False):
    """Mock AnsibleModule.get_bin_path"""
    if arg.endswith('my_command'):
        return '/usr/bin/my_command'
    else:
        if required:
            fail_json(msg='%r not found !' % arg)


def fail_json(*args, **kwargs):
    """function to patch over fail_json; package return data into an exception"""
    kwargs['failed'] = True
    raise AnsibleFailJson(kwargs)


def set_module_args(args):
    import json
    from ansible.module_utils import basic
    from ansible.module_utils._text import to_bytes

    args = json.dumps({'ANSIBLE_MODULE_ARGS': args})
    basic._ANSIBLE_ARGS = to_bytes(args)


@pytest.fixture(scope="session", autouse=True)
def prepare_python_environment():
    import sys
    sys.path.append("./plugins/modules")
    sys.path.append("./plugins/module_utils")


@pytest.fixture(scope="function", autouse=True)
def mock_ansible(mocker):
    from ansible.module_utils import basic
    mocker.patch.multiple(basic.AnsibleModule, exit_json=exit_json, fail_json=fail_json, get_bin_path=get_bin_path)


@pytest.fixture(scope="function")
def rapi_client():
    from ganeti_rapi_client import GanetiRapiClient

    client = GanetiRapiClient("localhost", username="gnt-cc", password="gnt-cc")
    return client


@pytest.fixture(scope="function")
def module_args():
    return {
        'user': 'gnt-cc',
        'password': 'gnt-cc',
        'name': 'homer'
    }