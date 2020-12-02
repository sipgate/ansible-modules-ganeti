#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2020 sipgate GmbH, <bearmetal@sipgate.de>
# Copyright (c) 2020 Stefan Valouch (svalouch), <svalouch@valouch.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# Original by Stefan Valouch (svalouch): BSD 3-Clause License

from __future__ import absolute_import, division, print_function

__metaclass__ = type

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = r'''
---
module: ganeti_instance
short_description: Manage Ganeti instances
description:
  - Manage instances supervised by a Ganeti cluster
  - Instances can be started, stopped and restarted, migrated, modified
  - Allows semi-complex creation of instances
author: sipgate GmbH (bearmetal@sipgate.de), Stefan Valouch (@svalouch)
requirements:
  - "python >= 3.5"
  - "ganeti >= 2.15"
  - GanetiRapiClient
options:
    address:
        description:
          - Address the RAPI listens to
        required: false
        default: localhost
        type: str
    port:
        description:
          - RAPI port
        required: false
        default: 5080
        type: int
    user:
        description:
          - Name of the user that connects to RAPI
        required: false
        type: str
    password:
        description:
          - Password associated with the user account
        required: false
        type: str
    job_timeout:
        description:
          - If I(wait=true), specifies the maximum amount of time in
            seconds to wait for the job to finish before moving on
        required: false
        type: int
        default: 300
    state:
        description:
          - Desired state of the instance.
          - States except I(state=absent) and I(state=present) report an error if the
            instance does not exist.
          - To create or modify an instance use I(state=present).
          - To delete an instance use I(state=absent). The instance must be shutdown to be deleted.
          - To stop an instance use I(state=stopped).
          - To start an instance use I(state=started).
          - To restart an instance use I(state=restarted).
          - To migrate an instance use I(state=migrated).
        required: true
        choices:
          - absent
          - present
          - restarted
          - started
          - stopped
          - migrated
        default: 'present'
        type: str
    wait:
        description:
          - If I(wait=true), waits for the job that gets submitted to ganeti by
            the module.
          - The module waits for I(job_timeout) seconds before reporting an
            error.
          - If I(wait=false) the module submits the job and returns immediately
            instead of waiting for ganeti to finish the job. There is no way
            for the module to detect if the job results in an error.
        required: false
        type: bool
        default: true
    disk_template:
        description:
          - If I(state=present), specifies the disk template to use.
          - If I(disk_template=ext) is specified, the provider needs to be specified in
            the I(disks) structure.
          - Templates not enabled on the cluster will result in an error.
        type: str
        choices:
          - sharedfile
          - diskless
          - plain
          - gluster
          - blockdev
          - drbd
          - ext
          - file
          - rbd
        default: plain
    disks:
        description:
          - Specifies the disks and their options in a list.
        type: list
        suboptions:
            size:
                description:
                  - Size of the disk in megabytes
                type: int
                required: true
            mode:
                description:
                  - Disk access mode, such as "rw"
                type: str
            name:
                description:
                  - Name of the disk
                  - This is optional for some templates/providers, but may be
                    used by the os creation script.
                type: str
            provider:
                description:
                  - The extstorage provider, required if I(disk_template=ext).
                type: str
    nics:
        description:
          - Specifies the network interfaces for the instance.
          - The mode defines which of the suboptions are required, refer
            to the Ganeti documentation in instance creation.
        type: list
        suboptions:
            bridge:
                description:
                  - The name of the bridge to use
                  - Used with mode set to bridged
                type: str
            name:
                description:
                  - Name of the network interface.
                  - This is optional but may be used by the os creation script
                    and helps when working with gnt-instance.
                type: str
            ip:
                description:
                  - IP that should be assigned to the interface.
                  - This may be used by os creation scripts or drivers, and is
                    usually optional.
                type: str
            vlan:
                description:
                  - VLAN ID to use
                  - Optional
                type: int
            mac:
                description:
                  - Overwrite the MAC of this interface
                  - Optional, by default the cluster-wide MAC-prefix is used
                    to compute a unique MAC address
            link:
                description:
                  - Interface on the host this virtual interface is connected to.
                  - "Example: Specify the name of the bridge to connect the tap device to."
                type: str
            mode:
                description:
                  - Operation mode.
                type: str
                choices:
                  - routed
                  - bridged
                  - openvswitch
                required: true
            network:
                description:
                  - Network this interface is connected to
                type: str
    hypervisor:
        description:
          - Overwrite the default hypervisor setting set in the cluster.
          - Only enabled hypervisors can be chosen, specifying a disabled one
            results in an error.
        type: str
        choices:
          - chroot
          - xen-pvm
          - kvm
          - xen-hvm
          - lxc
          - fake
        default: kvm
    iallocator:
        description:
          - IAllocator to use
        type: str
        default: hail
    name:
        description:
          - Name of the instance
        required: true
        type: str
        aliases:
          - instance_name
    new_name:
        description:
          - "When this parameter is present, the instance will be renamed to this value. Note: The VM needs to be stopped."
        required: false
        type: str
    os_type:
        description:
          - Name of the OS create script and variant to deploy
          - The availability depends on the cluster setup
        type: str
    osparams:
        description:
          - Optional parameters that are passed to the os create script.
          - Specify flat key:value pairs
        type: dict
    pnode:
        description:
          - Name or address of the primary node
          - If not given, the node running RAPI will be used
        type: str
    snode:
        description:
          - Name or address of the optional secondary node.
          - If set, I(pnode) has to be set.
        type: str
    memory:
        description:
          - Amount of memory in megabytes to allocate to the instance
        type: int
    vcpus:
        description:
          - Number of vCPUs to give to the instance
          - If not given, the clusters defaults are used.
        type: int
    conflicts_check:
        description:
          - Whether to check for conflicting IP addresses
        type: bool
        default: True
    ip_check:
        description:
          - Whether to ensure instance’s IP address is inactive
        type: bool
        default: True
    name_check:
        description:
          - Whether to check name
        type: bool
        default: True
    no_install:
        description:
          - Do not install the OS (will disable automatic start)
        type: bool
    wait_for_sync:
        description:
          - Whether to wait for the disk to synchronize
        type: bool
        default: True
    tags:
        description:
          - Instance tags
        type: list
        default: []
    group_name:
        description:
          - Optional group name
        type: str
'''

