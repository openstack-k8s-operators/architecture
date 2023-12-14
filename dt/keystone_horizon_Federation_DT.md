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
| freeipa                                       | vm    | 1      |


## Services, enabled features and configurations
| Service                                        | configuration                 | Lock-in coverage?  |
| ---------------------------------------------- | ----------------------------- | ------------------ |
| Cinder                                         | Any                           | Must have          |
| Glance                                         | Any                           | Must have          |
| Keystone                                       | Federation config             | Must have          |
| Horizon                                        | Federation config             | Must have          |
| Barbican                                       | Any                           | Must have          |
| TLS                                            | default                       | Must have          |
| FIPS                                           | default                       | Must have          |
| freeipa-container                              | default supplier if using pod | Must have          |
| keycloak-container                             | link to freeipa if using pod  | Must have          | 

## Considerations/Constraints
1. We will need a freeipa server and a Keyclock server, the keycloak server will be connected to the freeipa server with a ldap/ldaps connecton.
2. We could ether setup a pod in the openshift env using [freeipa-container](https://github.com/freeipa/freeipa-container) and [keycloak-container](https://www.keycloak.org/server/containers) or we could setup a vm on rhel9 using [ansible-freeipa](https://github.com/freeipa/ansible-freeipa) and deploy the keycloak pod on the freeipa node using our existing [playbook here](https://gitlab.cee.redhat.com/OSP-DFG-security/automation/-/blob/master/playbooks/run_prep_keycloak_setup.yml)
3. The CA from freeipa will need to be passed into the keystone pod so ldaps connections will work.
4. Additional openstack setup is needed to enable the keycloak backend to keystone using this [playbook](https://gitlab.cee.redhat.com/OSP-DFG-security/automation/-/blob/master/playbooks/run_pre_federation-keycloak.yml)
5. The keystone pod will need to have extra federation settings. See example [config](https://gitlab.cee.redhat.com/OSP-DFG-security/automation/-/blob/master/playbooks/security-keycloak-federation.yml.j2)

## Testing tree

| Test framework                    | Stage to run | Special configuration | Test case to report  |
| ----------------                  | ------------ | --------------------- | :-----------------:  |
| tempest	                        | stage7       |                       |                      |

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
