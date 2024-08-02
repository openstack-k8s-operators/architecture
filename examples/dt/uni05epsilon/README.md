# Deployment Topology – Epsilon

This document contains a list of integration test suites that would be
executed against the below specified topology of Red Hat OpenStack Services
on OpenShift. It also contains a collection of custom resources (CRs) for
deploying the test environment.


## Purpose

Focused on verifying Cinder and Glance with multiple backends.


## Environment


### Nodes

| Role              | Machine Type | Count |
| ----------------- | ------------ | ----- |
| Compact OpenShift | vm           |   3   |
| OpenStack Compute | vm           |   3   |


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
| octavia     | VLAN tagged | 172.23.0.0/24     |
| storage     | VLAN tagged | 172.18.0.0/24     |
| storagemgmt | VLAN tagged | 172.20.0.0/24     |
| tenant      | VLAN tagged | 172.19.0.0/24     |


### Services, enabled features and configurations

| Service          | configuration           | Lock-in coverage?  |
| ---------------- | ----------------------- | ------------------ |
| Barbican         | (default)               | Must have          |
| Cinder           | iSCSI/netapp, NFS, Ceph | Must have          |
| Cinder Backup    | Swift                   | Must have          |
| Glance           | cinder/NFS, Ceph, swift | Must have          |
| Horizon          | N/A                     | Must have          |
| Neutron          | Geneve (OVN)            | Must have          |
| Octavia (TODO)   | act-stby                | Must have          |
| Swift            | (default)               | Must have          |


#### Support services

The following table lists services which are not the main focus of the testing
(which may be covered by additional scenarios), but are required for the DT
to work properly and can be deployed with any/default configuration.

| Service          | Reason                     |
| ---------------- |--------------------------- |
| Nova             | needed by scenario testing |
| Keystone         | needed by all services     |


### Additional configuration

- iSCSI service is enabled on all OpenShift nodes.
- Multipath service is enabled on all OpenShift nodes.


#### iSCSI

It is assumed *iSCSI* services are enabled in all nodes participating in the
Red Hat OpenShift cluster. If not, a `MachineConfig` similar to the below one
is applied. The node would be *rebooted* after applying the configuration.

```YAML
---
apiVersion: machineconfiguration.openshift.io/v1
kind: MachineConfig
metadata:
  labels:
    machineconfiguration.openshift.io/role: master
    service: cinder
  name: 99-master-cinder-enable-iscsid
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


## Workflow

1. [Install the OpenStack K8S operators and their dependencies](../../common/README.md).
2. [Configure networking and deploy the OpenStack control plane](control-plane.md).
3. [Configure and deploy the initial data plane to prepare for Ceph installation](dataplane-pre-ceph.md).
4. Install Ceph on the compute nodes.
5. [Update the control plane and finish deploying the data plane after Ceph has been installed](dataplane-post-ceph.md).

Note: OpenStack K8S CRDs do not provide a way to install Ceph via any sort
of CRs combination. This step needs to be handled separately.
