# Deployed Topology uni-delta

**Based on OpenStack K8S operators from the "main" branch of the [OpenStack Operator repo](https://github.com/openstack-k8s-operators/openstack-operator/commit/7354503e770cbb0435700e2e5b2707de9f7d90e5)**

## Purpose

Almost a twin of VA1/uni03gamma, focused on testing external Ceph, manila with ganesha, and designate.

## Node topology
| Node role                                        | bm/vm | amount |
| ------------------------------------------------ | ----- | ------ |
| Openshift master/worker combo-node cluster       | vm    | 3      |
| Compute nodes                                    | vm    | 2      |
| External Ceph                                    | vm    | 3      |


## Services, enabled features and configurations

| Service          | configuration                   | Lock-in coverage?  |
| ---------------- | ------------------------------- | ------------------ |
| Cinder           | Ceph                            | Must have          |
| Cinder Backup    | Ceph                            | Must have          |
| Glance           | Ceph                            | Must have          |
| Manila           | NFS ganesha                     | Must have          |
| RGW as Swift     | ---                             | Must have          |
| Designate        |                                 | Must have          |
| Horizon          | N/A                             | Must have          |


### Support services
The following table lists services which are not the main focus of the testing (which may be covered by additional scenarios), but are required for the DT to work properly and can be deployed with any/default configuration.

| Service          | Reason  |
| ---------------- |------------------ |
| Barbican         | needed by other services   |
| Neutron          | needed by other services   |
| Nova             | needed by scenario testing |
| Keystone         | needed by all services     |


### Additional configuration

Default settings: TLSe


## Considerations/Constraints

N/A


## Testing tree

| Test framework   | When to run          | Special configuration |
| ---------------- | -------------------- | ----------------------|
| relevant volume tests | tempest stage |           |
| relevant image tests  | tempest stage |           |
| relevant manila tests | tempest stage |           |
| relevant object-storage tests  | tempest stage |           |
| relevant designate tests | tempest stage |           |
| horizon integration   | own stage (post-tempest)|           |
