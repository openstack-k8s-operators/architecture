# Deployed Topology uni-delta

**Based on OpenStack K8S operators from the "main" branch of the [OpenStack Operator repo](https://github.com/openstack-k8s-operators/openstack-operator/commit/d1bd4f70ded050463064d929c7342ccbcb660bff)**

## General information

| Revision | Change                | Date             |
|--------: | :-------------------- | :--------------: |
| v0.1     | Initial publication   | 2023-12-15       |

## Purpose
Almost a twin of VA1/uni03gamma, focused on testing external Ceph, and manila with ganesha.

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

Always-on, default services and features

| Service  |
| -------- |
| FIPS     |
| TLS-e    |


## Considerations/Constraints

N/A


## Testing tree

| Test framework   | When to run          | Special configuration |
| ---------------- | -------------------- | ----------------------|
| relevant volume tests | tempest stage |           |
| relevant image tests  | tempest stage |           |
| relevant manila tests | tempest stage |           |
| relevant object-storage tests  | tempest stage |           |
| horizon integration   | own stage (post-tempest)|           |
