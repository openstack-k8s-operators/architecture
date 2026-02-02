# Deployed Topology - Nova/Nova02Beta

This deployment takes advantage of multiple nodesets to allow for mixed GPU
environment consisting of vGPUs via MDevs and SR-IOV. This DT also allows for
the support of SR-IOV Nics, PCI in placement, and mixed CPU pinning 
configurations.


## Purpose

This allows for testing heterogeneous dataplanes via different nodeset 
configurations. These nodesets have different OpenstackDataplaneServices (OSDPS)
for the respective GPU hardware and also allows users to create different PCPU 
pinning schemes.

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
kind: OpenStackControlPlane
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
        pci_in_placement = True
```

#### OSDPNS

Create two custom OSDPS for each nodeset, both are responsible for installing
GPU services with one allowing for MDevs and the other using SR-IOV.

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
    - validate-network
    - install-os
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
---
apiVersion: dataplane.openstack.org/v1beta1
kind: OpenStackDataPlaneNodeSet
metadata:
  name: openstack-edpm-2
  namespace: openstack
spec:
  services:
    - bootstrap
    - download-cache
    - configure-network
    - validate-network
    - install-os
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
    - install-nvidia-sriov

```

#### Provider.yaml via ConfigMap

Create a ConfigMap that maps the resource providers with vGPU resources to
their respective traits.

```YAML
apiVersion: v1
kind: ConfigMap
metadata:
  name: edpm-provider-values
  annotations:
    config.kubernetes.io/local-config: "true"
data:
  nova:
    compute:
      provider: |
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

```

## Stages
All stages must be executed in the order listed below. Everything is required
unless otherwise indicated.

1. [Install the OpenStack K8S operators and their dependencies](../../../common/)
2. [Configuring networking and deploy the OpenStack control plane](control-plane.md)
3. [Configure and deploy dataplane, finalize GPU installation, and create provider.yaml](dataplane.md)