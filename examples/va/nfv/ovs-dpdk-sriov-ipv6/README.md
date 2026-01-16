# Validated Architecture - NFV/OVS-DPDK-SRIOV with IPv6

Deploys an OVS-DPDK-SRIOV environment with IPv6 as the primary IP stack. It is an extension
of the regular OVS-DPDK-SRIOV scenario, so all information in that scenario is
valid here too. Check [OpenStack OVS DPDK SRIOV](../ovs-dpdk-sriov/README.md)

## Purpose

This scenario extends the standard OVS-DPDK-SRIOV VA to support IPv6 networking.
All OpenStack control plane and data plane networks are configured with IPv6 addresses
(using 2620:cf:cf:XXXX::/64 subnets). This scenario deploys a single nodeset with
OVS-DPDK and SR-IOV enabled compute nodes.

This VA is based on the standard OVS-DPDK-SRIOV scenario with IPv6-specific network
configuration added in the NNCP and service values

## Stages

All stages must be executed in the order listed below. Everything is required unless otherwise indicated.
Stages are the same than the OVS-DPDK-SRIOV scenario, the only difference is that it will
be created 2 nodesets instead of just 1

1. [Install the OpenStack K8S operators and their dependencies](../../../common/)
2. [Configuring networking and deploy the OpenStack control plane](control-plane.md)
3. [Configure and deploy the data plane](dataplane.md)


