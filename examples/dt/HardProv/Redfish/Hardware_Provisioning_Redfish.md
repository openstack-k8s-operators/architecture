# RHOSO Deployed Topology HardProv-3cont_2comp_2ironic-ipv4-geneve-redfish

**Redfish / Sushy**

## General information

| Revision | Change                | Date             |
|--------: | :-------------------- | :--------------: |
| v0.1     | Initial publication   | 2023-12-18      |
| v0.2     | Suggested changes  frpm PR54   | 2024-01-17 |


## Node topology
| Node role                                     | bm/vm | amount |
| --------------------------------------------- | ----- | ------ |
| Openshift master/worker combo-node cluster    | vm    | 3      |
| Compute nodes                                 | vm    | 2      |
| Ironic                                        | vm    | 2      |


## Services, enabled features and configurations
| Service                 | configuration             | Lock-in coverage? |
| ----------------------- | ------------------------- | ----------------- |
| Glance                  |  default                  |  Must have        |
| Ironic                  |  default                  |  Must have        |
| Keystone                |  default                  |  Must have        |
| Neutron                 |  default                  |  Must have        |
| Nova                    |  default                  |  Must have        |


## Considerations/Constraints

1. VM nodes configured with Redfish/Sushy instead of ipmi/vbmc


## Testing tree

| Test framework   | Stage to run | Special configuration | Test case to report |
| ---------------- | ------------ | --------------------- | :-----------------: |
| Tempest/ironic_api       |  stage7 | Use cirros image |                     |
| Tempest/ironic_scenario  |  stage7 | Use cirros image |                     |

## Stages

(determine actual stages needed) All stages must be executed in the order listed below.  Everything is required unless otherwise indicated.

1. [Install dependencies for the OpenStack K8S operators](stage1)
2. [Install the OpenStack K8S operators](stage2)
3. [Configuring networking on the OCP nodes](stage3)
4. [Configure and deploy the control plane](stage4)
5. ~~[Configure and deploy the initial data plane to prepare for CephHCI installation](stage5)~~
6. ~~[Update the control plane and finish deploying the data plane after CephHCI has been installed](stage6)~~
7. [Execute non destructive testing](stage7)
8. [Execute load testing](stage8)
9. [Destructive testing](stage9)
