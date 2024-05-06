# BGP Basic configuration

This document describes the basic configuration that has been created to
support deploying Red Hat OpenStack Services on OpenShift using BGP Dynamic
routing.
This collection of CR templates will be extended to deploy RHOSO BGP Deployed
Topologies.
The BGP CRs should be applied on an environment where EDPM and OCP nodes are
connected through a spine/leaf network. The BGP protocol should be enabled on
those spine and leaf routers.

## Purpose

These CRs can be used to deploy a RHOSO environment with BGP, but its main
intention is to be the basic one that will be extended by the final RHOSO BGP
Deployed Topologies.

## Environment

### Nodes

| Role               | Machine Type | Count |
| ------------------ | ------------ | ----- |
| Compact OpenShift  | vm           | 3     |
| OpenStack Compute  | vm           | 3     |
| Ansible Controller | vm           | 1     |

### Networks

| Name                     | Type     | CIDR             |
| ------------------------ | -------- | ---------------- |
| Provisioning             | untagged | 192.168.122.0/24 |
| RH OSP                   | untagged | 192.168.111.0/24 |
| edpm/ocp to left leaves  | untagged | 100.64.x.y/30    |
| edpm/ocp to right leaves | untagged | 100.65.x.y/30    |

### Services, enabled features and configurations

| Service          | configuration    | Lock-in coverage?  |
| ---------------- | ---------------- | ------------------ |
| Glance           | Swift            | Must have          |
| Swift            | (default)        | Must have          |
| Octavia          | (default)        | Must have          |
| Heat             | (default)        | Must have          |
| frr              | dataplane        | Must have          |
| ovn-bgp-agent    | dataplane        | Must have          |

## Stages

All stages must be executed in the order listed below. Everything is required unless otherwise indicated.

1. [Install the OpenStack K8S operators and their dependencies](../../common/)
2. [Configuring networking and deploy the OpenStack control plane](control-plane.md)
3. [Configure and deploy the dataplane](dataplane.md)
