# Deployed Topology 

**Based on OpenStack K8S operators from the "main" branch of the [OpenStack Operator repo](https://github.com/openstack-k8s-operators/openstack-operator/)**


## Purpose

When new users first approach OpenStack as a project, they are presented with a vast and wonderful array of choices of components they could choose to begin with. This array is so vast and wonderful that it becomes really hard for people to understand where to start, be confident that the decisions they make will not prevent them from deploying something usable, and ensure they are able to expand the scope of their OpenStack over time. This deployment topology intends to define the smallest subset of projects that allow the user to provide a cloud capable of booting a VM. This is ideal for CI workloads, development clusters, small edge or business clusters with limited resources, or as a building block for more complex topologies. This deployment topology will be used as the minimal smoke test for promoting compute components.

## Node topology
| Node role                                       | bm/vm | amount |
| ------------------------------------------------| ----- | ------ |
| Openshift master/worker combo-node cluster (CRC)| vm    | 1      |
| Compute nodes                                   | vm    | 2      |



## Services, enabled features and configurations

| Service                                     | configuration                   | Lock-in coverage?  |
| ------------------------------------------- | ------------------------------- | ------------------ |
| RabbitMQ                                    | default                         | Must have          |
| OVN                                         | default                         | Must have          |
| galara                                      | default                         | Must have          |
| Glance                                      | filestore                       | Must have          |
| Keystone                                    | default                         | Must have          |
| placement                                   | default                         | Must have          |
| nova                                        | default                         | Must have          |
| neutron                                     | default                         | Must have          |

No other services should be added to this deployment topology as it's important that this model the minimum set of services that are required to provide the ability to boot a VM.

### Support services

Additional services required for integration testing that may not be the subject of this DT

| Service  | Reason                                            |
| -------- | ------------------------------------------------- |
| tempest  | validation fo basic functionality                 |
| whitebox | validation of non hardware specific functionally  |
| FIPS     | Enabled by default                                |

### Additional configuration

The DT crs will use the defaults for most services.
As a result, we shall likely create two job variants:
one using the defaults
    anonymous memory
    images-type=qcow
    FIPS enabled
    TLS-E enabled
hugepages and file-backed memory are mutually exclusive so we will
use this DT to test file-backed memory in a variant job.
Nova may use images-type=flat with force_raw_images=true.

As a result, we shall likely create two job variants:
one using the defaults:
    anonymous memory
    images-type=qcow
    FIPS enabled
    TLS-E enabled
    neither cpu_shared_set nor cpu_dedicated_set defined (CPU pinning unsupported)
    hugepages
and the other with the overrides described below:
    file-backed memory
    images-type=flat
    force_raw_images=true
    FIPS disabled
    TLS-E disabled
    cpu_shared_set and cpu_dedicated_set defined (CPU pinning supported)

## Constraints and Considerations

No additional OpenStack services can be added to this DT and it cannot be combined with others.
This job will be capable of testing block-based live migration with local non-shared storage.
As such, other DTs will not need to duplicate that testing and can cover block-based shared storage
migration and nova-provisioned Ceph storage. Ceph and Cinder are intentionally not part of this DT
as it is not required to meet the definition of the minimal set of services required to boot
a usable VM. As such, this DT will not test interaction with the Cinder service.
Similarly, Barbican integration, which is required for vTPM, is not tested in this DT as it
is also out of scope. Barbican and Cinder integration should be tested in other compute
or common DTs.


## Testing tree

| Test framework   | Stage to run | Special configuration | Test case to report |
| ---------------- | ------------ | --------------------- | :-----------------: |
| Tempest/compute  | stage5       | Use cirros image      | N/A                 |
| Tempest/scenairo | stage5       | Use cirros image      | N/A                 |
| Tempest/whitebox | stage5       | applicable subset     | N/A                 |

## Stages

All stages must be executed in the order listed below.  Everything is required unless otherwise indicated.

1. [Install dependencies for the OpenStack K8S operators](stage1)
2. [Install the OpenStack K8S operators](stage2)
3. [Configuring networking on the OCP nodes](stage3)
4. [Configure and deploy the control plane](stage4)
7. [Execute testing](stage5)
