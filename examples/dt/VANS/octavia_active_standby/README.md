# Deployed Topology VANS/octavia-active-standby

## General information

| Revision | Change                |    Date    |
|--------: | :-------------------- |:----------:|
| v0.1     | Initial publication   | 2024-04-05 |

## Purpose

This DT will test Octavia when running with Active/Standby topology

## Node topology
| Node role                                     | bm/vm | amount |
| --------------------------------------------- | ----- |--------|
| Openshift master/worker combo-node cluster    | vm    | 3      |
| Compute nodes                                 | vm    | 3      |

## Services, enabled features and configurations
| Service   | configuration              | Lock-in coverage? |
|-----------|----------------------------|-------------------|
| RabbitMQ  | default                    | Must have         |
| Neutron   | ML2/OVN, Geneve            | Must have         |
| Glance    | default                    | Must have         |
| Placement | default                    | Must have         |
| Keystone  | default                    | Must have         |
| OVN       | octavia NIC mapping        | Must have         |
| Nova      | default                    | Must have         |
| Redis     | default                    | Must have         |

### Additional information

Octavia is disabled by default in the openstack operator so it must be enabled,
with the appropriate network attachments configured to deploy Octavia. Also
`active-standby` is enabled by setting the `loadbalancer_topology`
configuration in the `controller_worker` section of the configuration for the
worker, health manager and housekeeping services.

e.g.:
    octavia:
      enabled: true
      template:
        octaviaAPI:
          networkAttachments:
            - internalapi
        octaviaHousekeeping:
          networkAttachments:
            - octavia
          customServiceConfig: |
            [controller_worker]
            loadbalancer_topology=ACTIVE_STANDBY
        octaviaWorker:
          networkAttachments:
            - octavia
          customServiceConfig: |
            [controller_worker]
            loadbalancer_topology=ACTIVE_STANDBY
        octaviaHealthManager:
          networkAttachments:
            - octavia
          customServiceConfig: |
            [controller_worker]
            loadbalancer_topology=ACTIVE_STANDBY

#### NetworkAttachmentDefinition and NodeNetworkConfigurationPolicy

Octavia manages amphorae VMs through a self-service tenant network. The Octavia
Amphora controllers get access to it through a Neutron externally routed flat
provider network configured as a SNAT-less gateway for a neutron router linked
to the tenant networks. Host routes on the tenant network's subnet and routes
on the network attachment provide the required `next hop` routing to establish
the necessary bidirectional routing.

This arrangement requires a network attachment for connecting the OVN and
Amphora Controller pods (octavia-housekeeping, octavia-healthmanager,
octavia-worker). Because Neutron ML2/OVN implements provider networks by
bridging the relevant physical interface - in this case the network-attachment
- there is an additional requirement that this attachment function when
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

#### OVN
Add the octavia network attachment to the ovncontroller.nicMappings.

e.g.:
  ovn:
    template:
      ovncontroller:
        nicMappings:
          - datacentre: ospbr
          - octavia: octbr

#### Redis
Redis is disabled by default and must be enabled. The default configuration is sufficient.

e.g.:
  redis:
    enabled: true

## Testing tree
Tempest and Tobiko

| Test framework         | Stage to run | Special configuration | Test case to report |
|------------------------| ------------ |-----------------------|:-------------------:|
| Tempest/octavia        | stage7       | Use Cirros image      |      11223344       |
| Tobiko/octavia-faults  | stage9       | Use Ubuntu image      |      33445566       |

## Stages

All stages must be executed in the order listed below.  Everything is required unless otherwise indicated.

1. [Install dependencies for the OpenStack K8S operators](stage1)
2. [Install the OpenStack K8S operators](stage2)
3. [Configuring networking on the OCP nodes](stage3)
4. [Configure and deploy the control plane](stage4)
5. [Configure and deploy the initial data plane to prepare for CephHCI installation](stage5)
6. [Update the control plane and finish deploying the data plane after CephHCI has been installed](stage6)
7. [Execute non destructive testing](stage7)
8. [Execute load testing](stage8)
9. [Destructive testing](stage9)

