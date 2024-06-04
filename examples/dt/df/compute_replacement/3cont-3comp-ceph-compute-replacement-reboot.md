# Deployed Topology 3cont-3comp-ceph-compute-replacement-reboot

**Based on OpenStack K8S operators from the "main" branch of the [OpenStack Operator repo](https://github.com/openstack-k8s-operators/openstack-operator/tree/78b3c876eaf9168f9d95b201997ebdc2da42fa02) on Oct 17th, 2023**

## General information

| Revision | Change                | Date             |
|--------: | :-------------------- | :--------------: |
| v0.1     | Initial publication   | 12/15/2023      |

## Node topology
| Node role                                     | bm/vm | amount |
| --------------------------------------------- | ----- | ------ |
| Openshift master/worker combo-node cluster    | vm    | 3      |
| Compute nodes                                 | vm    | 3      |
| Ceph 7                                        | vm    | 1      |


## Services, enabled features and configurations
| Service                                     | configuration                   | Lock-in coverage?  |
| ------------------------------------------- | ------------------------------- | ------------------ |
| FIPS Mode                                   | default                         | Must have/standard |

## Considerations/Constraints

1. A new vm that was not part of initial deployment is required when performing scale up stage
2.

## Testing tree

| Test framework   | Stage to run | Special configuration | Test case to report |
| ---------------- | ------------ | --------------------- | :-----------------: |
| Tempest/compute  | stage10       | Use rhel image        | 11223344            |
| Tempest/scenairo | stage10       | Use cirros image      | 22334455            |
| Jordan           | stage10       | None                  | 44556677            |
| Rally/Browbeat   | stage11       | Use CS9 image         | 55667788            |
| Tobiko/Faults    | stage12       | Use cirros image      | 33445566            |

## Stages

All stages must be executed in the order listed below.  Everything is required unless otherwise indicated.

1. [Install dependencies for the OpenStack K8S operators](stage1)
2. [Install the OpenStack K8S operators](stage2)
3. [Configuring networking on the OCP nodes](stage3)
4. [Configure and deploy the control plane](stage4)
5. [Configure and deploy the initial data plane to prepare for CephHCI installation](stage5)
6. [Update the control plane and finish deploying the data plane after CephHCI has been installed](stage6)
7. [Execute openstack node reboot](stage7)
8. [Execute scale down of a compute node](stage8)
9. [Execute scale up of a new compute node](stage9)
10. [Execute non destructive testing](stage10)
11. [Execute load testing](stage11)
12. [Destructive testing](stage12)
