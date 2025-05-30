# Validated Architecture - Nvidia-Mdev

This document describes the CR's and deployment workflow to create an 
environment with EDPM Compute Nodes capable of supplying Nvidia mediated 
devices (Mdevs). Mdevs allow multiple guests to share the same physical GPU
card on the hypervisor. The deployment also takes advantage of defining and
mapping Custom Traits to different resource providers by passing definition via
provider.yaml through a ConfigMap.

## Purpose

This topology is used to primarily verify environments that provide Nvidia
Mdevs and confirm guests are able to take advantage of the resource correctly.
It should be noted that this type of deployment cannot be simulated with nested
virtualization and requires real baremetal hosts.

## Environment

### Nodes

| Role                        | Machine Type | Count |
| --------------------------- | ------------ | ----- |
| Compact OpenShift           | vm           | 3     |
| OpenStack Baremetal Compute | Baremetal    | 2     |

### Networks

| Name         | Type     | Interface | CIDR            |
| ------------ | -------- | --------- | --------------- |
| Provisioning | untagged | nic1      | 172.23.0.0/24   |
| Machine      | untagged | nic2      | 192.168.51.0/20 |
| RH OSP       | trunk    | nic3      |                 |


#### VLAN networks in RH OSP

| Name        | Type        | CIDR              |
| ----------- | ----------- | ----------------- |
| ctlplane    | untagged    | 192.168.122.0/24  |
| internalapi | VLAN tagged | 172.17.0.0/24     |
| storage     | VLAN tagged | 172.18.0.0/24     |
| storagemgmt | VLAN tagged | 172.20.0.0/24     |
| tenant      | VLAN tagged | 172.19.0.0/24     |

#### Nova Mdev Configuration

To deploy vGPU devices comprised of different types as well as the capacity to 
live migrate, define what mdev types should be enabled and map the respective
mdev types to their pci address(es). Example below using nivida-228 and
nvidia-229 as the types.

```YAML
---
apiVersion: v1
data:
  25-cpu-pinning-nova.conf: |
    [libvirt]
    live_migration_completion_timeout = 0
    live_migration_downtime = 500000
    live_migration_downtime_steps = 3
    live_migration_downtime_delay = 3
    live_migration_permit_post_copy = false
    [devices]
    enabled_vgpu_types=nvidia-228,nvidia-229
    [vgpu_nvidia-228]
    device_addresses=0000:82:00.0
    [vgpu_nvidia-229]
    device_addresses=0000:04:00.0
kind: ConfigMap
metadata:
  name: cpu-pinning-nova
  namespace: openstack
```

#### Openstack Dataplane Composable Service

An Openstack Dataplane service can used to customize how the GPU cards need to
be installed on the EDPM nodes. An example of OSPDS service can be seen
[here](../../../va/nvidia-mdev/edpm/nodeset/nova_sriov.yaml). With the OSDPS
configured, the operator would need to make sure to include the service to the
list of services for the Openstack Dataplane NodeSet.

**Note:** The example listed is not an officially supported procedure for
installing Nvidia GPU's in RHOSO and is meant to be purely an example of how
to leverage OSDPS. Please reference Nvidia's documentation when creating a
procedure to install GPU's.

#### Provider.yaml

In order to easily take advantage of multiple Mdev types in an environment when
creating flavors, we can associate traits to specific resource providers. With
provider.yaml we can map those traits and apply them as part of a deployment.
An example definition can be found [here](edpm-post-driver/nodeset/values.yaml)
that associates different custom traits to different RPs.

## Stages
All stages must be executed in the order listed below. Everything is required
unless otherwise indicated.

1. [Install the OpenStack K8S operators and their dependencies](../../common/)
2. [Configuring networking and deploy the OpenStack control plane](control-plane.md)
3. [Configure and deploy the initial dataplane](edpm-pre.md)
4. [Update Dataplane to reboot EDPM nodes and optionally apply provider.yaml](edpm-post.md)