EXAMPLES = r'''
---
- name: start instance
  ganeti_instance:
      user: ansible
      password: supersecret
      name: vmname
      state: started

- name: stop instance
  ganeti_instance:
      user: operator
      password: operator
      name: vmname
      state: stopped

- name: restart instance
  ganeti_instance:
      user: root
      password: toor
      name: vmname
      state: restarted

- name: create a new instance
  ganeti_instance:
      address: ganeti.example.com
      user: admin
      password: bofh
      name: vmname
      state: present
      memory: 512
      vcpus: 1
      disk_template: plain
      disks:
        - name: root
          size: 10G
      nics:
        - mode: bridged
          link: br0
      os_type: debian+default
'''

RETURN = r'''
changed:
    description: Whether the the module performed a change related to the instance.
    returned: always
    type: bool
message:
    description: Optional message returned as a result of an action.
    returned: always
    type: str
    sample: Instance created
reboot_required:
    description: Optional return value used when instances are modified. When it is set to true, a restart of the qemu process is necessary.
    returned: always
    type: bool
changed_parameters:
    description: If a instance is modified this contains all changed parameters. Currently only supported for growed disks.
    returned: always
    type: dict
'''

from ansible.module_utils.basic import AnsibleModule

try:
    from ansible_collections.sipgate.ganeti.plugins.module_utils.ganeti_rapi_client import GanetiRapiClient, GanetiApiError
