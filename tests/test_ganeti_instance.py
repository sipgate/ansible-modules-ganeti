from pytest import raises

from conftest import set_module_args, AnsibleExitJson, AnsibleFailJson


def test_import_module_works():
    import ganeti_instance


def test_dummy_instance_can_be_started(module_args, rapi_client):
    import ganeti_instance

    set_module_args({
        **module_args,
        "state": "started"
    })

    with raises(AnsibleExitJson) as result:
        ganeti_instance.main()

    assert (result.value.args[0]['changed'] is True)
    assert (result.value.args[0]['reboot_required'] is False)
    assert (result.value.args[0]['message'] == "startup complete")
    assert (rapi_client.GetInstance("homer")["status"] == "running")


def test_dummy_instance_can_be_stopped(module_args, rapi_client):
    import ganeti_instance

    set_module_args({
        **module_args,
        "state": "stopped"
    })

    with raises(AnsibleExitJson) as result:
        ganeti_instance.main()

    assert (result.value.args[0]['changed'] is True)
    assert (result.value.args[0]['reboot_required'] is False)
    assert (result.value.args[0]['message'] == "shutdown complete")
    assert (rapi_client.GetInstance("homer")["status"] == "ADMIN_down")
