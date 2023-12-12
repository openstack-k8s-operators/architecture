# Deployed Topology 3_ocp_workers_2_compute_netapp_ipv4

**Based on OpenStack K8S operators from the "main" branch of
the [OpenStack Operator repo](https://github.com/openstack-k8s-operators/openstack-operator/tree/78b3c876eaf9168f9d95b201997ebdc2da42fa02)
on Oct 17th, 2023**

## General information

| Revision | Change              |    Date    |
|---------:|:--------------------|:----------:|
|     v0.1 | Initial publication | 2023-12-12 |

## Node topology

| Node role                                  | bm/vm | amount |
|--------------------------------------------|-------|--------|
| Openshift master/worker combo-node cluster | vm    | 3      |
| Compute nodes                              | vm    | 2      |

## Services, enabled features and configurations

| Service   | configuration                | Lock-in coverage? |
|-----------|------------------------------|-------------------|
| Manila    | NetApp Backend               | Must have         |
| Neutron   | ML2/OVN, Geneve              | Must have         |
| Barbican  | Crypto backend               | Must have         |
| Glance    | Ceph/RBD                     | Must have         |
| Designate | <will add config>            | Must have         |
| Cinder    | Ceph/RBD Backend             | Must have         |
| Keystone  | Special appliance [redacted] | Interchangable    |
| Compute   | set-nova-scheduler-filter    | Must have         |

### Additional information

#### Nova

#### Cinder

#### OVN

add configuration of ovn extras

## Considerations/Constraints

1. Glance requirement dictates specific lab
2. HSM access limited geographically

## Testing tree

| Test framework   | Stage to run | Special configuration | Test case to report |
|------------------|--------------|-----------------------|:-------------------:|
| Tempest/compute  | stage7       | Use rhel image        |      11223344       |
| Tempest/scenairo | stage7       | Use cirros image      |      22334455       |
| Jordan           | stage7       | None                  |      44556677       |
| Rally/Browbeat   | stage8       | Use CS9 image         |      55667788       |
| Tobiko/Faults    | stage9       | Use cirros image      |      33445566       |

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