# Deployed Topology DFG-upgrades-adoption-18.0-from-17.1-passed-phase2-rhev-3cont-2comp-ipv4-HA-geneve-ovn

## General information

| Revision | Change                | Date             |
|--------: | :-------------------- | :--------------: |
| v0.1     | Initial publication   | 22.12.23      |

## Node topology
| Node role                                     | bm/vm | amount |
| --------------------------------------------- | ----- | ------ |
| Openshift master/worker combo-node cluster    | vm    | 3      |
| Undercloud node - Source osp 17               | vm    | 1      |
| Controller nodes - Source osp 17              | vm    | 3      |
| Compute nodes    - Source osp 17              | vm    | 2      |


## Services, enabled features and configurations
| Service                                     | configuration                   | Lock-in coverage?  |
| ------------------------------------------- | ------------------------------- | ------------------ |
| RabbitMQ                                    | default                         | Must have          |
| OVN                                         | default                         | Must have          |
| galera                                      | default                         | Must have          |
| Keystone                                    | default                         | Must have          |
| glance                                      | default                         | Must have          |
| placement                                   | default                         | Must have          |
| nova                                        | default                         | Must have          |
| neutron                                     | default                         | Must have          |

## Considerations/Constraints

1. 3 node openshift cluster on RHEV.
2. Source openstack with HA is pre-deployed on RHEV.
3. Network protocol - ipv4
4. Native VLAN for openstack setup shared between source openstack and target openshift environment.
   - Nic1: RHEV network rhevm
   - Nic2: RHEV network OSP-RHV-Ctlplane
   - Nic3: RHEV network OSP-RHV-API
   - Nic4: RHEV network OSP-RHV-Tenant
   - Nic5: RHEV network OSP-RHV-External

## Testing tree

| Test framework   | Stage to run | Special configuration                 | Test case to report |
| ---------------- | ------------ | ---------------------                 | :-----------------: |
| Tempest/Sanity   | stage5       | Use rhel image                        | ReportPortal        |
| Workload Test    | stage5       | Use rhel/cirros image                 | ReportPortal        |

## Stages

All stages must be executed in the order listed below.  Everything is required unless otherwise indicated.

1. [Install dependencies for the OpenStack K8S operators](stage1)
2. [Install the OpenStack K8S operators](stage2)
3. [Configuring networking on the OCP nodes](stage3)
4. [Run Dataplane Adoption test suite](stage4)
5. [Execute Testing](stage5)
