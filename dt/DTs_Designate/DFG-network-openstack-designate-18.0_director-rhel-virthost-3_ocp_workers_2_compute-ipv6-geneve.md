# Deployed Topology DFG-network-openstack-designate-18.0_director-rhel-virthost-3_ocp_workers_2_compute-ipv6-geneve

**Based on OpenStack K8S operators from the "main" branch of the [OpenStack Operator repo](https://github.com/openstack-k8s-operators/openstack-operator/tree/78b3c876eaf9168f9d95b201997ebdc2da42fa02) on Oct 17th, 2023**

## General information

| Revision | Change              |  Date   |
| -------: | :------------------ | :-----: |
|     v0.1 | Initial publication | 2023-15-12 |

## Node topology

| Node role                                  | bm/vm | amount |
| ------------------------------------------ | ----- | ------ |
| Openshift master/worker combo-node cluster | vm    | 3      |
| Compute nodes                              | vm    | 2      |

## Services, enabled features and configurations

| Service   | configuration                | Lock-in coverage?  |
|-----------|------------------------------| ------------------ |
| Neutron   | ML2/OVN, Geneve              | Must have          |
| Designate | Geneve                       | Must have          |
| Keystone  | default                      | Interchangable     |
| Compute   | set-nova-scheduler-filter    | Must have          |

### Additional information 
We need networking protocol IPv6  
ןפסכ
## Testing tree
Tempest

| Test framework   | Stage to run | Special configuration | Test case to report |
| ---------------- | ------------ | --------------------- | :-----------------: |
| Tempest/designate| stage7       | Use rhel image        |      Designate      |

## Stages

All stages must be executed in the order listed below. Everything is required unless otherwise indicated.

1. [Install dependencies for the OpenStack K8S operators](stage1)
2. [Install the OpenStack K8S operators](stage2)
3. [Configuring networking on the OCP nodes](stage3)
4. [Configure and deploy the control plane](stage4)
5. [Configure and deploy the initial data plane to prepare for CephHCI installation](stage5)
6. [Update the control plane and finish deploying the data plane after CephHCI has been installed](stage6)
7. [Execute non destructive testing](stage7)
8. [Execute load testing](stage8)
9. [Destructive testing](stage9)