except:
    from ganeti_rapi_client import GanetiRapiClient, GanetiApiError

client: GanetiRapiClient = None


def wait_for_job_to_complete(module, job_id, action: str):
    if module.params['wait']:
        success = client.WaitForJobCompletion(job_id, period=1, retries=module.params["job_timeout"])
        if not success:
            module.fail_json(name=module.params['name'],
                             msg='{0} action failed with job_id: {1}'.format(action, job_id))
        else:
            return (True, '{0} complete'.format(action))
    else:
        return (True, '{0} signal sent'.format(action))


def instance_create(module):
    params = {
        '__version__': 1,
        'beparams': {
            'memory': module.params['memory'],
            'minmem': module.params['memory'],
            'maxmem': module.params['memory'],
            'vcpus': module.params['vcpus'],
        },
        'disk_template': module.params['disk_template'],
        'hypervisor': module.params['hypervisor'],
        'iallocator': module.params['iallocator'],
        'name': module.params['name'],
        'os_type': module.params['os_type'] if module.params['os_type'] is not None else 'debootstrap+default',
        'pnode': module.params['pnode'],
        'snode': module.params['snode'],
        'mode': 'create',
        'conflicts_check': module.params['conflicts_check'],
        'ip_check': module.params['ip_check'],
        'name_check': module.params['name_check'],
        'no_install': module.params['no_install'],
        'wait_for_sync': module.params['wait_for_sync'],
        'tags': module.params['tags'],
        'group_name': module.params['group_name']
    }

    # disks
    disks = _assemble_disks_for_rapi(module)
    params['disks'] = disks

    # nics
    nics = _assemble_nics_for_rapi(module)
    params['nics'] = nics

    # osparams
    if len(module.params['osparams']) > 0:
        osparams = dict()
        for k, v in module.params['osparams'].items():
            if isinstance(v, dict) or isinstance(v, list):
                module.fail_json(name=module.params['name'], msg='Got complex type for osparams key %s' % k)
            osparams[k] = v
        if len(osparams) > 0:
            params['osparams'] = osparams

    job_id = client.CreateInstance(**params)
    return wait_for_job_to_complete(module, job_id, "create")


def _assemble_disks_for_rapi(module):
    disks = []

    if not module.params['disks']:
        return []

    disk_i = 0
    for disk in module.params['disks']:
        disk_params = _assemble_disk_params_for_rapi(module, disk)

        if len(disk_params) != 0:
            disks.append(disk_params)
            disk_i += 1

    return disks


def _assemble_disk_params_for_rapi(module, disk):
    DISK_PARAMETERS = ['size', 'mode', 'name', 'provider']
    disk_params = dict()

    if 'size' not in disk.keys():
        module.fail_json(name=module.params['name'], msg='No "size" given for disk')
    elif 'provider' in disk.keys() and disk['provider'] == 'ext':
        # things outside DISK_PARAMETERS are now appended as kwargs
        for key in disk.keys():
            disk_params[key] = disk[key]
    else:
        for key in disk.keys():
            if key in DISK_PARAMETERS:
                disk_params[key] = disk[key]
            else:
                module.fail_json(name=module.params['name'],
                                 msg='Invalid disk parameter for disk: {0} is not a valid key'.format(key))

    return disk_params


def _assemble_nics_for_rapi(module):
    nics = []
    nic_i = 0

    if not module.params['nics']:
        return []

    for nic in module.params['nics']:
        nic_params = _assemble_nic_params_for_rapi(module, nic)

        if len(nic_params) != 0:
            nics.append(nic_params)
            nic_i += 1

    return nics


