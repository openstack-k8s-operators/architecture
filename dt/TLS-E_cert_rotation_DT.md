# RHOSO Deployed Topology %3_ocp_workers_1_compute_ipv4%

**Based on OpenStack K8S operators from the "main" branch of the [OpenStack Operator repo](https://github.com/openstack-k8s-operators/openstack-operator/tree/78b3c876eaf9168f9d95b201997ebdc2da42fa02) on Oct 17th, 2023**

## General information

| Revision | Change                | Date              |
|--------: | :-------------------- | :--------------:  |
| v0.1     | Initial publication   | %13/12/2023%      |

## Node topology
| Node role                                     | bm/vm | amount |
| --------------------------------------------- | ----- | ------ |
| Openshift master/worker combo-node cluster    | vm    | 3      |
| Compute nodes                                 | vm    | 1 or > |


## Services, enabled features and configurations
| Service                                        | configuration                 | Lock-in coverage?  |
| ---------------------------------------------- | ----------------------------- | ------------------ |
| Cinder                                         | Any                           | Must have          |
| Glance                                         | Any                           | Must have          |
| Keystone                                       | Any                           | Must have          |
| Barbican                                       | Any                           | Must have          |
| TLS                                            | default                       | Must have          |
| FIPS                                           | default                       | Must have          |

## Considerations/Constraints
1. We will need to issues certmanager rotation calls for service certificates
2. We will need to issues certmanager rotation calls for CA certificates
3. This will need to not interfear with other CI jobs stablility


## Testing tree

| Test framework                    | Stage to run | Special configuration | Test case to report  |
| ----------------                  | ------------ | --------------------- | :-----------------:  |
| rotation and tempest	            | stage9       |                       |                      |

## Stages

All stages must be executed in the order listed below.  Everything is required unless otherwise indicated.

1. [Install dependencies for the OpenStack K8S operators](stage1)
2. [Install the OpenStack K8S operators](stage2)
3. [Configuring networking on the OCP nodes](stage3)
4. [Configure and deploy the control plane](stage4)
5. [Any](stage5)
6. [Any](stage6)
7. [Execute non destructive testing](stage7)
8. [Execute load testing](stage8)
9. [Destructive testing](stage9)
