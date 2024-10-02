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
live migrate, you would need the below configuration applied to Nova.

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

#### Provider.yaml

In order to easily take advantage of multiple Mdev types in an environment when
creating flavors, we can associate traits to specific resource providers. With
provier.yaml we can map those traits and apply them as part of a deployment.

```YAML
---
apiVersion: v1
data:
  provider.yaml: |
    meta:
      schema_version: "1.0"
    providers:
      - identification:
          name: edpm-compute-0.ctlplane.example.com_pci_0000_04_00_0
        traits:
          additional:
            - CUSTOM_NVIDIA_229
      - identification:
          name: edpm-compute-0.ctlplane.example.com_pci_0000_82_00_0
        traits:
          additional:
            - CUSTOM_NVIDIA_228
      - identification:
          name: edpm-compute-1.ctlplane.example.com_pci_0000_04_00_0
        traits:
          additional:
            - CUSTOM_NVIDIA_229
      - identification:
          name: edpm-compute-1.ctlplane.example.com_pci_0000_82_00_0
        traits:
          additional:
            - CUSTOM_NVIDIA_228
kind: ConfigMap
  name: compute-provider
  namespace: openstack
---
apiVersion: dataplane.openstack.org/v1beta1
kind: OpenStackDataPlaneService
metadata:
  name: compute-provider
  namespace: openstack
spec:
  addCertMounts: false
  caCerts: combined-ca-bundle
  dataSources:
  - configMapRef:
      name: compute-provider
  - configMapRef:
      name: cpu-pinning-nova
  - configMapRef:
      name: sriov-nova
  - secretRef:
      name: nova-cell1-compute-config
  - secretRef:
      name: nova-migration-ssh-key
  edpmServiceType: nova
  playbook: osp.edpm.nova
  tlsCerts:
    default:
      contents:
      - dnsnames
      - ips
      issuer: osp-rootca-issuer-internal
      networks:
      - ctlplane
---
apiVersion: dataplane.openstack.org/v1beta1
kind: OpenStackDataPlaneDeployment
metadata:
  name: edpm-deployment-post-driver
  namespace: openstack
spec:
  ansibleExtraVars:
    edpm_reboot_strategy: force
  nodeSets:
  - openstack-edpm
  preserveJobs: true
  servicesOverride:
  - reboot-os
  - compute-provider
```

## Stages
All stages must be executed in the order listed below. Everything is required unless otherwise indicated.

1. [Install the OpenStack K8S operators and their dependencies](../../common/)
2. [Configuring networking and deploy the OpenStack control plane](control-plane.md)
3. [Configure and deploy the initial dataplane](edpm-pre.md)
4. [Update Dataplane to deploy necessary vGPU MDev requirements](edpm-post.md)