def _assemble_nic_params_for_rapi(module, nic):
    nic_params = dict()
    for key in nic.keys():
        if key not in ['bridge', 'name', 'ip', 'vlan', 'mac', 'link', 'mode', 'network']:
            module.fail_json(name=module.params['name'],
                             msg='Invalid nic parameter for nic: {0} is not a valid key'.format(key))
        else:
            if key == 'mode' and nic[key] not in ['routed', 'bridged', 'openvswitch']:
                module.fail_json(name=module.params['name'],
                                 msg='Invalid mode for nic {0}'.format(nic[key]))
                return
            nic_params[key] = nic[key]

    return nic_params


def instance_start(module):
    job_id = client.StartupInstance(module.params["name"])
    return wait_for_job_to_complete(module, job_id, "startup")


def instance_stop(module):
    job_id = client.ShutdownInstance(module.params["name"])
    return wait_for_job_to_complete(module, job_id, "shutdown")


def instance_destroy(module):
    job_id = client.DeleteInstance(module.params["name"])
    return wait_for_job_to_complete(module, job_id, "delete")


def instance_restart(module):
    job_id = client.RebootInstance(module.params["name"])
    return wait_for_job_to_complete(module, job_id, "restart")


def instance_migrate(module):
    job_id = client.MigrateInstance(module.params["name"])
    return wait_for_job_to_complete(module, job_id, "migrate")


def instance_rename(module):
    job_id = client.RenameInstance(module.params["name"], module.params["new_name"], module.params['ip_check'],
                                   module.params['name_check'])
    return wait_for_job_to_complete(module, job_id, "rename")


def instance_modify(module):
    changed = False
    params_changed = False
    reboot_required = False
    message = ''
    changed_parameters = {}

    params = {
        'beparams': {},
        'conflicts_check': module.params['conflicts_check'],
        'wait_for_sync': module.params['wait_for_sync']
    }

    current_instance_parameters = client.GetInstance(module.params["name"])

    # NICs
    changed_nics, nics = _modify_instance_assemble_nics(module, current_instance_parameters)
    if changed_nics:
        changed = params_changed = True
        params["nics"] = nics

    # VCPUs
    if module.params["vcpus"] != current_instance_parameters["beparams"]["vcpus"]:
        changed = params_changed = True
        reboot_required = True
        params["beparams"]["vcpus"] = module.params["vcpus"]

    # MEMORY
    if int(module.params["memory"]) != int(current_instance_parameters["beparams"]["maxmem"]):
        changed = params_changed = True
        reboot_required = True
        params["beparams"]['memory'] = module.params['memory']
        params["beparams"]['minmem'] = module.params['memory']
        params["beparams"]['maxmem'] = module.params['memory']

    # DISKs
    changed_disks, disks, disks_growed = _modify_instance_assemble_disks(module, current_instance_parameters)
    if changed_disks:
        changed = True
        if len(disks_growed) > 0:
            changed_parameters["disks_growed"] = disks_growed
        if len(disks) > 0:
            params_changed = True
            params["disks"] = disks

    # NODE GROUP
    if module.params["group_name"] and module.params["group_name"] != find_host_group_for_host(module):
        module.fail_json(name=module.params['name'],
                         msg='''Modifying the hardware node group is not supported by the ganeti RAPI.
                         Please run this command yourself and then rerun this playbook:
                         gnt-instance change-group --to={0} {1}'''.format(module.params["group_name"],
                                                                          module.params['name']))

    # TAGS
    changed = _modify_instance_tags(module, current_instance_parameters) or changed

    if params_changed:
        job_id = client.ModifyInstance(instance=module.params['name'], **params)
        changed, message = wait_for_job_to_complete(module, job_id, "modify")

    if not changed:
        message = "Instance not modified."

    return changed, changed_parameters, reboot_required, message


