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


def test_dummy_instance_can_be_created(module_args, rapi_client):
    import ganeti_instance

    memory = 1024
    disk_template = "diskless"
    vcpus = 2

    set_module_args({
        **module_args,
        "name": "new_instance",
        "state": "present",
        "ip_check": False,
        "name_check": "False",
        "no_install": "True",
        "hypervisor": "fake",
        "vcpus": str(vcpus),
        "memory": str(memory),
        "disk_template": disk_template,
        "disks": [
            {
                "size": 1000
            }
        ],
        "osparams": {}
    })

    with raises(AnsibleExitJson) as result:
        ganeti_instance.main()

    assert (result.value.args[0]['changed'] is True)
    assert (result.value.args[0]['reboot_required'] is False)
    assert (result.value.args[0]['message'] == "create complete")
    assert (rapi_client.GetInstance("new_instance")["status"] == "ADMIN_down")
    assert (rapi_client.GetInstance("new_instance")["disk_template"] == disk_template)
    assert (rapi_client.GetInstance("new_instance")["beparams"]["vcpus"] == vcpus)
    assert (rapi_client.GetInstance("new_instance")["beparams"]["memory"] == memory)
    assert (rapi_client.GetInstance("new_instance")["beparams"]["minmem"] == memory)
    assert (rapi_client.GetInstance("new_instance")["beparams"]["maxmem"] == memory)
