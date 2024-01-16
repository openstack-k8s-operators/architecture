# OpenStack SRIOV

**Based on OpenStack K8S operators from the "main" branch of the [OpenStack Operator repo](https://github.com/openstack-k8s-operators/openstack-operator/tree/12c57baeca4ae33dd30a7707d330eb094309b4cd) on Dec 6th, 2023**

This is a collection of CR templates that represent a validated Red Hat OpenStack Services on OpenShift deployment that has the following characteristics:

- 3 master/worker combo-node OpenShift cluster
- 3-replica Galera database
- RabbitMQ
- OVN networking
- Network isolation over a single NIC
- 2 compute nodes with an additional SRIOV-enabled NIC

## Considerations

1. These CRs are validated for the overall functionality of the OSP cloud deployed, but they nonetheless require customization for the particular environment in which they are utilized.  In this sense they are _templates_ meant to be consumed and tweaked to fit the specific constraints of the hardware available.

2. The CRs are applied against an OpenShift cluster in _stages_.  That is, there is an ordering in which each grouping of CRs is fed to the cluster.  It is _not_ a case of simply taking all CRs from all stages and applying them all at once.

3. In stages 1 and 2 [kustomize](https://kustomize.io/) is used to genereate the CRs dynamically. The `*-values.yaml` file(s) must be updated to fit your environment. kustomize version 5 or newer required.

4. In stage 3 YAML comments are placed throughout the CRs to aid in the process of customizing the CRs.  Fields that _must_ (or most likely need to be) changed are commented with "# CHANGEME" either on the field itself or somewhere nearby.  Other comments are added to explain fields that can be changed and, sometimes, to explain additions that can be made.

## Stages

All stages must be executed in the order listed below. Everything is required unless otherwise indicated.

1. [Install the OpenStack K8S operators and their dependencies](../../../common/)
2. [Configuring networking and deploy the OpenStack control plane](control-plane.md)
3. [Configure and deploy the data plane](edpm)
