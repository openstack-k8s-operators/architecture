# RHOSO Deployed Topology HardProv_3ceph_2comp_2ironic-ipv4-geneve_tempest


**Tempest tests running against baremetal**


## General information

| Revision | Change                | Date          |
|--------: | :-------------------- | :-----------: |
|   v0.1   | Initial work file     | 2023-12-13 |
|   v0.2   | clarify test framework     | 2023-12-13 |

## Node topology
| Node role                                     | bm/vm | amount |
| --------------------------------------------- | ----- | ------ |
| Openshift master/worker combo-node cluster    | vm    | 3      |
| Compute nodes                                 | bm    | 2      |
| Networkers                                    | vm    | 1      |
| Ceph                                          | vm    | 3      |
| non-provisioned nodes for Tempest testcases   | bm    | 2      |



## Services, enabled features and configurations
| Service                 | configuration             | Lock-in coverage? |
| ----------------------- | ------------------------- | ----------------- |
| Nova                    |  default                  |  Must have        |
| Keystone                |  default                  |  Must have        |
| Glance                  |  default                  |  Must have        |
| Cinder                  |  (Do we need cinder if we only support BFV in odd cases which we can’t directly support because a lack of lvm iscsi support |  Possible  |



## Considerations/Constraints

1. Tempest needs 2 baremetal or virtualized baremetal nodes 
2. Extra nodes are defined but not part of the Openstack itself, created/defined at the beginning of the job before starting any of the OpenStack setup

## Testing tree

| Test framework   | Stage to run | Special configuration                 | Test case to report |
| ---------------- | ------------ | ---------------------                 | :-----------------: |
| Tempest/ironic_api       |  stage7 | Use cirros image |                     |
| Tempest/ironic_scenario  |  stage7 | Use cirros image |                     |
|                  |              |                                       |                     |


## Stages

_(existing sample, not necessarily relevant to ironic/hardprov)_  
All stages must be executed in the order listed below.  Everything is required unless otherwise indicated.

1. Do we need to create/define the extra nodes for ironic-tempest before everything else?
2. [Install dependencies for the OpenStack K8S operators](stage1)
3. [Install the OpenStack K8S operators](stage2)
4. [Configuring networking on the OCP nodes](stage3)
5. [Configure and deploy the control plane](stage4)
6. [Configure and deploy the data plane](stage5)
7. Install and run Tempest
8. Collect logs

