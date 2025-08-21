# Ansible modules for Ganeti

This is a small collection of modules that use the JSON API of Ganetis
RAPI daemon. Use at your own risk!

## Overview

Ganeti comes with a JSON API that is managed by their Remote API (RAPI)
daemon. By default RAPI listens on "localhost" on the manager node and
uses a self-signed certificate, but can be configured to listen to other
addresses and use a proper certificate. Configuring this is outside of
this projects scope.

The API is documented [here](http://docs.ganeti.org/ganeti/2.16/html/rapi.html).

## Dependencies / expected environment

The modules are developed against version **3.0** and **3.1** of Ganeti and thus
RAPI, running on a Debian Bullseye, Bookworm, Trixie (11, 12, 13) hosts. The Python interpreter is
assumed to be Python 3.7. While the
code does not use features introduced after Python 3.5, no care is taken
to remain backwards compatible with earlier Python versions, especially
not **2.x**. It is also tested to work on Ansible **2.17**.

## Build and install

```
ansible-galaxy collection build
ansible-galaxy collection install sipgate-ganeti-$version.tar.gz --force
```

## Validate module

```
cd /$HOME/.ansible/collections/ansible_collections/sipgate/ganeti
ansible-test sanity --test validate-modules
```

### GanetiRapiClient
This module depends on the official [GanetiRapiClient](https://github.com/ganeti/ganeti/tree/master/lib/rapi) for python. Therefore it needs to be present for the python interpreter on the machine running ansible. The easiest way is to copy the GanetiRapiClient in a `module_utils` directory parallel to your library directory (see [Ansible Documentation](https://docs.ansible.com/ansible/latest/dev_guide/developing_module_utilities.html#using-and-developing-module-utilities)).

```
playbooks/
├── library/
│   ├── ganeti_instance.py
├── module_utils/
│   ├── ganeti_rapi_client.py
└── roles/
    ├── ...
```

The GanetiRapiClient itself also has some dependencies which need to be present on the machine running ansible:
* pycurl
* simplejson

## Authentication

The modules connect to RAPI using TLS, setting up the trust store on the
host may be required if you use your own CA or the self-signed
certificate (refer to the **requests** documentation for insights).

RAPI uses a users file to map usernames to both passwords and
permissions. The default location is `/var/lib/ganeti/rapi/users`. Each
line configures one user. Permissions are either read, write, or both.
The password is the concatenation of the username, the fixed string
`:Ganeti Remote API:` and the password. It can be created using the
following jinja2 template, assuming `ganeti_rapi_users` is a hash with
`name`, `password` and `access` keys:

``` {.sourceCode .}
{% for user in ganeti_rapi_users %}
{% set string = user.name ~ ':Ganeti Remote API:' ~ user.password %}
{{ user.name }} {HA1}{{ string | hash('md5') }}{% if user.access %} {{ user.access }}{% endif %}
{% endfor %}
```

## Modules

All modules use the following variables to connect:

-   `user` is the username
-   `password` is the users password, it is protected using
    `no_log=True`
-   `address` is the address on which RAPI listens, and defaults to
    `localhost`
-   `port` is the port at which RAPI listens, defaulting to `5080`

### ganeti\_instance

As the name implies, the module manages instances. It is used to create,
modify, start, stop, migrate and remove instances. Support for import is not present yet.

The module is a fork of
[svalouch/ansible-modules-ganeti](https://github.com/svalouch/ansible-modules-ganeti).
Instead of using requests to access the Rapi directly this module uses
the official [GanetiRapiClient](https://github.com/ganeti/ganeti/tree/master/lib/rapi) python library
. This library
must be present to python (see Section Dependencies).

The module allows to wait for job completion. If `wait` is true, the
module waits for the tasks completion. The amount of time to wait at
most is set using `job_timeout` in seconds, the default is **5
minutes**. If the job does not finish within that time frame, the module
returns an error (usually ending the playbook), but it does not clean
up. This means that an instance could have been successfully created
eventually, and it is up to the user to determin if and what to clean
up. If `wait` is false, the module is in fire-and-forget mode and will
return as soon as the response from RAPI is received.

#### Checks
Ganeti's default checks can be disabled:
* conflicts_check
* ip_check
* name_check

#### state: present

The state is used to create a new instance. It has features an extensive
parameter set, but does not implement **all** of the parameters that
RAPI understands. It performs some validation, for example a list of
possible disk templates and hypervisor choices is coded into it,
representing the state of Ganeti 2.16. Most parameters are optional, but
some like `name` are mandatory. In the end, the configuration and
defaults set on the cluster, node and instance os determin what is
required to create an instance and detecting that is outside the modules
scope.

Complex example, the comments denote the parameter that would normally
go to `gnt-instance create` on the shell:

``` {.sourceCode .yaml}
- name: create test vm
  ganeti_instance:
      user: ansible
      password: "ansible"
      name: testvm
      state: present
      memory: 1024
      # -B vcpus=2
      vcpus: 2
      # -t ext
      disk_template: ext
      disks:
        # --disk 0:size=10G,name=root,provider=zfs
        - size: 10G
          name: root
          provider: zfs
        # --disk 1:size=1G,name=swap,provider=zfs
        - size: 1G
          name: swap
          provider: zfs
        # --disk 2:size=20G,name=srv,provider=zfs
        - size: 20G
          name: srv
          provider: zfs
      # -o debian+default
      os_type: debian+default
      # -O
      osparams:
        # fqdn=testvm.intern
        fqdn: testvm.intern
        # puppet=no
        puppet: 'no'
        # release=buster
        release: buster
        # netmode=manual
        netmode: manual
      nics:
        # --net 0:mode=bridged,name=server,link=br_ext,ip=192.168.90.14
        - mode: bridged
          name: server
          link: br_ext
          ip: 192.168.90.14
        # --net 1:mode=bridged,name=server_int,link=br_int,ip=192.168.80.14
        - mode: bridged
          name: server_int
          link: br_host
          ip: 192.168.80.14
```

The modification of some parameters is also possible:
* Adding and removing of **vCPUs**
* Adding and removing of **Memory**
* Adding **disks** and increasing a disks size
  * Removing or shrinking disks is not supported
* Adding and removing of **NICs**
* Adding and removing tags
* Renaming an instance (only when the instance is stopped)

When modifications to an instance are done no automatic reboot will happen. For most of the changes to become active the instance needs to be shutdown and started again manually.

#### state: absent

The `absent` state is used to remove an instance, akin to
`gnt-instance remove`. Thus, this **can't be undone**. it is not
required to power the instance down beforehand, Ganeti will handle that.
`name` is the only required parameter.

#### state: started

Starts the instance if it is down, and does nothing if it is running.
Same as `gnt-instance start`. `name` is the only required parameter.
Returns an error if the instance does not exist.

#### state: stopped

Shuts the instance down, the same as executing `gnt-instance stop`. A
timeout can't be given (yet) and the only required parameter is `name`.
Does nothing if the instance is not running. Returns an error if the
instance does not exist.

### state: restarted

Restarts the instance, or starts it if it was down. This is analog to
running `gnt-instance restart`. It requires the `name` of the instance.
Returns an error if the instance does not exist.

### state: migrated

Executes a live migration of the instance. The instance needs to be running.

# Development

## Testing

The ansible modules are tested using `pytest` and a docker container containing a ganeti fake cluster (https://github.com/sipgate/ganeti-docker). The tests are fully integrated using Github Actions.

### Run test locally

```
docker run -d -p 5080:5080 --cap-add=NET_ADMIN $docker_image_id
pytest
```