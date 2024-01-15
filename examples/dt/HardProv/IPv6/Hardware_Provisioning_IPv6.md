# RHOSO Deployed Topology HardProv-3cont_6comp_6ceph-ipv6-geneve

**IPv6**


## General information

| Revision | Change                | Date             |
|--------: | :-------------------- | :--------: |
|   v0.1   | Initial work file     | 2023-12-13 |
|   v0.2   | clarify test framework | 2023-12-13 |

## Node topology
| Node role                                               | bm/vm | amount |
| ---------------------------------------------           | ----- | ------ |
| Openshift master/worker combo-node cluster IPv6 enabled | vm    | 3      |
| Compute nodes                                           | bm    | 6      |
| Ceph                                                    | vm    | 6      |
| Networkers                                              | vm    | 1      |



## Services, enabled features and configurations
| Service                 | configuration             | Lock-in coverage? |
| ----------------------- | ------------------------- | ----------------- |
| Nova                    |  default                  |  Must have        |
| Keystone                |  default                  |  Must have        |
| Glance                  |  default                  |  Must have        |
| Cinder                  |  (Do we need cinder if we only support BFV in odd cases which we can’t directly support because a lack of lvm iscsi support |  Possible  |



## Considerations/Constraints

1. Going on the presumption that OpenShift isn't already configured with IPv6 by default, would need a build configured for that.  Basing this on the impression that IPv6 would be needed in OpenShift in order for IPv6 to work in the hosted OpenStack


## Testing tree

| Test framework     | Stage to run | Special configuration            | Test case to report |
| ----------------   | ------------ | ---------------------            | :-----------------: |
| Tempest/Smoke Test | stage7 | Use cirros image |                     |
|                    |              |                                  |                     |


## Stages

_(existing sample, not necessarily relevant to ironic/hardprov)_  
All stages must be executed in the order listed below.  Everything is required unless otherwise indicated.

1. OpenShift host configured for IPv6 (presuming it isn't already IPv6 by default)
2. [Install dependencies for the OpenStack K8S operators](stage1)
3. [Install the OpenStack K8S operators](stage2)
4. [Configuring networking on the OCP nodes](stage3)
5. [Configure and deploy the control plane](stage4)
6. [Configure and deploy the data plane](stage5)
7. Install and run Tempest (?)
8. Collect logs

