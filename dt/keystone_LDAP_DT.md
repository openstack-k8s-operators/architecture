# RHOSO Deployed Topology %3_ocp_workers_1_compute_1freeipa_ipv4%

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
| freeipa                                       | vm    | 1      |

## Services, enabled features and configurations
| Service                                        | configuration                 | Lock-in coverage?  |
| ---------------------------------------------- | ----------------------------- | ------------------ |
| Cinder                                         | Any                           | Must have          |
| Glance                                         | Any                           | Must have          |
| Keystone                                       | LDAP config                   | Must have          |
| Barbican                                       | Any                           | Must have          |
| TLS                                            | default                       | Must have          |
| FIPS                                           | default                       | Must have          |
| freeipa-container                              | single supplier setup         | Must have          |



## Considerations/Constraints
1. We will need a freeipa server to connect too for ldap/ldaps connectons
2. We could ether setup a pod in the openshift env using [freeipa-container](https://github.com/freeipa/freeipa-container) or we could setup a vm on rhel9 using [ansible-freeipa](https://github.com/freeipa/ansible-freeipa)
3. The CA from freeipa will need to be passed into the keystone pod so ldaps connections will work.
4. The keystone pod will need to have extra ldap backend settings. See example [config](https://github.com/redhat-openstack/infrared/blob/master/plugins/tripleo-overcloud/vars/overcloud/templates/keystone-ldap-ipa.yml) 
5. Create users and groups in freeipa using the [playbook](https://gitlab.cee.redhat.com/OSP-DFG-security/automation/-/blob/master/playbooks/freeipa-user-group-add.yml) 
6. Run the LDAP playbooks for stage8 testing [Base ldap tests](https://gitlab.cee.redhat.com/OSP-DFG-security/automation/-/blob/master/playbooks/keystone-ldap.yml)

## Testing tree

| Test framework                    | Stage to run | Special configuration | Test case to report  |
| ----------------                  | ------------ | --------------------- | :-----------------:  |
| ansible playbook                  | stage8       |                       |                      |

## Stages

All stages must be executed in the order listed below.  Everything is required unless otherwise indicated.

1. [Install dependencies for the OpenStack K8S operators](stage1)
2. [Install the OpenStack K8S operators](stage2)
3. [Configuring networking on the OCP nodes](stage3)
4. [Configure and deploy the control plane](stage4)
5. [Any](stage5)
6. [Any](stage6)
8. [Execute load testing](stage8)
