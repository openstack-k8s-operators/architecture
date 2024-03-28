# Deployed Topology - Alpha

This document contains a list of integration test suites that would be
executed against the below specified topology of Red Hat OpenStack Services
on OpenShift. It also contains a collection of custom resources (CRs) for
deploying the test environment.

## Purpose

This topology is used for executing integration tests that evaluate the
`default` backends of the below mentioned services.

## Environment

### Nodes

| Role | Machine Type | Count |
| ---- | ------------ | ----- |
| Compact OpenShift | vm | 3 |
| OpenStack Compute | vm | 2 |
| Networker         | vm | 3 |
| Test nodes        | vm | 2 |

### Networks

| Name | Type | Interface |
| ---- | ---- | --------- |
| Provisioning | untagged | nic1 |
| Machine | untagged | nic2 |
| RH OSP | trunk | nic3 |

#### Networks in RH OSP

| Name | Type |
| ---- | ---- |
| ctlplane | untagged |
| internalapi | VLAN tagged |
| Storage | VLAN tagged |
| Tenant | VLAN tagged |

### Services, enabled features and configurations

| Service          | configuration    | Lock-in coverage?  |
| ---------------- | ---------------- | ------------------ |
| Cinder           | LVM/iSCSI/lioadm | Must have          |
| Cinder Backup    | Swift            | Must have          |
| Glance           | Swift            | Must have          |
| Swift            | (default)        | Must have          |
| Octavia          | (amphora)        | Must have          |
| Horizon          | N/A              | Must have          |
| Barbican         | (default)        | Must have          |
| Telemetry        |                  | Must have          |
| Ironic           |                  | Must have          |
| Neutron          | OVN - AZs        | Must have          |

#### Support services

The following table lists services which are not the main focus of the testing
(which may be covered by additional scenarios), but are required for the DT to
work properly and can be deployed with any/default configuration.

| Service          | Reason            |
| ---------------- |------------------ |
| Nova             | needed by scenario testing |
| Keystone         | needed by all services     |

### Additional configuration

- Always-on, default services and features: TLSe
- Two additional fake baremetal nodes
- Availability zones for OVN (zone-1 & zone-2)
- Logical volume with the name cinder-volumes exists on a OpenShift node.
- iSCSI service is enabled on all OpenShift nodes.
- Multipath service is enabled on all OpenShift nodes.

#### iSCSI

It is assumed *iSCSI* services are enabled in all nodes participating in the
Red Hat OpenShift cluster. If not, a `MachineConfig` similar to the below one
is applied. The node needs to be *rebooted* after applying the configuration.

```YAML
---
apiVersion: machineconfiguration.openshift.io/v1
kind: MachineConfig
metadata:
  labels:
    machineconfiguration.openshift.io/role: master
    service: cinder
  name: 90-master-cinder-enable-iscsid
spec:
  config:
    ignition:
      version: 3.2.0
    systemd:
      units:
        - enabled: true
          name: iscsid.service
```

#### Multipath

It is assumed *multipath* services are enabled in all nodes particpating in the
Red Hat OpenShift cluster. If not, a `MachineConfig` like the one below must be
applied. The node requires a *reboot* for the changes to be applied.

```YAML
---
apiVersion: machineconfiguration.openshift.io/v1
kind: MachineConfig
metadata:
  labels:
    machineconfiguration.openshift.io/role: master
    service: cinder
  name: 91-master-cinder-enable-multipathd
spec:
  config:
    ignition:
      version: 3.2.0
    storage:
      files:
        - path: /etc/multipath.conf
          overwrite: false
          # Mode must be decimal, this is 0600
          mode: 384
          user:
            name: root
          group:
            name: root
          contents:
            # Source can be a http, https, tftp, s3, gs, or data as defined in rfc2397.
            # This is the rfc2397 text/plain string format
            source: data:,defaults%20%7B%0A%20%20user_friendly_names%20no%0A%20%20recheck_wwid%20yes%0A%20%20skip_kpartx%20yes%0A%20%20find_multipaths%20yes%0A%7D%0A%0Ablacklist%20%7B%0A%7D
    systemd:
      units:
      - enabled: true
        name: multipathd.service
```

The plain text contents of the multipath configuration file is

```conf
defaults {
  user_friendly_names    no
  recheck_wwid    yes
  skip_kpartx    yes
  find_multipaths  yes
}
blacklist {
}
```

#### Cinder backend - LVM

It is assumed that worker nodes or the master nodes have extra disks and there
exists a logical volume with the name *cinder_volumes*. If not, a
`MachineConfig` like the one below must be applied.

```YAML
---
apiVersion: machineconfiguration.openshift.io/v1
kind: MachineConfig
metadata:
  name: 92-create-logical-volume
  labels:
    machineconfiguration.openshift.io/role: master
    service: cinder
spec:
  config:
    ignition:
      version: 3.2.0
    storage:
      disks:
        - device: "/dev/sdb"
          wipeTable: true
        - device: "/dev/sdc"
          wipeTable: true
      files:
        - path: /usr/local/bin/lv-cinder-volumes.sh
          overwrite: false
          mode: 493
          user:
            name: root
          group:
            name: root
          contents:
            source: data:text/plain;charset=utf-8;base64,{{ _replaced_ }}
    systemd:
      units:
        - name: lv-cinder-volumes.service
          enabled: true
          contents: |
            [Unit]
            Description=Create logical volume with name cinder-volumes.
            After=var.mount systemd-udev-settle.service

            [Service]
            Type=oneshot
            ExecStart=/usr/local/bin/lv-cinder-volumes.sh
            RemainAfterExit=yes

            [Install]
            WantedBy=multi-user.target
```

*{{ _replaced_ }}* should be replaced with the base64 encoding of the below script.

```bash
#! /usr/bin/bash
set -euo pipefail

if [[ $(lvdisplay /dev/cinder_volumes_vg/cinder-volumes) ]]; then
    echo "cinder-volumes vg exists."
    exit 0
fi

disks=$(lsblk -o NAME,TYPE | awk '{ if ($2 == "disk" && $1 != "sda") print "/dev/"$1}')
disk_str=''

for disk in ${disks}; do
    pvcreate ${disk}
    disk_str="${disk_str} ${disk}"
done

vgcreate cinder_volumes_vg ${disk_str}
lvcreate -l 100%FREE -n cinder-volumes cinder_volumes_vg
```

##### Notes

The LVM backend for Cinder is a special case as the storage data is on the
OpenShift node and has no external storage systems. This has several
implications

- To prevent issues with exported volumes, cinder-operator automatically uses
  the host network. The backend is configured to use the host's VLAN IP
  address. This means that the cinder-volume service doesn't need any
  networkAttachments.
- There can only be one node with the label `openstack.org/cinder-lvm=`. Apply
  the label using the command
  `oc label node <nodename> openstack.org/cinder-lvm=`


## Testing

| Test framework   | When to run          | Special configuration |
| ---------------- | -------------------- | ----------------------|
| relevant volume tests | tempest stage |           |
| relevant image tests  | tempest stage |           |
| relevant object-storage tests  | tempest stage |           |
| relevant octavia tests | tempest stage |           |
| horizon integration   | own stage (post-tempest)|           |

## Workflow

1. [Install the OpenStack K8S operators and their dependencies](../../common/README.md)
2. [Configure and deploy the OpenStack control plane](control-plane.md)
3. [Configure and deploy the OpenStack networker deployment](networker.md)
4. [Configure and deploy the OpenStack data plane](data-plane.md)
