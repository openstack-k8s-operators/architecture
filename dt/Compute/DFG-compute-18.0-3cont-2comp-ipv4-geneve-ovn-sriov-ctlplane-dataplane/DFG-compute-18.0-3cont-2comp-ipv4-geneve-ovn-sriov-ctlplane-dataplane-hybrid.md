# Deployed Topology DFG-compute-18.0-3cont-2comp-ipv4-geneve-ovn-sriov-ctlplane-dataplane

**Based on OpenStack K8S operators from the "main" branch of the [OpenStack Operator repo](https://github.com/openstack-k8s-operators/openstack-operator/tree/78b3c876eaf9168f9d95b201997ebdc2da42fa02) on Oct 17th, 2023**

## General information

| Revision | Change                | Date             |
|--------: | :-------------------- | :--------------: |
| v0.1     | Initial publication   | 12.12.23      |

## Node topology
| Node role                                     | bm/vm | amount |
| --------------------------------------------- | ----- | ------ |
| Openshift master/worker combo-node cluster    | vm    | 3      |
| Compute nodes                                 | bm    | 2      |
| Controller                                    | vm    | 1     |


## Services, enabled features and configurations
| Service                                     | configuration                                                 | Lock-in coverage?  |
| ------------------------------------------- | -------------------------------                               | ------------------ |
| Neutron                                     | ML2/OVN-DPDK, Geneve with MQ, balance-tcp and LACP-IGMP       | Must have          |
| SRIOV                                       | SR-IOV agent with nova config                                 | Must have          |

## Considerations/Constraints

1. NFV requires dictates specific lab
2. Physical setups are required
3. Specific switch configuration

## Testing tree

| Test framework   | Stage to run | Special configuration                 | Test case to report |
| ---------------- | ------------ | ---------------------                 | :-----------------: |
| Tempest/Whitebox | stage7       | Use rhel image                        | Compute             |


## Stages

All stages must be executed in the order listed below.  Everything is required unless otherwise indicated.

1. [Install dependencies for the OpenStack K8S operators](stage1)
2. [Install the OpenStack K8S operators](stage2)
3. [Configuring networking on the OCP nodes](stage3)
4. [Configure and deploy the control plane](stage4)
5. [Execute non destructive testing](stage7)
6. [Execute load testing](stage8)
7. [Destructive testing](stage9)
