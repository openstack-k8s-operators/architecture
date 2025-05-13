# Dual OpenStack deployments in separate namespaces

**Based on OpenStack K8S operators from the "main" branch of the [OpenStack Operator repo](https://github.com/openstack-k8s-operators/openstack-operator/commit/b0944fc30a9387cf41d019165c5dbc6a8f128597) on Apr 25th, 2025**

This is a collection of CR templates that represent a validated Red Hat OpenStack Services on OpenShift deployment that has the following characteristics:

- 3 master/worker combo-node OpenShift cluster
- 2 OSP control and data plane deployments (2 separate clouds in different namespaces)

Per cloud:

- 3-replica Galera database
- RabbitMQ
- OVN networking
- Network isolation over a single NIC
- 3 compute nodes

## Considerations

1. These CRs are validated for the overall functionality of the OSP cloud deployed, but they nonetheless require customization for the particular environment in which they are utilized.  In this sense they are _templates_ meant to be consumed and tweaked to fit the specific constraints of the hardware available.

2. The CRs are applied against an OpenShift cluster in _stages_.  That is, there is an ordering in which each grouping of CRs is fed to the cluster.  It is _not_ a case of simply taking all CRs from all stages and applying them all at once.

3. [kustomize](https://kustomize.io/) is used to genereate the control plane CRs dynamically. The `control-plane/networking/nncp/values.yaml`, `control-plane/service-values.yaml`, `control-plane2/networking/nncp/values.yaml` and `control-plane2/service-values.yaml` file(s) must be updated to fit your environment. kustomize version 5 or newer required.

4. [kustomize](https://kustomize.io/) is used to generate the dataplane CRs dynamically. The `edpm/nodeset/values.yaml` and `edpm2/nodeset/values.yaml` files must be updated to fit your environment. kustomize version 5 or newer required.

## Stages

All stages must be executed in the order listed below. Everything is required unless otherwise indicated.

1. [Install the OpenStack K8S operators and their dependencies](../../common/)
2. [Create the second namespace](namespace.md)
3. [Configuring networking and deploy the OpenStack control planes](control-plane.md)
4. [Deploy the data planes](dataplane.md)
