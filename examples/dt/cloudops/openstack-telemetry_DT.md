# RHOSO Deployed Topology OpenStack Observability

**Based on OpenStack K8S operators from the "main" branch of the [OpenStack Operator repo](https://github.com/openstack-k8s-operators/openstack-operator/tree/78b3c876eaf9168f9d95b201997ebdc2da42fa02) on Oct 17th, 2023**

## General information

| Revision | Change                | Date             |
|--------: | :-------------------- | :--------------: |
| v0.1     | Initial publication   | 14.12.23      |

## Node topology
| Node role                                     | bm/vm | amount |
| --------------------------------------------- | ----- | ------ |
| Compute nodes                                 | vm    | 2      |
| Controller nodes                              | vm    | 3      |


## Services, enabled features and configurations
| Service                                     | configuration                     | Lock-in coverage?  |
| ------------------------------------------- | ----------------------------------| ------------------ |
| Nova                                        | default                           | Standard           |
| Neutron                                     | default                           | Standard           |
| Cinder                                      | default                           | Standard           |
| Glance                                      | default                           | Standard           |
| Keystone                                    | default                           | Standard           |
| Memcached                                   | default                           | Standard           |
| RabbitMQ                                    | default                           | Standard           |
| Telemetry                                   | aka ceilometer, aodh & prometheus | Must have          |

## Considerations/Constraints
1. Telemetry should be enabled that will enable autoscaling, telemetry, prometheus deployment, grafana deployment, etc.
2. No topology constraints


## Testing tree

| Test framework       | Stage to run  | Special configuration | Test case to report |
| -------------------- | ------------  | --------------------- | :-----------------: |
| Autoscaling          | stage 10      | Use cirros image      |    TBD         |
| Tempest-telemetry    | stage 11      | Use rhel image        |    TBD         |


## Stages

All stages must be executed in the order listed below.  Everything is required unless otherwise indicated.

1. [Install dependencies for the OpenStack K8S operators](stage1)
2. [Install the OpenStack K8S operators](stage2)
3. [Configuring networking on the OCP nodes](stage3)
4. [Configure and deploy the control plane](stage4)
5. [Configure and deploy the initial data plane to prepare for CephHCI installation](stage5)
6. [Update the control plane and finish deploying the data plane after CephHCI has been installed](stage6)
7. [Execute non destructive testing](stage7)
8. [Execute load testing](stage8)
9. [Destructive testing](stage9)
