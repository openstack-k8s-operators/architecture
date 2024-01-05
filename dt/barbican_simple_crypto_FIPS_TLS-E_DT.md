# RHOSO Deployed Topology %DFG-security-openstack-barbican-18.0_director-rhel-virthost-3cont_2comp_1freeipa-ipv4-geneve-lvm-containers-fips-tlse%

**Based on OpenStack K8S operators from the "main" branch of the [OpenStack Operator repo](https://github.com/openstack-k8s-operators/openstack-operator/tree/78b3c876eaf9168f9d95b201997ebdc2da42fa02) on Oct 17th, 2023**

## General information

| Revision | Change                | Date              |
|--------: | :-------------------- | :--------------:  |
| v0.1     | Initial publication   | %13/12/2023%      |

## Node topology
| Node role                                      | bm/vm | amount |
| ---------------------------------------------- | ----- | ------ |
| Openshift master/worker combo-node cluster     |  vm   |   3    |
| Compute nodes                                  |  vm   |   1    |

## Services, enabled features and configurations
| Service                                        | configuration                 | Lock-in coverage?  |
| ---------------------------------------------- | ----------------------------- | ------------------ |
| Cinder                                         | swift-encryption              | Must have          |
| Glance                                         | signed-image                  | Must have          |
| Nova                                           | signed-image                  | Must have          |
| Keystone                                       | any                           | Must have          |
| Barbican                                       | Simple Crypto backend         | Must have          |
| TLS                                            | default                       | Must have          |
| FIFS                                           | default                       | Must have          |

## Considerations/Constraints

1.
2.

## Testing tree

| Test framework                                                                                                        | Stage to run | Special configuration | Test case to report  |
| ----------------                                                                                                      | ------------ | --------------------- | :-----------------:  |
| barbican_tempest_plugin.tests.api.test_consumers.ConsumersTest                                                        | stage7       |                       |                      |
| barbican_tempest_plugin.tests.api.test_orders.OrdersTest                                                              | stage7       |                       |                      |
| barbican_tempest_plugin.tests.api.test_containers.ContainersTest                                                      | stage7       |                       |                      |
| barbican_tempest_plugin.tests.api.test_quotas.ProjectQuotasTest                                                       | stage7       |                       |                      |
| barbican_tempest_plugin.tests.api.test_quotas.QuotasTest                                                              | stage7       |                       |                      |
| barbican_tempest_plugin.tests.api.test_secret_metadata.SecretMetadataTest                                             | stage7       |                       |                      |
| barbican_tempest_plugin.tests.api.test_secrets.SecretsTest                                                            | stage7       |                       |                      |
| barbican_tempest_plugin.tests.scenario.test_volume_encryption.VolumeEncryptionTest.test_encrypted_cinder_volumes_luks | stage7       |                       |                      |
| barbican_tempest_plugin.tests.scenario.test_image_signing.ImageSigningSnapshotTest                                    | stage7       |                       |                      |
| barbican_tempest_plugin.tests.scenario.test_certificate_validation.CertificateValidationTest                          | stage7       |                       |                      |
| barbican_tempest_plugin.tests.scenario.test_image_signing.ImageSigningTest                                            | stage7       |                       |                      |
