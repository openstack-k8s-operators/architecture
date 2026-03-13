# Deployed Topology - Nova/Nova03Gamma

Allows for a purely virtualized Nova focused deployment with additional
emulated devices.

## Purpose

This provides a compute focused deployment that can be fully virtualized.
Unlike Nova01,02,04 that all rely on having baremetal computes, this DT can be 
deployed without the need of real computes.

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
  nova:
    apiServiceTemplate:
      customServiceConfig: |
        [pci]
        alias = {"name": "usb_passthrough", "vendor_id":"abcd", "product_id":"000a"}
        [filter_scheduler]
        pci_in_placement = True
        [quota]
        driver = nova.quota.UnifiedLimitsDriver
        [oslo_limit]
        endpoint_id = abc123
    cell0Conductor:
      customServiceConfig: |
        [pci]
        alias = {"name": "usb_passthrough", "vendor_id":"abcd", "product_id":"000a"}
        [filter_scheduler]
        pci_in_placement = True
        [quota]
        driver = nova.quota.UnifiedLimitsDriver
        [oslo_limit]
        endpoint_id = abc123
    cell1Conductor:
      customServiceConfig: |
        [pci]
        alias = {"name": "usb_passthrough", "vendor_id":"abcd", "product_id":"000a"}
        [filter_scheduler]
        pci_in_placement = True
        [quota]
        driver = nova.quota.UnifiedLimitsDriver
        [oslo_limit]
        endpoint_id = abc123
    schedulerServiceTemplate:
      customServiceConfig: |
        [filter_scheduler]
        pci_in_placement = True
```

#### OSDPNS

Nothing major needs to be udpated for OSDPNS, but nova.compute.conf can be used  
to define pci passthrough information.

```YAML

nova:
  compute:
    conf: |
      [compute]
      cpu_dedicated_set=0,1,4,5
      cpu_shared_set=2,6
      [libvirt]
      cpu_mode = custom
      cpu_models = Nehalem
      cpu_model_extra_flags = vme,+ssse3,-mmx
      rx_queue_size = 1024
      cpu_power_management = true
      [pci]
      device_spec = {"address": "0000:0x:00.0", "vendor_id":"abcd", "product_id":"000a"}
      alias = {"name": "usb_passthrough", "vendor_id": "abcd", "product_id": "000a", "device_type": "type-PCI"}
      report_in_placement = True
```

## Stages
All stages must be executed in the order listed below. Everything is required
unless otherwise indicated.

1. [Install the OpenStack K8S operators and their dependencies](../../../common/)
2. [Configuring networking and deploy the OpenStack control plane](control-plane.md)
3. [Configure and deploy dataplane with compute overwrites](dataplane.md)