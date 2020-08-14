
def set_module_args(args):
    import json
    from ansible.module_utils import basic
    from ansible.module_utils._text import to_bytes

    args = json.dumps({'ANSIBLE_MODULE_ARGS': args})
    basic._ANSIBLE_ARGS = to_bytes(args)

def test_dummy():
    assert True

def test_import_module_works():
    import ganeti_instance

def test_dummy_instance_is_present():
    import ganeti_instance

    set_module_args({
        'user': 'gnt-cc',
        'gnt-cc': 'gnt-cc',
        'name': 'homer',
        'state': 'started'
    })

    ganeti_instance.main()