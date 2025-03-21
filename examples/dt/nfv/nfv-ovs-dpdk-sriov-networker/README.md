# Deployed Topology - NFV/OVS-DPDK-SRIOV with Networker Nodeset

This DT is intended to deploy OVS-DPDK SRIOV setup with a compute nodeset and a
networker nodeset. It is an extension of the standard OVS-DPDK SRIOV scenario
(which only deploys a compute nodset).
Check [OpenStack OVS DPDK SRIOV](../../../va/nfv/ovs-dpdk-sriov/README.md).

## Purpose

This DT is based on OVS-DPDK VA and allows to deploy the standard scenario but
adding a networker nodeset to be able to run OVN composable services on
dedicated networker nodes.

## Stages

All stages must be executed in the order listed below. Everything is required
unless otherwise indicated.
The stages are the same as those in the OVS-DPDK SRIOV scenario. The only
difference is that a networker-nodeset will be deployed instead of just a
compute-nodeset.

1. [Install the OpenStack K8S operators and their dependencies](../../../common/)
2. [Configuring networking and deploy the OpenStack control plane](control-plane.md)
3. [Configure and deploy the data plane](dataplane.md)
