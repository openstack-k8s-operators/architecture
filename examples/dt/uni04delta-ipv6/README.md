# Unified Delta Deployed topology (IPv6)

** This DT is Work-in-Progress **

This document contains a list of integration test suites that would
be executed against the below specified topology of Red Hat OpenStack Services
on OpenShift. It also has a collection of custom resources (CRs).

## Purpose

This topology is used for executing integration tests that evaluate Cinder
and Manila OpenStack services configured with Ceph.

## Environment

### Node

| Role | Machine Type | Count |
| ---- | ------------ | ----- |
| Compact OpenShift | vm | 3 |
| OpenStack Compute | vm | 2 |
| OpenStack EDPM Ceph Nodes | vm | 3 |

### Networks

#### OpenShift and OpenStack Computes

| Name | Type | Interface |
| ---- | ---- | --------- |
| Provisioning | untagged | nic1 |
| Machine | untagged | nic2 |
| RH OSP | trunk | nic3 |

##### Networks in RH OSP

| Name | Type |
| ---- | ---- |
| Ctlplane | untagged |
| Internal-api | VLAN tagged |
| Storage | VLAN tagged |
| Tenant | VLAN tagged |
| StorageManagement | VLAN tagged |
| ironic | untagged |

### Services, enabled features and configurations

| Service          | configuration   | Lock-in coverage?  |
| ---------------- | --------------- | ------------------ |
| Cinder           | Ceph            | Must have          |
| Cinder Backup    | Ceph            | Must have          |
| Glance           | Ceph            | Must have          |
| Manila           | NFS ganesha     | Must have          |
| RGW as Swift     | ---             | Must have          |
| Horizon          | N/A             | Must have          |
| Barbican         |                 | Must have          |
| Ironic           |                 | Must have          |

#### Support services

The following table lists services which are not the main focus of the testing
(which may be covered by additional scenarios), but are required for the DT to
work properly and can be deployed with any/default configuration.

| Service          | Reason  |
| ---------------- |------------------ |
| Neutron          | needed by other services   |
| Nova             | needed by scenario testing |
| Keystone         | needed by all services     |

#### Additional configuration

Default settings: TLSe

## Considerations/Constraints

N/A

## Testing

| Test framework   | When to run          | Special configuration |
| ---------------- | -------------------- | ----------------------|
| relevant volume tests | tempest stage |           |
| relevant image tests  | tempest stage |           |
| relevant manila tests | tempest stage |           |
| relevant object-storage tests  | tempest stage |           |
| relevant designate tests | tempest stage |           |
| horizon integration   | own stage (post-tempest)|           |
| ironic integration    | tempest stage |           |

## Workflow

1. [Install the OpenStack K8S operators and their dependencies](../../common/)
2. [Configure and deploy the OpenStack control plane](control-plane.md)
3. [Configure and deploy Ceph](edpm-pre-ceph.md)
4. [Configure and deploy the OpenStack data plane](edpm.md)
