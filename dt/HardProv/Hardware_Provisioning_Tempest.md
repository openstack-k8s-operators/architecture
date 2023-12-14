# Deployed Topology HardProv Tempest job, Integration CI

**basing this off of the [HardProv rqci-17.1 IRtempest job](https://rhos-ci-jenkins.lab.eng.tlv2.redhat.com/job/DFG-hardware_provisioning-rqci-17.1-3cont_3ceph_2comp_2ironic-ipv4-geneve-IRtempest), although we may want to see if any part of IPv6 needs to be included too**


## General information

| Revision | Change                | Date             |
|--------: | :-------------------- | :--------------: |
|   v0.1   | Initial work file     | 12.13.23      |

## Node topology
| Node role                                     | bm/vm | amount |
| --------------------------------------------- | ----- | ------ |
| Openshift master/worker combo-node cluster    | vm    | 1      |
| Compute nodes                                 | bm    | 2      |
| Networkers                                    | vm    | 1      |
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
| ironic_api       |  ??          |                                       |                     |
| ironic_scenario  |  ??          |                                       |                     |
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

