# DFG-osasinfra-shiftstack_ci-osp_verification

## General information

| Revision | Change                | Date             |
|--------: | :-------------------- | :--------------: |
| v0.1     | Initial publication   | 12.12.23         |
| v0.2     | Addressing comments   | 30.01.23         |

This DT is intented to run in the integration pipeline and should take no more than 4 hours.
It will use a restricted amount of resources to accelerate results and ensure that the OSP candidate release passes acceptance criteria as a shiftstack cluster cloud.

## Node topology
| Node role                                     | bm/vm | amount |
| --------------------------------------------- | ----- | ------ |
| Openshift master/worker combo-node cluster    | vm    | 3      |
| Compute nodes                                 | bm    | 1      |


## Services, enabled features and configurations
**Based on https://github.com/openshift/installer/tree/master/docs/user/openstack#openstack-requirements

| Service                                     | configuration                                                | Lock-in coverage?  |
| ------------------------------------------- | -------------------------------------------------------------| ------------------ |
| external Ceph                               |                                                              | Must have          |
| Neutron                                     | ML2/OVN                                                      | Must have          |
| Octavia                                     |                                                              | Must have          |
| Swift                                       | rados-gw backed by Ceph                                      | Must have          |
| Keystone                                    | user/password and app creds                                  | Must have          |
| Nova                                        | Metadata service enabled & NovaEnableRbdBackend disabled     | Must have          |
| Glance                                      | RBD - backed by Ceph                                         | Must have          |
| Cinder                                      | RBD - backed by Ceph                                         | Must have          |
| Manila                                      | CephFS through NFS (ganesha)                                 | Must have          |
| Barbican                                    |                                                              | Must have          |
| ssl or tls-e e2e encryption                 |                                                              | Must have          |
| ipv4 and ipv6 provider subnets              |                                                              | Must have          |

## Considerations/Constraints

1. OSASINFRA requires dictates specific lab
2. Physical setups are required:
    - Hybrid: titan01 (Hypervisor) + titan05
    - Hybrid: titan02 (Hypervisor) + titan06
    - Hybrid: titan03 (Hypervisor) + titan07
3. Specific switch configuration extending the OSP networks to the physical layer so it supports the physical computes.
    - This configuration will remain static.
4. Use stable openshift version to test openstack candidate release.
5. A subset of testing is selected to exercise the Openshift integration with opensatck.

## Testing tree

| Test framework                        | Stage to run |  Test case to report |
| ------------------------------------- | ------------ |  ------------------- |
| Openshift Openstack-tests             | stage8       |  ReportPortal        |

## Stages

All stages must be executed in the order listed below.  Everything is required unless otherwise indicated.

1. [Install dependencies for the OpenStack K8S operators](stage1)
2. [Install the OpenStack K8S operators](stage2)
3. [Configuring networking on the OCP nodes](stage3)
4. [Configure and deploy the control plane](stage4)
5. [Configure and deploy the initial data plane to prepare for Ceph installation](stage5)
6. [Update the control plane and finish deploying the data plane after Ceph has been installed](stage6)
7. [Install OCP Cluster](stage7)
8. [Execute testing](stage8)
9. [Destroy OCP Cluster](stage9)

