# Validated Architecture - Nvidia GPU Passthrough (VFIO)

This document describes the CR's and deployment workflow to create an
environment with EDPM Compute Nodes capable of supplying Nvidia GPUs via
passthrough (VFIO). This setup allows entire physical GPUs on compute nodes to
be passed directly to virtual machines, providing near-native performance.

## Purpose

This topology is used to primarily verify environments that provide Nvidia GPU
passthrough and confirm guests are able to take advantage of the resource
correctly. It should be noted that this type of deployment cannot be simulated
with nested virtualization and requires real baremetal hosts.

## Environment

### Nova

# FIXME: this looks only used in PCI groups in placement? The same pci_passthrough:alias should be used in both cases it seems?
Nova control plane is configured for requesting PCI devices from Placement
by setting `resources:VGPU=X` in flavor extra specs.
That is a contrary to the legacy mode where PCI devices used to be requested through
`pci_passthrough:alias` flavor extra specs.

### Guest VM

To use the passthrough GPU, the guest operating system inside the VM must have
the appropriate native NVIDIA driver installed. You will need a standard NVIDIA
driver. Do not use vGPU-enabled guest drivers. The GPU will appear as a physical
PCI device within the guest.

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

NOTE: A network attach definition is not provided for storagemgmt because only
RHEL EDPM nodes are going to use it, while control plane pods on OpenShift do
not need it.

## Stages
All stages must be executed in the order listed below. Everything is required unless otherwise indicated.

1. [Install the OpenStack K8S operators and their dependencies](../../common/)
2. [Configuring networking and deploy the OpenStack control plane](control-plane/README.md)
3. [Configure and deploy the initial dataplane](data-plane-pre.md)
4. [Update Dataplane with a reboot](data-plane-post.md)
