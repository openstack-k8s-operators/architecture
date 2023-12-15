# Deployed Topology uni-beta

**Based on OpenStack K8S operators from the "main" branch of the [OpenStack Operator repo](https://github.com/openstack-k8s-operators/openstack-operator/commit/ee6dc8ad78ef14ef8abe1fa310ea21d7e01948fc)**

## General information

| Revision | Change                | Date             |
|--------: | :-------------------- | :--------------: |
| v0.1     | Initial publication   | 2023-12-14       |

## Purpose
Focused on components with NFS-based backends.

## Node topology
| Node role                                        | bm/vm | amount |
| ------------------------------------------------ | ----- | ------ |
| Openshift master/worker combo-node cluster       | vm    | 3      |
| Compute nodes                                    | vm    | 2      |


## Services, enabled features and configurations

| Service          | configuration                   | Lock-in coverage?  |
| ---------------- | ------------------------------- | ------------------ |
| Cinder           | NetApp/NFS                      | Must have          |
| Cinder Backup    | NFS                             | Must have          |
| Glance           | file/NFS                        | Must have          |
| Manila           | NFS from Netapp                 | Must have          |
| Horizon          | N/A                             | Must have          |


### Support services
The following table lists services which are not the main focus of the testing (which may be covered by additional scenarios), but are required for the DT to work properly and can be deployed with any/default configuration.

| Service          | Reason  |
| ---------------- |------------------ |
| Swift            | needed for scenario testing |
| Neutron          | needed by other services   |
| Nova             | needed by scenario testing |
| Keystone         | needed by all services     |


### Additional configuration
- other default settings for complex jobs (TLSe, FIPS)

## Considerations/Constraints

1. The DT requires a NetApp appliance with multiple NFS shares, which needs to be accessible and that may constraint the location.


## Testing tree

| Test framework   | When to run          | Special configuration |
| ---------------- | -------------------- | ----------------------|
| relevant volume tests | tempest stage |           |
| relevant image tests  | tempest stage |           |
| relevant share tests  | tempest stage |           |
| horizon integration   | own stage (post-tempest)|           |