def _modify_instance_tags(module, current_instance_parameters):
    changed = False

    wanted_tags = module.params["tags"] or []
    current_tags = current_instance_parameters["tags"]
    tags_to_delete = list(set(current_tags) - set(wanted_tags))
    tags_to_add = list(set(wanted_tags) - set(current_tags))
    if len(tags_to_add) > 0:
        changed = True
        job_id = client.AddInstanceTags(module.params["name"], tags_to_add)
        success = client.WaitForJobCompletion(job_id, period=1, retries=30)
        if not success:
            module.fail_json(name=module.params['name'],
                             msg='Adding tags for instance {0} with job_id {1} failed.'.format(module.params["name"],
                                                                                               job_id))
    if len(tags_to_delete) > 0:
        changed = True
        job_id = client.DeleteInstanceTags(module.params["name"], tags_to_delete)
        success = client.WaitForJobCompletion(job_id, period=1, retries=30)
        if not success:
            module.fail_json(name=module.params['name'],
                             msg='Deleting tags for instance {0} with job_id {1} failed.'.format(module.params["name"],
                                                                                                 job_id))
    return changed


def find_host_group_for_host(module):
    primary_node = client.GetInstance(module.params['name'])["pnode"]
    for group in client.GetGroups():
        if primary_node in client.GetGroup(group)["node_list"]:
            return group


def _modify_instance_assemble_nics(module, current_instance_parameters):
    nics = []
    changed = False

    current_nics = current_instance_parameters["custom_nicparams"]
    for i, nic in enumerate(module.params["nics"]):
        nic_params_from_ansible = _assemble_nic_params_for_rapi(module, nic)

        if i + 1 > len(current_nics):
            changed = True
            nics.append(("add", i, nic_params_from_ansible))
        else:
            new_nic_params = {}
            for key, value in nic_params_from_ansible.items():
                if key == "mac" and value == "generate":
                    continue
                elif key not in current_nics[i] or current_nics[i][key] != value:
                    new_nic_params[key] = value

            if len(new_nic_params) > 0:
                changed = True
                nics.append(("modify", i, new_nic_params))

    number_of_nics_to_delete = len(current_nics) - len(module.params["nics"])
    if number_of_nics_to_delete == 1:
        changed = True
        for nic in current_nics[-number_of_nics_to_delete:]:
            index = current_nics.index(nic)
            nics.append(("remove", index, {}))
    elif number_of_nics_to_delete > 1:
        module.fail_json(name=module.params['name'], msg='Ganeti is not able to remove more than 1 NIC at a time.')

    return changed, nics


def _modify_instance_assemble_disks(module, current_instance_parameters):
    disks = []
    disks_growed = []
    changed = False

    current_disk_sizes = current_instance_parameters["disk.sizes"]
    wanted_disks = module.params["disks"]

    if len(module.params["disks"]) < len(current_instance_parameters["disk.sizes"]):
        module.fail_json(name=module.params['name'], msg='Removing disks is not implemented.')

    for index, wanted_disk in enumerate(wanted_disks):
        if index + 1 > len(current_disk_sizes):
            changed = True
            new_disk_params = _assemble_disk_params_for_rapi(module, wanted_disk)
            disks.append(("add", index, new_disk_params))
        elif wanted_disk["size"] == current_disk_sizes[index]:
            continue
        elif wanted_disk["size"] > current_disk_sizes[index]:
            changed = True

            size_to_grow_mb = wanted_disk["size"] - current_disk_sizes[index]

            params = {
                "absolute": True,
                "amount": wanted_disk["size"]
            }

            job_id = client.GrowInstanceDisk(module.params["name"], index, size_to_grow_mb, wait_for_sync=True)
            wait_for_job_to_complete(module, job_id, "disk grow")
            disks_growed.append(index)
        else:
            module.fail_json(name=module.params['name'], msg='Reducing a disks size is not supported.')

    return changed, disks, disks_growed


