# Deployed Topology - Nova/Nova01Alpha

Deploys a GPU with MDevs, SR-IOV NICs, and PCI in placement

## Purpose

This brings together a deployment that utilizes mulitiple hardware focused 
compute features. This includes the capacity the create guests with vGPU 
resources via MDev and support of PCI in placement.

## Environment

### Nodes

| Role              | Machine Type | Count |
| ----------------- | ------------ | ----- |
| Compact OpenShift | vm           |   3   |
| OpenStack Compute | vm           |   2   |


### Networks

| Name         | Type     | Interface | CIDR            |
| ------------ | -------- | --------- | --------------- |
| Provisioning | untagged | nic1      | 172.22.0.0/24   |
| Machine      | untagged | nic2      | 192.168.32.0/20 |
| RH OSP       | trunk    | nic3      |                 |


#### VLAN networks in RH OSP

| Name        | Type        | CIDR              |
| ----------- | ----------- | ----------------- |
| ctlplane    | untagged    | 192.168.122.0/24  |
| internalapi | VLAN tagged | 172.17.0.0/24     |
| octavia     | VLAN tagged | 172.23.0.0/24     |
| storage     | VLAN tagged | 172.18.0.0/24     |
| storagemgmt | VLAN tagged | 172.20.0.0/24     |
| tenant      | VLAN tagged | 172.19.0.0/24     |


### Services, enabled features and configurations

| Service          | configuration           | Lock-in coverage?  |
| ---------------- | ----------------------- | ------------------ |
| Barbican         | (default)               | Must have          |
| Cinder           | LVM/iSCSI/lioadm        | Must have          |
| Cinder Backup    | Swift                   | Must have          |
| Glance           | Swift                   | Must have          |
| Swift            | (default)               | Must have          |
| Horizon          | N/A                     | Must have          |
| Neutron          | Geneve (OVN)            | Must have          |
| Swift            | (default)               | Must have          |

#### Support services

The following table lists services which are not the main focus of the testing
(which may be covered by additional scenarios), but are required for the DT
to work properly and can be deployed with any/default configuration.

| Service          | Reason                     |
| ---------------- |--------------------------- |
| Keystone         | needed by all services     |


### Additional configuration

- Always-on, default services and features: TLSe

#### Nova

Enable PCI in placement and create an alias for the PCI device the operator 
wishes to passthrough to the guest.

```YAML
---
spec:
  nova:
    apiServiceTemplate:
      customServiceConfig: |
        [pci]
        alias = { "vendor_id":"8086", "product_id":"154d", "device_type":"type-PCI", "name":"a1" }
        [filter_scheduler]
        pci_in_placement = True
    cell0:
      conductorServiceTemplate:
        customServiceConfig: |
          [filter_scheduler]
          pci_in_placement = True
    cell1:
      conductorServiceTemplate:
        customServiceConfig: |
          [filter_scheduler]
          pci_in_placement = True
    schedulerServiceTemplate:
      customServiceConfig: |
        [filter_scheduler]
        enabled_filters = AvailabilityZoneFilter,ComputeFilter,ComputeCapabilitiesFilter,ImagePropertiesFilter,ServerGroupAntiAffinityFilter,ServerGroupAffinityFilter,PciPassthroughFilter,NUMATopologyFilter,AggregateInstanceExtraSpecsFilter
```

#### OSDPNS

Updates the traditional OSDPNS template with additional OSDPS nova-custom-sriov
to allow for the deployment of SR-IOV NICs as well as install the necessary
Nvidia Drivers for GPU and MDev.

```YAML
apiVersion: dataplane.openstack.org/v1beta1
kind: OpenStackDataPlaneNodeSet
metadata:
  name: openstack-edpm
  namespace: openstack
spec:
  services:
    - bootstrap
    - download-cache
    - configure-network
    - install-os
    - validate-network
    - configure-os
    - ssh-known-hosts
    - run-os
    - reboot-os
    - install-certs
    - libvirt
    - ovn
    - neutron-ovn
    - nova-custom-sriov
    - neutron-sriov
    - neutron-metadata
    - install-nvidia-mdev

```

## Stages
All stages must be executed in the order listed below. Everything is required
unless otherwise indicated.

1. [Install the OpenStack K8S operators and their dependencies](../../../common/)
2. [Configuring networking and deploy the OpenStack control plane](control-plane.md)
3. [Configure and deploy dataplane and finalize GPU installation](dataplane.md)