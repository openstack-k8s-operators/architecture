**Based on OpenStack K8S operators from the "main" branch of the [OpenStack Operator repo](https://github.com/openstack-k8s-operators/openstack-operator/tree/78b3c876eaf9168f9d95b201997ebdc2da42fa02) on Oct 17th, 2023**

## General information

| Revision | Change              |  Date   |
| -------: | :------------------ | :-----: |
|     v0.1 | Initial publication | 2023-12-14 |

## Node topology

| Node role                                  | bm/vm | amount |
| ------------------------------------------ | ----- | ------ |
| Openshift master/worker combo-node cluster | vm    | 3      |
| Compute nodes                              | bm    | 2      |

## Services, enabled features and configurations

| Service   | configuration                | Lock-in coverage?  |
| --------- | ---------------------------- | ------------------ |
| Neutron   | ML2/OVN, Geneve              | Must have          |
| SRIOV     | SR-IOV agent with nova config| Must have          |
| Compute   | set-nova-scheduler-filter    | Must have          |
| Cinder    | Ceph/RBD Backend             | Must have          |


## Support services
## Additional services required for integration testing that may not be the subject of this DT
| Service   |  Reason                |
| --------- | ---------------------- |
| Glance    | Must have              |
| Keystone  | needed by all services |
| FIPS      | Enabled by default     |

#### Nova
| Service         | configuration |
| ----------------| --------------|
| Image_type      | rbd           |


#### OVN
add configuration of ovn extras

## Considerations/Constraints

1. Baremetal Computes that support a GPU that supports mediated devices e.g. Tesla T4 
2. Physical setups are required.
3. PCI pass through enabled.
4. 2M hugepage size by setting flavor property: hw:mem_page_size=2048
5. hw:cpu_policy set for CPU pinning.

## Testing tree

| Test framework   | Stage to run | Special configuration | Test case to report |
| ---------------- | ------------ | --------------------- | :-----------------: |
| Tempest/whitebox | stage7       | Use rhel image        |       <TBD>         |

## Stages

All stages must be executed in the order listed below. Everything is required unless otherwise indicated.

1. [Install dependencies for the OpenStack K8S operators](stage1)
2. [Install the OpenStack K8S operators](stage2)
3. [Configuring networking on the OCP nodes](stage3)
4. [Configure and deploy the control plane](stage4)
5. [Execute non destructive testing](stage7)
6. [Execute load testing](stage8)
7. [Destructive testing](stage9)
