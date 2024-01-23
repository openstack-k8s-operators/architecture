# Deployed Topology uni-eta

**Based on OpenStack K8S operators from the "main" branch of the [OpenStack Operator repo](https://github.com/openstack-k8s-operators/openstack-operator/commit/7354503e770cbb0435700e2e5b2707de9f7d90e5)**

## Purpose
Focused on testing cinder with iSCSI, glance over cinder, and a few additional testing for neutron.

## Node topology
| Node role                                        | bm/vm | amount |
| ------------------------------------------------ | ----- | ------ |
| Openshift master/worker combo-node cluster       | vm    | 3      |
| Compute nodes                                    | vm    | 2      |


## Services, enabled features and configurations

| Service          | configuration                   | Lock-in coverage?  |
| ---------------- | ------------------------------- | ------------------ |
| Cinder           | iSCSI                           | Must have          |
| Glance           | cinder as backend               | Must have          |
| Neutron          | default                         | Must have          |
| Horizon          | N/A                             | Must have          |


### Support services
The following table lists services which are not the main focus of the testing (which may be covered by additional scenarios), but are required for the DT to work properly and can be deployed with any/default configuration.

| Service          | Reason  |
| ---------------- |------------------ |
| Cinder Backup    | needed by scenario testing |
| Barbican         | needed by other services   |
| Nova             | needed by scenario testing |
| Swift            | needed by scenario testing |
| Keystone         | needed by all services     |


### Additional configuration

Always-on, default services and features: TLSe


## Considerations/Constraints

1. Cinder needs access to an iSCSI appliance.


## Testing tree

| Test framework   | When to run          | Special configuration |
| ---------------- | -------------------- | ----------------------|
| relevant volume tests | tempest stage |           |
| relevant image tests  | tempest stage |           |
| relevant networking tests | tempest stage | full CentOS/RHEL image  |
| relevant neutron tobiko tests | tobiko stage |                      |
| horizon integration   | own stage (post-tempest/tobiko)|           |
