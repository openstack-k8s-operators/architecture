# Deployed Topology uni-zeta

**Based on OpenStack K8S operators from the "main" branch of the [OpenStack Operator repo](https://github.com/openstack-k8s-operators/openstack-operator/commit/7354503e770cbb0435700e2e5b2707de9f7d90e5)**

## Purpose
Focused on components with a bit of heterogenous configuration (please see below).

## Node topology
| Node role                                        | bm/vm | amount |
| ------------------------------------------------ | ----- | ------ |
| Openshift master/worker combo-node cluster       | vm    | 3      |
| Compute nodes                                    | vm    | 2      |
| HCI Ceph (TBD, see below)                        | vm    | -      |


## Services, enabled features and configurations

| Service          | configuration                   | Lock-in coverage?  |
| ---------------- | ------------------------------- | ------------------ |
| Cinder           | LVM/NVMeoF                      | Must have          |
| Cinder Backup    | S3(+zstd compression)           | Must have          |
| Glance           | Swift                           | Must have          |
| Neutron          | no DVR                          | Must have          |
| Horizon          | N/A                             | Must have          |


### Support services
The following table lists services which are not the main focus of the testing (which may be covered by additional scenarios), but are required for the DT to work properly and can be deployed with any/default configuration.

| Service          | Reason  |
| ---------------- |------------------ |
| Barbican         | needed by other services   |
| Neutron          | needed by other services   |
| Nova             | needed by scenario testing |
| Swift            | needed by scenario testing |
| Keystone         | needed by all services     |


### Additional configuration

Always-on, default services and features: TLSe


## Considerations/Constraints

1. The S3 backend for cinder-backup requires a valid S3 implementation, which could be provided by HCI Ceph services or by Swift, if Swift can be deployed first.


## Testing tree

| Test framework   | When to run          | Special configuration |
| ---------------- | -------------------- | ----------------------|
| relevant volume tests | tempest stage |           |
| relevant image tests  | tempest stage |           |
| relevant object-storage tests  | tempest stage |           |
| relevant networking tests | tempest stage | full CentOS/RHEL image  |
| horizon integration   | own stage (post-tempest)|           |
