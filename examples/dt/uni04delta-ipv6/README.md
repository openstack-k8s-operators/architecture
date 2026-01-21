# Unified Delta Deployed topology (IPv6)

** This DT is Work-in-Progress **

This document contains a list of integration test suites that would
be executed against the below specified topology of Red Hat OpenStack Services
on OpenShift. It also has a collection of custom resources (CRs).

## Purpose

This topology is used for executing integration tests that evaluate Cinder
and Manila OpenStack services configured with Ceph.

## Environment

### Node

| Role | Machine Type | Count |
| ---- | ------------ | ----- |
| Compact OpenShift | vm | 3 |
| OpenStack Compute | vm | 2 |
| OpenStack EDPM Ceph Nodes | vm | 3 |

### Networks

#### OpenShift and OpenStack Computes

| Name | Type | Interface |
| ---- | ---- | --------- |
| Provisioning | untagged | nic1 |
| Machine | untagged | nic2 |
| RH OSP | trunk | nic3 |

##### Networks in RH OSP

| Name | Type |
| ---- | ---- |
| Ctlplane | untagged |
| Internal-api | VLAN tagged |
| Storage | VLAN tagged |
| Tenant | VLAN tagged |
| StorageManagement | VLAN tagged |
| ironic | untagged |
| octavia | VLAN tagged |

### Services, enabled features and configurations

| Service          | configuration   | Lock-in coverage?  |
| ---------------- | --------------- | ------------------ |
| Cinder           | Ceph            | Must have          |
| Cinder Backup    | Ceph            | Must have          |
| Glance           | Ceph            | Must have          |
| Manila           | NFS ganesha     | Must have          |
| RGW as Swift     | ---             | Must have          |
| Horizon          | N/A             | Must have          |
| Barbican         |                 | Must have          |
| Ironic           |                 | Must have          |
| Telemetry        |                 | Must have          |
| Octavia          |                 | Must have          |

#### Support services

The following table lists services which are not the main focus of the testing
(which may be covered by additional scenarios), but are required for the DT to
work properly and can be deployed with any/default configuration.

| Service          | Reason  |
| ---------------- |------------------ |
| Neutron          | needed by other services   |
| Nova             | needed by scenario testing |
| Keystone         | needed by all services     |
| Ceilometer       | needed by Telemetry        |
| Heat             | needed by Telemetry        |
| Prometheus       | needed by Telemetry        |

#### Additional configuration

- Default settings: TLSe
- Cluster Observability Operator is installed on the platform.

##### Octavia

Octavia is enabled with the appropriate network attachments configured to
deploy Octavia. It manages amphorae VMs through a self-service tenant network.
The Octavia Amphora controllers get access to it through a Neutron externally
routed flat provider network configured as a SNAT-less gateway for a neutron
router linked to the tenant networks. Host routes on the tenant network's
subnet and routes on the network attachment provide the required `next hop`
routing to establish the necessary bidirectional routing.

This arrangement requires a network attachment for connecting the OVN and
Amphora Controller pods (octavia-housekeeping, octavia-healthmanager,
octavia-worker). Because Neutron ML2/OVN implements provider networks by
bridging the relevant physical interface - in this case the network-attachment,
there is an additional requirement that this attachment function when
bridged. As the default macvlan attachments do not function when bridged, a
bridge network attachment is used.

Bridge attachments do not directly provide connectivity outside of the OCP
node. To implement this, the NodeNetworkConfigurationPolicy creates an VLAN
interface as is typical for the other networks, but does not configure an IP
pool as it is not needed. It is also not configured for metallb as it is solely
as part of a way to establish a L2 network link between nodes. The
NodeNetworkConfigurationPolicy also configures an octbr linux bridge which is
configured as the bridge for the network attachment mentioned above. It is also
configured to add the VLAN interface as a port, effectively linking the nodes
and the network attachments.

```YAML
spec:
  octavia:
    enabled: true
    template:
      octaviaAPI:
        networkAttachments:
          - internalapi
      octaviaHousekeeping:
        networkAttachments:
          - octavia
      octaviaWorker:
        networkAttachments:
          - octavia
      octaviaHealthManager:
        networkAttachments:
          - octavia

  ovn:
    template:
      ovncontroller:
        nicMappings:
          datacentre: ospbr
          octavia: octbr
```

## Considerations/Constraints

N/A

## Testing

| Test framework   | When to run          | Special configuration |
| ---------------- | -------------------- | ----------------------|
| relevant volume tests | tempest stage |           |
| relevant image tests  | tempest stage |           |
| relevant manila tests | tempest stage |           |
| relevant object-storage tests  | tempest stage |           |
| relevant designate tests | tempest stage |           |
| horizon integration   | own stage (post-tempest)|           |
| ironic integration    | tempest stage |           |

## Workflow

1. [Install the OpenStack K8S operators and their dependencies](../../common/)
2. [Configure and deploy the OpenStack control plane](control-plane.md)
3. [Configure and deploy Ceph](edpm-pre-ceph.md)
4. [Configure and deploy the OpenStack data plane](edpm.md)
