# Deployed Topology - Zeta

This document contains a list of integration test suites that would be
executed against the below specified topology of Red Hat OpenStack Services
on OpenShift. It also contains a collection of custom resources (CRs) for
deploying the test environment.

## Purpose

Focused on components with a bit of heterogeneous configuration (please see below).

## Environment

### Nodes


## Node topology
| Node role                                        | bm/vm | amount |
| ------------------------------------------------ | ----- | ------ |
| Openshift master/worker combo-node cluster       | vm    | 3      |
| Compute nodes                                    | vm    | 2      |
| HCI Ceph (TBD, see below)                        | vm    | -      |

### Networks

| Name | Type | Interface |
| ---- | ---- | --------- |
| Provisioning | untagged | nic1 |
| Machine | untagged | nic2 |
| RH OSP | trunk | nic3 |

#### Networks in RH OSP

| Name | Type |
| ---- | ---- |
| ctlplane | untagged |
| internalapi | VLAN tagged |
| Storage | VLAN tagged |
| Tenant | VLAN tagged |

### Services, enabled features and configurations

| Service          | configuration             | Lock-in coverage?  |
| ---------------- | ------------------------- | ------------------ |
| Cinder           | nvemof-tcp / lvm          | Must have          |
| Cinder Backup    | Swift/S3/zstd             | Must have          |
| Glance           | Swift                     | Must have          |
| Swift            | (default)                 | Must have          |
| Octavia          | (ovn)                     | Must have          |
| Horizon          | N/A                       | Must have          |
| Barbican         | (default)                 | Must have          |
| Neutron          | OVN/no-dvr/provider_vlans | Must have          |

#### Support services

The following table lists services which are not the main focus of the testing
(which may be covered by additional scenarios), but are required for the DT to
work properly and can be deployed with any/default configuration.

| Service          | Reason                     |
| ---------------- |--------------------------- |
| Barbican         | needed by other services   |
| Neutron          | needed by other services   |
| Nova             | needed by scenario testing |
| Swift            | needed by scenario testing |
| Keystone         | needed by all services     |

### Additional configuration

- Always-on, default services and features: TLSe
- Logical volume with the name cinder-volumes exists on a OpenShift node.
- The S3 backend for cinder-backup requires a valid S3 implementation, which could be provided by HCI Ceph services or by Swift, if Swift can be deployed first.
cinder-backup expected to compress the backups.

#### Cinder backend - LVM

It is assumed that worker nodes or the master nodes have extra disks(or loopack device)
and there exists a logical volume group with the name *cinder-volumes*. If not, a
for example a `MachineConfig` can be used to create one.

The LVM backend for Cinder is a special case as the storage data is on the
OpenShift node and has no external storage systems. The target ips are not managed by
the operators, recommended to create dedicated label for each target serving node
and configure the storage ips of each cinder-volume instance with LVM backend.


#### Octavia

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

## Testing tree

| Test framework   | When to run          | Special configuration |
| ---------------- | -------------------- | ----------------------|
| relevant volume tests | tempest stage |           |
| relevant image tests  | tempest stage |           |
| relevant object-storage tests  | tempest stage |           |
| relevant networking tests | tempest stage | full CentOS/RHEL image  |
| horizon integration   | own stage (post-tempest)|           |

## Additional steps

In case you are testing on a single hypervisor,  the hypervisor routing interface should be configured using `ip` and `iptables`:
```bash
ip link add link osp_trunk name vlan218 type vlan id 218
ip addr add 172.38.0.1/24 dev vlan218
ip link set dev vlan218 up
iptables -A POSTROUTING -s 172.38.0.0/24 ! -d 172.38.0.0/24 -j MASQUERADE -t nat
```

You also need to setup cinder backup bucket/container,
This is just example, you might want to choose a non admin user.
```bash
oc rsh -n openstack openstackclient openstack container create volumebackups
oc rsh -n openstack openstackclient openstack credential create --type ec2 --project admin admin '{"access": "example", "secret": "example"}'
```

## Workflow

1. [Install the OpenStack K8S operators and their dependencies](../../common/README.md)
2. [Configure and deploy the OpenStack control plane](control-plane.md)
3. [Configure and deploy the OpenStack data plane](data-plane.md)
