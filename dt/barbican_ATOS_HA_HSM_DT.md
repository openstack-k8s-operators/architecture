# RHOSO Deployed Topology %3_ocp_workers_1_compute_2atos_ipv4%

**Based on OpenStack K8S operators from the "main" branch of the [OpenStack Operator repo](https://github.com/openstack-k8s-operators/openstack-operator/tree/78b3c876eaf9168f9d95b201997ebdc2da42fa02) on Oct 17th, 2023**

## General information

| Revision | Change                | Date              |
|--------: | :-------------------- | :--------------:  |
| v0.1     | Initial publication   | %13/12/2023%      |

## Node topology
| Node role                                     | bm/vm    | amount |
| --------------------------------------------- | -----    | ------ |
| Openshift master/worker combo-node cluster    | vm       | 3      |
| Compute nodes                                 | vm       | 1 or > |
| Atos HSM                                      | RDU2/bm  | 1      |
| Atos HSM                                      | PARIS/bm | 1      |

## Services, enabled features and configurations
| Service                                        | configuration                 | Lock-in coverage?  |
| ---------------------------------------------- | ----------------------------- | ------------------ |
| Cinder                                         | swift-encryption              | Must have          |
| Glance                                         | signed-image                  | Must have          |
| Nova                                           | signed-image                  | Must have          |
| Keystone                                       | Any                           | Must have          |
| Barbican                                       | ATOS HA config                | Must have          |
| TLS                                            | default                       | Must have          |
| FIPS                                           | default                       | Must have          |

## Considerations/Constraints
1. barbican will need to user a specific HA config for the HSM config. Example [Config](https://gitlab.cee.redhat.com/OSP-DFG-security/automation/-/blob/master/playbooks/atos-17.1-ha.yaml.j2)
2. The ansible playbook will do the HA failover testing. Example [playbook](https://gitlab.cee.redhat.com/OSP-DFG-security/automation/-/blob/master/playbooks/run_barbican_ATOS_HA_test.yml) Please note that we will have to do this iptables blocking of an HSM access differently as we are dealing with Openshift pods now.

## Testing tree

| Test framework                    | Stage to run | Special configuration | Test case to report  |
| ----------------                  | ------------ | --------------------- | :-----------------:  |
| Ansible playbook                  | stage8       |                       |                      |

## Stages

All stages must be executed in the order listed below.  Everything is required unless otherwise indicated.

1. [Install dependencies for the OpenStack K8S operators](stage1)
2. [Install the OpenStack K8S operators](stage2)
3. [Configuring networking on the OCP nodes](stage3)
4. [Configure and deploy the control plane](stage4)
5. [Any](stage5)
6. [Any](stage6)
8. [Execute load testing](stage8)
