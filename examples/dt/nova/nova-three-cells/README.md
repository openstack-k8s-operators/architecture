# Deployed Topology - Nova/Three Cells

Deploys an environment with three cells instead of the standard two cells

## Purpose

Focused on leveraging multiple nodesets to deploy two distinct cells 
(cell1 and cell2) in addition to cell0. Compute-0 is allocated
to cell1 and compute-1 will be placed in cell2.

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
- Two additional compute nodes

#### Nova

Increase default cells to include cell2

```YAML
---
spec:
  nova:
    template:
      secret: osp-secret
      cellTemplates:
        cell0:
          cellDatabaseAccount: nova-cell0
          cellDatabaseInstance: openstack
          cellMessageBusInstance: rabbitmq
          conductorServiceTemplate:
            replicas: 3
          hasAPIAccess: true
        cell1:
          cellDatabaseAccount: nova-cell1
          cellDatabaseInstance: openstack-cell1
          cellMessageBusInstance: rabbitmq-cell1
          conductorServiceTemplate:
            replicas: 3
          hasAPIAccess: true
        cell2:
          cellDatabaseAccount: nova-cell2
          cellDatabaseInstance: openstack-cell2
          cellMessageBusInstance: rabbitmq-cell2
          conductorServiceTemplate:
            replicas: 3
          hasAPIAccess: true
```

#### RabbitMQ

Add a new rabbitmq service for cell2

```YAML
---
spec:
  rabbitmq:
    templates:
      rabbitmq-cell2:
        replicas: 3
```

#### Galera

Create a third galera service for cell2

```YAML
spec:
 galera:
    templates:
      openstack-cell2:
        storageClass: lvms-local-storage
        storageRequest: 5G
        secret: osp-secret
        replicas: 3
```

#### OSDPNS

Create a second nodeset that references a new compute service an necessary
secret/transport url for cell2

```YAML
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
  - install-os
  - validate-network
  - configure-os
  - ssh-known-hosts
  - run-os
  - reboot-os
  - install-certs
  - ovn
  - neutron-metadata
  - libvirt
  - nova-cell-2

apiVersion: dataplane.openstack.org/v1beta1
kind: OpenStackDataPlaneService
metadata:
  name: nova-cell-2
  namespace: openstack
spec:
  addCertMounts: false
  caCerts: combined-ca-bundle
  containerImageFields:
  - NovaComputeImage
  - EdpmIscsidImage
  dataSources:
  - secretRef:
      name: nova-cell2-compute-config
  - secretRef:
      name: nova-migration-ssh-key
  - configMapRef:
      name: nova-extra-config
      optional: true
  edpmServiceType: nova
  playbook: osp.edpm.nova

```