def main():
    # list of possible values for disk_template, taken from rapi docs v2.16
    disk_templates = ['sharedfile', 'diskless', 'plain', 'gluster', 'blockdev',
                      'drbd', 'ext', 'file', 'rbd']
    hypervisor_choices = ['chroot', 'xen-pvm', 'kvm', 'xen-hvm', 'lxc', 'fake']
    state_choices = ['present', 'absent', 'restarted', 'started', 'stopped', 'migrated']

    module_args = dict(
        address=dict(type='str', default='localhost'),
        port=dict(type='int', required=False, default=5080),
        user=dict(type='str', required=False, default=None),
        password=dict(type='str', required=False, default=None, no_log=True),
        job_timeout=dict(type='int', required=False, default=5 * 60),
        state=dict(type='str', default='present', choices=state_choices),
        wait=dict(type='bool', default=True),  # wait for job completion

        # parameters for vm creation / modification
        disk_template=dict(type='str', default='plain', choices=disk_templates),
        disks=dict(type='list', required=False),
        hypervisor=dict(type='str', default='kvm', choices=hypervisor_choices),
        iallocator=dict(type='str', required=False, default='hail'),
        name=dict(type='str', required=True, aliases=['instance_name']),
        new_name=dict(type='str', required=False),
        nics=dict(type='list', required=False),
        os_type=dict(type='str', required=False),
        osparams=dict(type='dict', required=False),
        pnode=dict(type='str', required=False, default=None),
        snode=dict(type='str', required=False, default=None),

        # beparams
        memory=dict(type='int', required=False),
        vcpus=dict(type='int', required=False),

        conflicts_check=dict(type='bool', required=False, default=True),
        ip_check=dict(type='bool', required=False, default=True),
        name_check=dict(type='bool', required=False, default=True),
        no_install=dict(type='bool', required=False, default=None),
        wait_for_sync=dict(type='bool', required=False, default=True),

        tags=dict(type='list', required=False, default=[]),
        group_name=dict(type='str', required=False, default=None),
    )

    changed = False
    reboot_required = False
    message = ''
    changed_parameters = {}

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
    )

    global client
    client = GanetiRapiClient(module.params['address'], username=module.params['user'],
                              password=module.params['password'])

    try:
        instance = client.GetInstance(module.params["name"])
    except GanetiApiError as e:
        instance = None
        if "Cloud not resolve host" in str(e):
            module.fail_json(message='Could not resolve ganeti master {0}'.format(module.params['address']))
        elif "404 Not Found: Nothing matches the given URI" in str(e):
            instance = None
        else:
            module.fail_json(message=str(e))

    if not instance:
        if module.params['state'] == 'present':
            changed, message = instance_create(module)
        elif module.params['state'] in ('restarted', 'started', 'stopped', 'migrated'):
            module.fail_json(message='Instance {0} is not present, can\'t set to {1}'.format(module.params['name'],
                                                                                             module.params['state']))
        else:
            message = 'No instance found'
    else:
        if module.params['new_name']:
            if instance['status'] in ('ADMIN_down', 'ERROR_down'):
                changed, message = instance_rename(module)
            else:
                message = 'Instance needs to be halted to be renamed, status {0}'.format(instance['status'])
        elif module.params['state'] == 'present':
            changed, changed_parameters, reboot_required, message = instance_modify(module)
        elif module.params['state'] == 'stopped':
            if instance['status'] not in ('ADMIN_down', 'ERROR_down'):
                changed, message = instance_stop(module)
            else:
                message = 'Instance already stopped, status {0}'.format(instance['status'])
        elif module.params['state'] == 'started':
            if instance['status'] != 'running':
                changed, message = instance_start(module)
        elif module.params['state'] == 'restarted':
            if instance['status'] == 'running':
                changed, message = instance_restart(module)
            else:
                changed = instance_start(module)
        elif module.params['state'] == 'migrated':
            if instance['status'] == 'running':
                changed, message = instance_migrate(module)
        elif module.params['state'] == 'absent':
            changed, message = instance_destroy(module)

    result = dict(
        changed=changed,
        message=message,
        reboot_required=reboot_required,
        changed_parameters=changed_parameters,
    )

    module.exit_json(**result)


if __name__ == '__main__':
    main()
