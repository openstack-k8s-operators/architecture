# Deployed Topology - ShiftStack

This document contains and overview about the deployment topology and the list
of tests used for evaluating the deployment. It also contains a collection of
custom resources (CRs) for deploying the test environment.

## Purpose

This topology is used for evaluating the deployment of OpenShift platforms using
OpenStack services running on OpenShift container platform.

## Environment

### Nodes

| Role               | Machine Type | Count |
| ------------------ |      :-:     |  :-:  |
| Compact OpenShift  | VM           | 3     |
| OpenStack Compute  | BM           | 1     |
| Ceph Storage       | VM           | 3     |

### Networks

| Name                       | Type     | Interface | CIDR            |
| ---                        | ---      |    :-:    | --------------- |
| OpenShift Machine Network  | untagged | nic2      | 10.46.22.128/26 |
| OpenStack Trunk Network    | trunk    | nic3      |                 |

#### Networks in OpenStack Trunk

| Name        | Type     | CIDR             |
| ---         |  :-:     |         :-:      |
| ctlplane    | untagged | 192.168.122.0/24 |
| internalapi | VLAN 120 | 172.17.0.0/24    |
| storage     | VLAN 121 | 172.18.0.0/24    |
| tenant      | VLAN 122 | 172.19.0.0/24    |
| storagemgmt | VLAN 123 | 172.20.0.0/24    |
| octavia     | VLAN 124 | 172.23.0.0/24    |

### OpenStack services

| Service       | Configuration          |
| ---           | ---                    |
| Cinder        | Backend - Ceph         |
| Cinder Backup | Backend - Ceph         |
| Glance        | Backend - Ceph         |
| Swift         | default                |
| Octavia       | Backend - amphora      |
| Manila        | Backend - NFS-Ganesha  |

#### Support services

| Service       | Reason                    |
| ---           | ---                       |
| Horizon       | needed by other services. |
| Keystone      | needed by all   services. |
| Nova          | needed by testing.        |
| Neutron       | needed by other services. |

## Workflow

1. [Install the OpenStack K8S operators and their dependencies](../../common/README.md)
2. [Configure and deploy the OpenStack control plane](control-plane.md)
3. [Configure and deploy Ceph nodes using EDPM](ceph.md)
4. [Configure and deploy the OpenStack data plane](data-plane.md)
