# RHV base adoption Topology

This topology contains Director deployed source openStack on RHV that is networked together with RHV deployed openshift cluster. This topology executes test suite that verifies adoption from existing 17.1 osp deployment into podified openstack. The upgrade/migration to the podified OpenStack requires planning various aspects of the environment such as node roles, planning your network topology.

## General information

| Revision | Change                | Date             |
|--------: | :-------------------- | :--------------: |
| v0.1     | Initial publication   | 22.12.23         |

## Node topology
| Node role                                     | bm/vm | amount |
| --------------------------------------------- | ----- | ------ |
| Openshift Compact cluster                     | vm    | 3      |
| Undercloud node - Source osp 17               | vm    | 1      |
| Controller nodes - Source osp 17              | vm    | 3      |
| Compute nodes    - Source osp 17              | vm    | 2      |

##### Networks in RH OSP

| Name         | Type        |
| ----         | ----------- |
| Ctlplane     | VLAN tagged |
| Internal-api | VLAN tagged |
| External     | VLAN tagged |
| Tenant       | VLAN tagged |

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

1. 3 node openshift cluster on RHV.
2. Source openstack with HA is pre-deployed on RHV.
3. Network protocol - ipv4
4. Native VLAN for openstack setup shared between source openstack and target openshift environment.

## Testing

| Test framework   | Special configuration  | Test case to report |
| ---------------- | ---------------------  | :-----------------: |
| Tempest/Sanity   | Use rhel image         | ReportPortal        |
| Workload Test    | Use rhel/cirros image  | ReportPortal        |

## Stages

All stages must be executed in the order listed below.  Everything is required unless otherwise indicated.

1. [Install the OpenStack K8S operators and their dependencies](../../../common/)
2. [Configuring networking on the OCP nodes](vendor/)
3. [Run Dataplane Adoption test suite](control-plane.md)
