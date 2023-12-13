# RHOSO Deployed Topology - BGP using OVN routing and OVN NB DB driver

## General information
| Revision | Change                | Date             |
|--------: | :-------------------- | :--------------: |
| v0.1     | Initial publication   | 2024-01-12       |

## Node topology
| Node role                                     | bm/vm | amount |
| --------------------------------------------- | ----- | ------ |
| Openshift master/worker combo-node cluster    | vm    | 3      |
| Compute nodes                                 | vm    | 3      |
| Networker nodes                               | vm    | 3      |
| Leaf routers                                  | vm    | 6      |
| Spine routers                                 | vm    | 2      |
| External routers                              | vm    | 1      |
| External VMs                                  | vm    | 1      |

## Services, enabled features and configurations
| Service                                     | configuration                                                                                  | Lock-in coverage?  |
| ------------------------------------------- | ---------------------------------------------------------------------------------------------- | ------------------ |
| Neutron                                     | ML2/OVN, DVR disabled                                                                          | Must have          |
| Octavia                                     |                                                                                                | Must have          |
| OVN-BGP-Agent                               | ovn-routing, nbdb-driver expose-tenant-networks enabled, sync-interval default value           | Must have          |
| FRR                                         | different ASN per rack, IP-level BGP peers                                                     | Must have          |

## Considerations/Constraints
1. Virtual networks should be created to connect the VMs between them.
2. All the VMs that are neither Openstack nor Openshift nodes need to be
   properly configured in order to support the BGP protocol.
3. The spine/leaf topology separates the overcloud nodes into different L2
   network segments, called racks. Each rack includes one compute, one
   networker and two leafs.
4. A separate provisioning network is necessary to install Openstack on those
   nodes.
5. Once Openstack is installed on them, controlplane and dataplane connectivity
   between them and with external machines (extvm) is achieved using the BGP
   protocol.
6. Tests are executed from the extvm machine, in order to verify external
   connectivity.

## Testing tree
| Test framework           | Stage to run | Special configuration                                                 | Test case to report      |
| ------------------------ | ------------ | --------------------------------------------------------------------- | :----------------------: |
| Tempest/neutron+octavia  | stage 5      | skips due to usupported features (multicast, FIP port-forwarding, etc)| scenario                 |
| Tobiko/Faults            | stage 6      |                                                                       | sanity, scenario, faults |

## Stages
All stages must be executed in the order listed below.  Everything is required unless otherwise indicated.
1. [Pre-deployment: create virtual networks, virtual routers and nodes](bgp-pre-deplyment.md)
2. [Install the OpenStack K8S operators and their dependencies](../../common/)
3. [Configure networking and deploy the Openstack control plane](bgp-control-plane.md)
4. [Configure and deploy the data plane](bgp-data-plane)
5. [Execute non destructive testing](bgp-tempest.md)
6. [Execute HA testing](bgp-tobiko.md)
