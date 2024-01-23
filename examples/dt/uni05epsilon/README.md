# Deployed Topology uni-epsilon

**Based on OpenStack K8S operators from the "main" branch of the [OpenStack Operator repo](https://github.com/openstack-k8s-operators/openstack-operator/commit/7354503e770cbb0435700e2e5b2707de9f7d90e5)**

## Purpose
Focused on testing:
- volume operations which involve multiple backends, including migrations;
- glance with multiple backends (cinder/NFS, ceph and Swift) but cinder/NFS as the primary one.

## Node topology
| Node role                                        | bm/vm | amount |
| ------------------------------------------------ | ----- | ------ |
| Openshift master/worker combo-node cluster       | vm    | 3      |
| Compute nodes                                    | vm    | 2      |
| HCI Ceph                                         | vm    | -      |


## Services, enabled features and configurations

| Service          | configuration                      | Lock-in coverage?  |
| ---------------- | ---------------------------------- | ------------------ |
| Cinder           | iSCSI+NFS+Ceph                     | Must have          |
| Cinder Backup    | Swift/RGW                          | Must have          |
| Glance           | Cinder/NFS(primary)+Ceph+Swift/RGW | Must have          |


### Support services
The following table lists services which are not the main focus of the testing (which may be covered by additional scenarios), but are required for the DT to work properly and can be deployed with any/default configuration.

| Service          | Reason  |
| ---------------- |------------------ |
| Barbican         | needed by other services   |
| Neutron          | needed by other services   |
| Nova             | needed by scenario testing |
| RGW              | needed by other services   |
| Keystone         | needed by all services     |


### Additional configuration

Always-on, default services and features: TLSe


## Considerations/Constraints

1. Cinder requires access to an iSCSI appliance and a standalone NFS server.


## Testing tree

| Test framework   | When to run          | Special configuration |
| ---------------- | -------------------- | ----------------------|
| relevant volume multibackend tests for all backends combinations | tempest stage |           |
| relevant image tests  | tempest stage |           |
