# Deployed Topology uni-epsilon

**Based on OpenStack K8S operators from the "main" branch of the [OpenStack Operator repo](https://github.com/openstack-k8s-operators/openstack-operator/commit/d1bd4f70ded050463064d929c7342ccbcb660bff)**

## General information

| Revision | Change                | Date             |
|--------: | :-------------------- | :--------------: |
| v0.1     | Initial publication   | 2023-12-15       |

## Purpose
Focused on testing:
- volume operations which involve multiple backends, including migrations;
- glance over cinder with NFS 

## Node topology
| Node role                                        | bm/vm | amount |
| ------------------------------------------------ | ----- | ------ |
| Openshift master/worker combo-node cluster       | vm    | 3      |
| Compute nodes                                    | vm    | 2      |
| HCI Ceph                                         | vm    | -      |


## Services, enabled features and configurations

| Service          | configuration                   | Lock-in coverage?  |
| ---------------- | ------------------------------- | ------------------ |
| Cinder           | iSCSI+NFS+Ceph                  | Must have          |
| Cinder Backup    | Swift                           | Must have          |
| Glance           | Cinder (NFS)                    | Must have          |


### Support services
The following table lists services which are not the main focus of the testing (which may be covered by additional scenarios), but are required for the DT to work properly and can be deployed with any/default configuration.

| Service          | Reason  |
| ---------------- |------------------ |
| Barbican         | needed by other services   |
| Neutron          | needed by other services   |
| Nova             | needed by scenario testing |
| Swift            | (default)                       | Must have          |
| Keystone         | needed by all services     |


### Additional configuration

Always-on, default services and features

| Service  |
| -------- |
| FIPS     |
| TLS-e    |


## Considerations/Constraints

1. Cinder requires access to an iSCSI appliance and a standalone NFS server.


## Testing tree

| Test framework   | When to run          | Special configuration |
| ---------------- | -------------------- | ----------------------|
| relevant volume multibackend tests for all backends combinations | tempest stage |           |
| relevant image tests  | tempest stage |           |
