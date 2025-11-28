# Deployed Topology - NFV/OVS-DPDK-SRIOV with IPv6 and 2 nodesets

Deploys an OVS-DPDK-SRIOV environment with IPv6 as the primary IP stack and 2 different nodesets.
It is an extension of the regular OVS-DPDK-SRIOV scenario, so all information in that scenario is
valid here too. Check [OpenStack OVS DPDK SRIOV](../../../va/nfv/ovs-dpdk-sriov/README.md)

## Purpose

This scenario is needed when compute nodes used to deploy OpenStack dataplane
are different (different nics, cpu, memory, ...) so a different nodeset can
be created for each different compute node.

This DT is based on OVS-DPDK-SRIOV VA with two key additions:
- IPv6 networking: All control plane and data plane networks use IPv6 addresses (2620:cf:cf:XXXX::/64 subnets)
- Multiple nodesets: Configures 2 separate nodesets to support heterogeneous compute nodes

## Stages

All stages must be executed in the order listed below. Everything is required unless otherwise indicated.
Stages are the same than the OVS-DPDK-SRIOV scenario, the only difference is that it will
be created 2 nodesets instead of just 1

1. [Install the OpenStack K8S operators and their dependencies](../../../common/)
2. [Configuring networking and deploy the OpenStack control plane](control-plane.md)
3. [Configure and deploy the data plane](dataplane.md)


