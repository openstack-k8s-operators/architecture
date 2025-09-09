# Deployed Topology - Iota

This document contains a list of integration test suites that would be
executed against the below specified topology of Red Hat OpenStack Services
on OpenShift. It also contains a collection of custom resources (CRs) for
deploying the test environment.

## Purpose

This topology is used for executing integration tests that primarly
evaluate the FC backend for cinder-volume and glance over cinder.

## Environment

### Nodes

| Role              | Machine Type | Count |
| ----------------- | ------------ | ----- |
| Compact OpenShift | vm           | 3     |
| OpenStack Compute | vm           | 2     |

All the nodes where OpenStack controller runs and all
the OpenStack Compute needs to be configured with a dedicated
HBA interface.

### Networks

| Name         | Type     | Interface | CIDR            |
| ------------ | -------- | --------- | --------------- |
| Provisioning | untagged | nic1      | 172.22.0.0/24   |
| Machine      | untagged | nic2      | 192.168.32.0/20 |
| RH OSP       | trunk    | nic3      |                 |

#### VLAN networks in RH OSP

| Name        | Type        | CIDR              |
| ----------- | ----------- | ----------------- |
| ctlplane    | untagged    | 192.168.122.0/24  |
| internalapi | VLAN tagged | 172.17.0.0/24     |
| storage     | VLAN tagged | 172.18.0.0/24     |
| tenant      | VLAN tagged | 172.19.0.0/24     |

### Services, enabled features and configurations

| Service          | configuration            | Lock-in coverage?  |
| ---------------- | ------------------------ | ------------------ |
| Cinder           | FC (pure)                | Must have          |
| Cinder Backup    | SwiftBackupDriver        | Must have          |
| Glance           | Cinder (FC)              | Must have          |
| Swift            | (default)                | Must have          |
| Horizon          | N/A                      | Must have          |
| Barbican         | (default)                | Must have          |
| Neutron          | Geneve (OVN)             | Must have          |

#### Support services

The following table lists services which are not the main focus of the testing
(which may be covered by additional scenarios), but are required for the DT to
work properly and can be deployed with any/default configuration.

| Service          | Reason                     |
| ---------------- |--------------------------- |
| Nova             | needed by scenario testing |
| Keystone         | needed by all services     |

### Additional configuration

- Multipath service is enabled on all OpenShift nodes.
- The cinder volume container needs to support the 'pure' driver.
- At least master-0 and the compute nodes needs to have access to an HBA
  in order for cinder-backup, cinder-volume and glance to access


#### Multipath

It is assumed *multipath* services are enabled in all nodes particpating in the
Red Hat OpenShift cluster. If not, a `MachineConfig` like the one below must be
applied. The node would be *rebooted* after applying the configuration.

```YAML
---
apiVersion: machineconfiguration.openshift.io/v1
kind: MachineConfig
metadata:
  labels:
    machineconfiguration.openshift.io/role: master
    service: cinder
  name: 99-master-cinder-enable-multipathd
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

#### Cinder volume - container

The container used by the cinder-volume service must support the 'pure'
driver with its dependencies. At this moment, this means having the
[purestorage](https://pypi.org/project/purestorage/) python module.

A way to get the official 'pure' cinder-volume container is described here:
https://pure-storage-openstack-docs.readthedocs.io/en/latest/cinder/configuration/cinder_config_files/section_rhoso180_flasharray_configuration.html

#### Cinder backend - FC protocol

When a Cinder backend which supports the FiberChannel protocol is used,
some pods and machines need to access the HBA (Host Bus Adapter) connected
to the storage.

This means that, on the OpenStack control plane, the following pods need
access to the HBA in this scenario:

- cinder-volume (the one configured for FC)
- cinder-backup
- all glance pods (as it is configured to use cinder)

In addition, nova_compute pods running on data plane nodes need access to
the HBAs too, but let's assume all compute nodes have an HBA.

This means that:
- the replica of the control plane services above needs to match the amount
  of OpenShift nodes with HBA access;
- the OpenShift nodes (schedulable masters) with HBA access needs to be
  identified with a label, for example as `fc_card=available`
  The label can be applied using the command:
  `oc label node <nodename> fc_card=available`

Due to hardware constraints, let's assume that only one of the OpenShift
controllers, specifically master-0, can access an HBA.
This means that all the OpenStack services that require access to an HBA
(cinder-backup, cinder-volume and glance) will be restricted to master-0
only, reducing their replica if needed.
The topology can be easily adapted to the case where all controllers
have access to an HBA by increasing the replica of the aforementioned
services and applying the `fc_card=available` label to all controllers.

## Workflow

1. [Install the OpenStack K8S operators and their dependencies](../../common/README.md)
2. [Configure and deploy the OpenStack control plane](control-plane.md)
3. [Configure and deploy the OpenStack data plane](data-plane.md)
