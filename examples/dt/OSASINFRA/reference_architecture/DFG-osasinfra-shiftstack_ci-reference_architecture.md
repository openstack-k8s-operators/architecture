# DFG-osasinfra-shiftstack_ci-reference_architecture

## General information

| Revision | Change                | Date             |
|--------: | :-------------------- | :--------------: |
| v0.1     | Initial publication   | 12.12.23         |
| v0.2     | Addressing comments   | 30.01.23         |

This DT is intented to run in the architecture pipeline and should take no more than 5 days.
It is based on VA-1 and includes the configuration detailed in the reference architeceture:

https://access.redhat.com/documentation/en-us/red_hat_openstack_platform/16.2/html/reference_architecture_for_deploying_red_hat_openshift_container_platform_on_red_hat_openstack_platform/technology-overview#solution-overview

This DT will be used to test OCP on top of an stable RHOSP18 cloud.


## Node topology
| Node role                                     | bm/vm | amount |
| --------------------------------------------- | ----- | ------ |
| Openshift master/worker combo-node cluster    | vm    | 3      |
| Compute nodes                                 | bm    | 3      |


## Services, enabled features and configurations
**Based on https://github.com/openshift/installer/tree/master/docs/user/openstack#openstack-requirements

| Service                                     | configuration                                                | Lock-in coverage?  |
| ------------------------------------------- | -------------------------------------------------------------| ------------------ |
| HCI                                         |                                                              | Must have          |
| Neutron                                     | ML2/OVN                                                      | Must have          |
| Octavia                                     |                                                              | Must have          |
| Swift                                       | rados-gw backed by Ceph(HCI)                                 | Must have          |
| Keystone                                    | user/password and app creds                                  | Must have          |
| Nova                                        | Metadata service enabled & NovaEnableRbdBackend disabled     | Must have          |
| Glance                                      | RBD - backed by Ceph (HCI)                                   | Must have          |
| Cinder                                      | RBD - backed by Ceph (HCI)                                   | Must have          |
| Manila                                      | CephFS through NFS (ganesha)                                 | Must have          |
| Barbican                                    |                                                              | Must have          |
| ssl or tls-e e2e encryption                 |                                                              | Must have          |
| ipv4 and ipv6 provider subnets              |                                                              | Must have          |

## Considerations/Constraints

1. OSASINFRA requires dictates specific lab
2. Physical setups are required:
    - titan08 (Underlying OCP)
    - titan04 (compute-0)
    - titan05 (compute-1)
    - titan07 (compute-2)
3. Specific switch configuration extending the OSP networks to the physical layer so it supports the physical computes.
    - This configuration will remain static.
4. OSASINFRA testing matrix:
    - Testing all the supported OCP releases for a given OSP release.
    - Testing all the supported NetworkTypes per OCP releases for a given OSP release (OVNKubernetes and OpenShiftSDN).
    - Testing supported installation types per OCP releases and NetworkType for a given OSP release (IPI, UPI, IPI-proxy, others)
5. A subset of testing can be selected to be run depending on the above combinations.

## Testing tree

| Test framework                        | Stage to run |  Test case to report |
| ------------------------------------- | ------------ |  ------------------- |
| Openshift Openstack-tests             | stage8       |  ReportPortal        |
| Openshift LB svc tests                | stage8       |  ReportPortal        |
| Openshift Cinder-CSI tests            | stage8       |  ReportPortal        |
| Openshift Manila-CSI tests            | stage8       |  ReportPortal        |
| Openshift Conformance Parallel tests  | stage6       |  ReportPortal        |
| Openshift Conformance Serial tests    | stage8       |  ReportPortal        |
| Openshift EgressIP tests              | stage8       |  ReportPortal        |
| Openshift CPMS tests                  | stage8       |  ReportPortal        |
| Openshift day2ops                     | stage8       |  ReportPortal        |

## Stages

All stages must be executed in the order listed below.  Everything is required unless otherwise indicated.

1. [Install dependencies for the OpenStack K8S operators](stage1)
2. [Install the OpenStack K8S operators](stage2)
3. [Configuring networking on the OCP nodes](stage3)
4. [Configure and deploy the control plane](stage4)
5. [Configure and deploy the initial data plane to prepare for CephHCI installation](stage5)
6. [Update the control plane and finish deploying the data plane after CephHCI has been installed](stage6)
7. [Install OCP Cluster](stage7)
8. [Execute testing](stage8)
9. [Destroy OCP Cluster](stage9)
10. [Move back to stage 7 and repeat with different configuration](stage10)

