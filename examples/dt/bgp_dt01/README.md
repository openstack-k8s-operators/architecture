# RHOSO Deployed Topology - BGP DT01 - Kernel routing and OVN NB DB driver

This document describes the first BGP Deployed Topology (DT), used to test the
BGP Dynamic Routing functionality on Red Hat OpenStack Services on OpenShift
(RHOSO).

The CRs included within this DT should be applied on an environment where EDPM
and OCP nodes are connected through a spine/leaf network. The BGP protocol
should be enabled on those spine and leaf routers.

## Purpose

This first BGP DT (DT01) tests default BGP configuration:
* Kernel routing (instead of OVN routing)
* OVN NB DB driver (instead of OVN SB DB driver)

The OCP cluster consists on the following nodes:
* 3 OCP master nodes
* 3 OCP worker nodes
* 1 OCP worker node with special configuration (OCP tester node)

This DT creates an OCP cluster that includes both master and worker nodes,
instead of the usual master/worker combo nodes. The reason for this is to run
disruptive tests only on the OCP workers, which host the Openstack Control
Plane services, avoiding potential issues when OCP master nodes are disrupted
that would not be relevant when testing RHOSO high availability scenarios.

The extra OCP worker (OCP tester) is needed to run tests from it because:
* disruptive tests can be run from this worker on the other workers without
  affecting the test exection
* this worker is connected to the spine/leaf routers with a special routing
  configuration, so that it can reach the Openstack provider network
The OCP tester is configured so that only test pods (created by the
Openstack test-operator) run on it.

This DT configures both compute and networker EDPM nodes. So far, networker
nodes are needed when BGP is used on RHOSO, in order to expose routes to SNAT
traffic (OVN Gateway IPs). In other words, when RHOSO is used with BGP, the OCP
workers cannot be configured as OVN Gateways.

The OCP and EDPM nodes deployed with this DT are distributed into three
different racks. Each rack is connected to two leaves.
Hence, the distribution of the nodes in the racks is the following one:
* rack0: r0-compute-0, r0-networker-0, ocp-master-0, ocp-worker-0, leaf-0, leaf-1
* rack1: r1-compute-0, r1-networker-0, ocp-master-1, ocp-worker-1, leaf-2, leaf-3
* rack2: r2-compute-0, r2-networker-0, ocp-master-2, ocp-worker-2, leaf-4, leaf-5

The OCP tester (ocp-worker-3) is not included into any rack. It is not
connected to any leaves, but to a router connected to the spines, due to the
reasons described before (it needs special connectivity to reach the provider
network).

## Node topology
| Node role               | bm/vm | amount |
| ----------------------- | ----- | ------ |
| Openshift master nodes  | vm    | 3      |
| Openshift worker nodes  | vm    | 4      |
| Openstack Computes      | vm    | 3      |
| Openstack Networker     | vm    | 3      |
| Leaf routers            | vm    | 6      |
| Spine routers           | vm    | 2      |
| External routers        | vm    | 1      |
| Ansible Controller      | vm    | 1      |

### Networks

| Name                     | Type     | CIDR             |
| ------------------------ | -------- | ---------------- |
| Controlplane rack0       | untagged | 192.168.122.0/24 |
| Controlplane rack1       | untagged | 192.168.123.0/24 |
| Controlplane rack2       | untagged | 192.168.124.0/24 |
| Provider network         | untagged | 192.168.133.0/24 |
| RH OSP                   | untagged | 192.168.111.0/24 |
| edpm/ocp to left leaves  | untagged | 100.64.x.y/30    |
| edpm/ocp to right leaves | untagged | 100.65.x.y/30    |

## Services, enabled features and configurations

| Service          | configuration    | Lock-in coverage?  |
| ---------------- | ---------------- | ------------------ |
| Glance           | Swift            | Must have          |
| Swift            | (default)        | Must have          |
| Octavia          | (default)        | Must have          |
| Heat             | (default)        | Must have          |
| frr              | dataplane        | Must have          |
| ovn-bgp-agent    | dataplane        | Must have          |

## Considerations/Constraints

1. Virtual networks should be created to connect the nodes to the routers.
2. All the VMs that are neither Openstack nor Openshift nodes, i.e. those that
   act as routers, need to be properly configured in order to support the BGP
   protocol.
3. The spine/leaf topology separates the nodes into different L2
   network segments, called racks. Each rack includes two leaves, some OCP
   nodes and some EDPM nodes.
4. The Openstack services running on the EDPM nodes are installed using the BGP
   network, i.e. the Openstack services running on OCP nodes connect to the
   Openstack services running on EDPM nodes using BGP. There is no direct L2
   network connectivity between them. OCP version 4.18 or higher is required
   because the Openstack Operators use the frr-k8s feature for this and frr-k8s
   is not available in OCP 4.16.
5. Once Openstack is installed on them, both dataplane and controlplane
   connections are achieved using the BGP protocol.
6. Tests are executed from the OCP worker to verify external connectivity.

## Stages

All stages must be executed in the order listed below. Everything is required unless otherwise indicated.

1. [Configure taints on the OCP worker](configure-taints.md)
2. [Disable RP filters on OCP nodes](disable-rp-filters.md)
3. [Install the OpenStack K8S operators and their dependencies](../../../common/)
4. [Apply metallb customization required to run a speaker pod on the OCP tester node](metallb/)
5. [Configuring networking and deploy the OpenStack control plane](control-plane.md)
6. [Create BGPConfiguration after controplane is deployed](bgp-configuration.md)
7. [Configure and deploy the dataplane - networker and compute nodes](data-plane.md)
