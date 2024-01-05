# RHOSO Deployed Topology DFG-network-ovn-bgp-agent-18.0-basic_topology-ipv4-geneve

## General information
| Revision | Change                | Date             |
|--------: | :-------------------- | :--------------: |
| v0.1     | Initial publication   | 12.13.2023       |

## Node topology
| Node role                                     | bm/vm | amount |
| --------------------------------------------- | ----- | ------ |
| Openshift master/worker combo-node cluster    | vm    | 3      |
| Compute nodes                                 | vm    | 6      |
| Networker nodes                               | vm    | 3      |
| Leaf routers                                  | vm    | 6      |
| Spine routers                                 | vm    | 2      |
| External routers                              | vm    | 1      |
| External VMs                                  | vm    | 1      |
# TODO(eolivare): should the previous routers and extvm be part of that
# section, or only openstack and openshift nodes?

## Services, enabled features and configurations
| Service                                     | configuration                      | Lock-in coverage?  |
| ------------------------------------------- | ---------------------------------- | ------------------ |
| Neutron                                     | ML2/OVN                            | Must have          |
| Octavia                                     |                                    | Must have          |
| OVN-BGP-Agent                               |                                    | Must have          |
| FRR                                         | common ASN for all Openstack nodes | Must have          |
# TODO(eolivare): should ovn-bgp-agent and frr be included here? They are
# services that are only deployed on Compute and Networker nodes

## Considerations/Constraints
1. This job is based on a virtualized setup. Therefore, all nodes are VMs
   running on a common HV.
2. Virtual networks should be created to connect the VMs between them.
3. All the VMs that are neither Openstack nor Openshift nodes need to be
   properly configured in order to support the BGP protocol.

## Testing tree
| Test framework   | Stage to run | Special configuration                                                 | Test case to report      |
| ---------------- | ------------ | --------------------------------------------------------------------- | :----------------------: |
| Tempest/neutron  | stage9       | skips due to usupported features (multicast, FIP port-forwarding, etc)| scenario                 |
| Tempest/octavia  | stage9       |                                                                       | scenario                 |
| Tobiko/Faults    | stage10      |                                                                       | sanity, scenario, faults |

## Stages
All stages must be executed in the order listed below.  Everything is required unless otherwise indicated.
1. [Create and configure the virtual networks](stage1)
2. [Deploy and configure the Leafs, Spines, ExtRouter and ExtVM](stage2)
3. [Install dependencies for the OpenStack K8S operators](stage3)
4. [Install the OpenStack K8S operators](stage4)
5. [Configuring networking on the OCP nodes](stage5)
6. [Configure and deploy the control plane](stage6)
7. [Configure and deploy the initial data plane](stage7)
8. [Update the control plane and finish deploying the data plane](stage8)
9. [Execute non destructive testing](stage9)
10. [Execute HA testing](stage10)

